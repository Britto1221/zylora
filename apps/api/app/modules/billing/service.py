from __future__ import annotations

import calendar
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.entities import Invoice, NotificationJob, Tenant
from app.db.models.enums import BillingStatus, InvoiceStatus, InvoiceType, TenantStatus
from app.modules.audit.service import record_audit


def billing_due_at(year: int, month: int, billing_day: int) -> datetime:
    last_day = calendar.monthrange(year, month)[1]
    day = min(max(billing_day, 1), last_day)
    return datetime(year, month, day, 23, 59, 59)


def recurring_invoice_number(tenant: Tenant, period: str) -> str:
    compact = period.replace("-", "")
    return f"ZY-R-{compact}-{str(tenant.id).split('-')[0].upper()}"


def generate_recurring_invoice(
    db: Session,
    *,
    tenant: Tenant,
    year: int,
    month: int,
    actor_user_id: UUID,
) -> Invoice | None:
    if tenant.operational_status == TenantStatus.PAUSED:
        return None
    if tenant.monthly_amount_minor <= 0:
        return None
    period = f"{year:04d}-{month:02d}"
    existing = db.scalar(
        select(Invoice).where(
            Invoice.tenant_id == tenant.id,
            Invoice.invoice_type == InvoiceType.RECURRING,
            Invoice.billing_period == period,
        )
    )
    if existing:
        return existing

    due_at = billing_due_at(year, month, tenant.billing_day)
    invoice = Invoice(
        tenant_id=tenant.id,
        number=recurring_invoice_number(tenant, period),
        status=InvoiceStatus.ISSUED,
        invoice_type=InvoiceType.RECURRING,
        billing_period=period,
        auto_generated=True,
        currency=tenant.billing_currency,
        subtotal_minor=tenant.monthly_amount_minor,
        tax_minor=0,
        total_minor=tenant.monthly_amount_minor,
        due_at=due_at,
        line_items=[
            {
                "description": f"Zylora managed platform service — {period}",
                "quantity": 1,
                "unitMinor": tenant.monthly_amount_minor,
                "kind": "recurring_monthly_service",
            }
        ],
    )
    db.add(invoice)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor_user_id,
        tenant_id=tenant.id,
        entity_type="invoice",
        entity_id=invoice.id,
        action="invoice.recurring_generated",
        payload={
            "billing_period": period,
            "currency": tenant.billing_currency,
            "amount_minor": tenant.monthly_amount_minor,
            "due_at": due_at.isoformat(),
        },
    )
    return invoice


def generate_monthly_invoices(
    db: Session,
    *,
    actor_user_id: UUID,
    reference: datetime | None = None,
) -> list[Invoice]:
    reference = reference or datetime.utcnow()
    tenants = db.scalars(
        select(Tenant).where(
            Tenant.is_active.is_(True),
            Tenant.operational_status == TenantStatus.ACTIVE,
            Tenant.monthly_amount_minor > 0,
        )
    ).all()
    generated: list[Invoice] = []
    for tenant in tenants:
        invoice = generate_recurring_invoice(
            db,
            tenant=tenant,
            year=reference.year,
            month=reference.month,
            actor_user_id=actor_user_id,
        )
        if invoice is not None:
            generated.append(invoice)
    return generated


def oldest_unpaid_recurring_invoice(db: Session, tenant_id: UUID) -> Invoice | None:
    return db.scalar(
        select(Invoice)
        .where(
            Invoice.tenant_id == tenant_id,
            Invoice.invoice_type == InvoiceType.RECURRING,
            Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.OVERDUE]),
            Invoice.due_at.is_not(None),
        )
        .order_by(Invoice.due_at.asc())
    )


def days_past_due(invoice: Invoice, now: datetime | None = None) -> int:
    now = now or datetime.utcnow()
    if invoice.due_at is None:
        return 0
    return max((now.date() - invoice.due_at.date()).days, 0)


def _set_billing_status(
    db: Session,
    *,
    tenant: Tenant,
    status: BillingStatus,
    actor_user_id: UUID,
    reason: str,
    invoice: Invoice | None,
) -> bool:
    if tenant.billing_status == status:
        return False
    previous = tenant.billing_status
    tenant.billing_status = status
    record_audit(
        db,
        actor_user_id=actor_user_id,
        tenant_id=tenant.id,
        entity_type="tenant_billing",
        entity_id=tenant.id,
        action="billing.status_changed",
        payload={
            "previous": previous.value if hasattr(previous, "value") else str(previous),
            "current": status.value,
            "reason": reason,
            "invoice_id": str(invoice.id) if invoice else None,
        },
    )
    return True


def clear_billing_restriction(
    db: Session,
    *,
    tenant: Tenant,
    actor_user_id: UUID,
    reason: str,
    action: str = "billing.lockout_cleared",
    override_invoice_id: UUID | None = None,
) -> None:
    previous = tenant.billing_status
    tenant.billing_status = BillingStatus.CURRENT
    metadata = dict(tenant.metadata_json or {})
    if override_invoice_id is not None:
        metadata["billing_lockout_override_invoice_id"] = str(override_invoice_id)
    else:
        metadata.pop("billing_lockout_override_invoice_id", None)
    tenant.metadata_json = metadata
    record_audit(
        db,
        actor_user_id=actor_user_id,
        tenant_id=tenant.id,
        entity_type="tenant_billing",
        entity_id=tenant.id,
        action=action,
        payload={
            "previous": previous.value if hasattr(previous, "value") else str(previous),
            "current": BillingStatus.CURRENT.value,
            "reason": reason,
            "override_invoice_id": str(override_invoice_id) if override_invoice_id else None,
        },
    )


