from __future__ import annotations

from datetime import datetime
from uuid import NAMESPACE_DNS, UUID, uuid5

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    AuthenticatedUser,
    require_super_admin,
    require_tenant_membership,
)
from app.core.serialization import model_dict
from app.db.models.entities import Payment, Tenant
from app.db.models.enums import BillingStatus
from app.db.session import get_db
from app.modules.admin_clients.service import queue_manual_payment_reminder
from app.modules.audit.service import record_audit
from app.modules.billing.service import (
    clear_billing_restriction,
    days_past_due,
    evaluate_tenant_dunning,
    oldest_unpaid_recurring_invoice,
)
from app.modules.payments.service import (
    create_invoice_checkout_order,
    mark_checkout_verified,
)

router = APIRouter(prefix="/billing", tags=["billing"])
settings = get_settings()
worker_id = uuid5(NAMESPACE_DNS, "zylora-worker")


class BillingConfigurationUpdate(BaseModel):
    monthly_amount_minor: int = Field(ge=0, le=1_000_000_000)
    billing_currency: str = Field(pattern=r"^(USD|INR)$")
    billing_day: int = Field(ge=1, le=31)

    @field_validator("billing_currency")
    @classmethod
    def uppercase_currency(cls, value: str) -> str:
        return value.upper()


class BillingCheckoutVerify(BaseModel):
    razorpay_order_id: str = Field(min_length=5, max_length=255)
    razorpay_payment_id: str = Field(min_length=5, max_length=255)
    razorpay_signature: str = Field(min_length=8, max_length=512)


def billing_payload(db: Session, tenant: Tenant) -> dict:
    invoice = oldest_unpaid_recurring_invoice(db, tenant.id)
    overdue = (
        days_past_due(invoice)
        if invoice and invoice.due_at and invoice.due_at < datetime.utcnow()
        else 0
    )
    return {
        "tenantId": str(tenant.id),
        "monthlyAmountMinor": tenant.monthly_amount_minor,
        "billingCurrency": tenant.billing_currency,
        "billingDay": tenant.billing_day,
        "billingStatus": tenant.billing_status.value,
        "daysPastDue": overdue,
        "showOverdueBanner": tenant.billing_status == BillingStatus.WARNED,
        "restricted": tenant.billing_status == BillingStatus.RESTRICTED,
        "invoice": model_dict(invoice) if invoice else None,
    }


@router.get("/{tenant_id}/configuration")
def get_billing_configuration(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Client not found.")
    return billing_payload(db, tenant)


@router.put("/{tenant_id}/configuration")
def update_billing_configuration(
    tenant_id: UUID,
    payload: BillingConfigurationUpdate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Client not found.")
    previous = {
        "monthly_amount_minor": tenant.monthly_amount_minor,
        "billing_currency": tenant.billing_currency,
        "billing_day": tenant.billing_day,
    }
    tenant.monthly_amount_minor = payload.monthly_amount_minor
    tenant.billing_currency = payload.billing_currency
    tenant.billing_day = payload.billing_day
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant.id,
        entity_type="tenant_billing",
        entity_id=tenant.id,
        action="billing.configuration_updated",
        payload={"previous": previous, "current": payload.model_dump()},
    )
    db.commit()
    return billing_payload(db, tenant)


@router.get("/{tenant_id}/status")
def get_billing_status(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_membership),
) -> dict:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Client not found.")
    # Re-evaluate on read so the API cannot rely solely on the scheduler.
    evaluate_tenant_dunning(db, tenant=tenant, actor_user_id=worker_id)
    db.commit()
    return billing_payload(db, tenant)


@router.post("/{tenant_id}/clear-lockout")
def manual_clear_lockout(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Client not found.")
    invoice = oldest_unpaid_recurring_invoice(db, tenant.id)
    clear_billing_restriction(
        db,
        tenant=tenant,
        actor_user_id=user.id,
        reason="super_admin_manual_override",
        action="billing.lockout_manual_override",
        override_invoice_id=invoice.id if invoice else None,
    )
    db.commit()
    return billing_payload(db, tenant)


@router.post("/{tenant_id}/send-reminder")
def send_payment_reminder(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Client not found.")
    result = queue_manual_payment_reminder(
        db, tenant=tenant, actor_user_id=user.id
    )
    db.commit()
    return result


@router.post("/{tenant_id}/pay-order", status_code=status.HTTP_201_CREATED)
def create_pay_now_order(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_membership),
) -> dict:
    invoice = oldest_unpaid_recurring_invoice(db, tenant_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="No unpaid recurring invoice.")
    try:
        payment, order = create_invoice_checkout_order(
            db,
            tenant_id=tenant_id,
            invoice_id=invoice.id,
            receipt=f"recurring-{invoice.number}",
        )
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="payment",
        entity_id=payment.id,
        action="billing.payment_order_created",
        payload={"invoice_id": str(invoice.id), "invoice_number": invoice.number},
    )
    db.commit()
    return {
        "payment": model_dict(payment),
        "invoice": model_dict(invoice),
        "order": order,
        "key_id": settings.razorpay_key_id or "rzp_test_development",
    }


@router.post("/{tenant_id}/verify-checkout")
def verify_pay_now_checkout(
    tenant_id: UUID,
    payload: BillingCheckoutVerify,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_membership),
) -> dict:
    payment = db.scalar(
        select(Payment).where(
            Payment.tenant_id == tenant_id,
            Payment.provider_order_id == payload.razorpay_order_id,
            Payment.purpose == "recurring_invoice",
        )
    )
    if payment is None:
        raise HTTPException(status_code=404, detail="Unknown recurring invoice order.")
    if not settings.razorpay_key_secret and not settings.is_production:
        payment.provider_payment_id = payload.razorpay_payment_id
        payment.status = "CHECKOUT_VERIFIED"
    else:
        try:
            payment = mark_checkout_verified(
                db,
                tenant_id=tenant_id,
                provider_order_id=payload.razorpay_order_id,
                provider_payment_id=payload.razorpay_payment_id,
                signature=payload.razorpay_signature,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="payment",
        entity_id=payment.id,
        action="billing.checkout_verified",
        payload={"invoice_id": str(payment.invoice_id) if payment.invoice_id else None},
    )
    db.commit()
    return {"verified": True, "status": payment.status}
