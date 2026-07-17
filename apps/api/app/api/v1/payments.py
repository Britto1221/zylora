from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import AuthenticatedUser, require_tenant_access, require_tenant_admin
from app.core.serialization import model_dict
from app.db.models.entities import Payment
from app.db.session import get_db
from app.modules.audit.service import record_audit
from app.modules.payments.service import create_checkout_order, mark_checkout_verified, public_packs

router = APIRouter(prefix="/payments", tags=["payments"])
settings = get_settings()


class OrderCreate(BaseModel):
    pack_id: str = Field(pattern=r"^(mini|standard|business|growth)$")


class CheckoutVerify(BaseModel):
    razorpay_order_id: str = Field(min_length=5, max_length=255)
    razorpay_payment_id: str = Field(min_length=5, max_length=255)
    razorpay_signature: str = Field(min_length=32, max_length=512)


@router.get("/packs")
def packs() -> dict:
    return {"items": public_packs()}


@router.get("/{tenant_id}")
def payment_history(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    return {
        "items": [
            model_dict(item)
            for item in db.scalars(
                select(Payment)
                .where(Payment.tenant_id == tenant_id)
                .order_by(Payment.created_at.desc())
            ).all()
        ]
    }


@router.post("/{tenant_id}/orders", status_code=status.HTTP_201_CREATED)
def new_order(
    tenant_id: UUID,
    payload: OrderCreate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_admin),
) -> dict:
    try:
        payment, order = create_checkout_order(
            db,
            tenant_id=tenant_id,
            pack_id=payload.pack_id,
            receipt=f"zylora-{tenant_id}-{uuid4().hex[:12]}",
        )
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="payment",
        entity_id=payment.id,
        action="payment.order_created",
        payload={"pack_id": payload.pack_id},
    )
    db.commit()
    return {
        "payment": model_dict(payment),
        "order": order,
        "key_id": settings.razorpay_key_id or "rzp_test_development",
    }


@router.post("/{tenant_id}/verify-checkout")
def verify_checkout(
    tenant_id: UUID,
    payload: CheckoutVerify,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_admin),
) -> dict:
    if not settings.razorpay_key_secret and not settings.is_production:
        payment = db.scalar(
            select(Payment).where(
                Payment.tenant_id == tenant_id,
                Payment.provider_order_id == payload.razorpay_order_id,
            )
        )
        if payment is None:
            raise HTTPException(status_code=404, detail="Unknown development order.")
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
        action="payment.checkout_verified",
    )
    db.commit()
    return {
        "verified": True,
        "status": payment.status,
        "message": "Credits are issued only after the captured-payment webhook.",
    }