def _notification_exists(db: Session, idempotency_key: str) -> bool:
    return bool(
        db.scalar(
            select(NotificationJob.id).where(NotificationJob.idempotency_key == idempotency_key)
        )
    )


def create_dunning_reminders(
    db: Session,
    *,
    tenant: Tenant,
    invoice: Invoice,
    overdue_days: int,
) -> list[NotificationJob]:
    jobs: list[NotificationJob] = []
    for reminder_day in (3, 8):
        if overdue_days < reminder_day:
            continue
        variables = {
            "client_name": tenant.name,
            "invoice_number": invoice.number,
            "amount": f"{invoice.total_minor / 100:.2f}",
            "currency": invoice.currency,
            "days_overdue": str(overdue_days),
            "due_date": invoice.due_at.date().isoformat() if invoice.due_at else "",
        }
        if tenant.whatsapp_number:
            key = f"billing:{invoice.id}:day-{reminder_day}:whatsapp"
            if not _notification_exists(db, key):
                jobs.append(
                    NotificationJob(
                        tenant_id=tenant.id,
                        lead_id=None,
                        recipient_type="BILLING_WHATSAPP",
                        recipient=tenant.whatsapp_number,
                        template_name="payment_overdue",
                        template_variables=variables,
                        charge_micro_usd=0,
                        idempotency_key=key,
                    )
                )
        if tenant.email:
            key = f"billing:{invoice.id}:day-{reminder_day}:email"
            if not _notification_exists(db, key):
                jobs.append(
                    NotificationJob(
                        tenant_id=tenant.id,
                        lead_id=None,
                        recipient_type="BILLING_EMAIL",
                        recipient=tenant.email,
                        template_name="payment_overdue",
                        template_variables=variables,
                        charge_micro_usd=0,
                        idempotency_key=key,
                    )
                )
    if jobs:
        db.add_all(jobs)
        db.flush()
    return jobs


def evaluate_tenant_dunning(
    db: Session,
    *,
    tenant: Tenant,
    actor_user_id: UUID,
    now: datetime | None = None,
) -> dict:
    now = now or datetime.utcnow()
    invoice = oldest_unpaid_recurring_invoice(db, tenant.id)
    if invoice is None or invoice.due_at is None or invoice.due_at >= now:
        _set_billing_status(
            db,
            tenant=tenant,
            status=BillingStatus.CURRENT,
            actor_user_id=actor_user_id,
            reason="no_overdue_recurring_invoice",
            invoice=None,
        )
        return {"status": tenant.billing_status.value, "daysPastDue": 0, "invoice": None}

    override_invoice_id = str(
        (tenant.metadata_json or {}).get("billing_lockout_override_invoice_id", "")
    )
    if override_invoice_id == str(invoice.id):
        _set_billing_status(
            db,
            tenant=tenant,
            status=BillingStatus.CURRENT,
            actor_user_id=actor_user_id,
            reason="manual_override_for_current_overdue_invoice",
            invoice=invoice,
        )
        return {
            "status": tenant.billing_status.value,
            "daysPastDue": days_past_due(invoice, now),
            "invoice": invoice,
            "manualOverride": True,
        }

    overdue_days = days_past_due(invoice, now)
    invoice.status = InvoiceStatus.OVERDUE
    target = BillingStatus.CURRENT
    if overdue_days >= 10:
        target = BillingStatus.RESTRICTED
    elif overdue_days >= 3:
        target = BillingStatus.WARNED
    _set_billing_status(
        db,
        tenant=tenant,
        status=target,
        actor_user_id=actor_user_id,
        reason=f"recurring_invoice_{overdue_days}_days_past_due",
        invoice=invoice,
    )
    jobs = create_dunning_reminders(
        db,
        tenant=tenant,
        invoice=invoice,
        overdue_days=overdue_days,
    )
    if jobs:
        record_audit(
            db,
            actor_user_id=actor_user_id,
            tenant_id=tenant.id,
            entity_type="billing_reminder",
            entity_id=invoice.id,
            action="billing.reminders_queued",
            payload={
                "invoice_id": str(invoice.id),
                "invoice_number": invoice.number,
                "days_past_due": overdue_days,
                "notification_job_ids": [str(job.id) for job in jobs],
            },
        )
    return {
        "status": tenant.billing_status.value,
        "daysPastDue": overdue_days,
        "invoice": invoice,
        "remindersCreated": len(jobs),
    }


def evaluate_all_dunning(
    db: Session,
    *,
    actor_user_id: UUID,
    now: datetime | None = None,
) -> list[dict]:
    tenants = db.scalars(select(Tenant).where(Tenant.is_active.is_(True))).all()
    return [
        {
            "tenantId": str(tenant.id),
            **evaluate_tenant_dunning(
                db,
                tenant=tenant,
                actor_user_id=actor_user_id,
                now=now,
            ),
        }
        for tenant in tenants
    ]
