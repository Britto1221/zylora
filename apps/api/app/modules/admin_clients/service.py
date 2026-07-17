from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models.entities import (
    Invoice,
    NotificationJob,
    Site,
    Tenant,
    TenantMembership,
    TenantNote,
)
from app.db.models.enums import BillingStatus, InvoiceStatus, InvoiceType, TenantStatus
from app.modules.audit.service import record_audit


def client_health(tenant: Tenant, site: Site | None, *, now: datetime | None = None) -> dict:
    now = now or datetime.utcnow()
    reasons: list[str] = []
    site_status = "live" if site and site.published_version_id else "draft"

    if tenant.billing_status == BillingStatus.RESTRICTED:
        reasons.append("Billing access is restricted")
    elif tenant.billing_status == BillingStatus.WARNED:
        reasons.append("Payment is overdue")

    if site_status != "live":
        reasons.append("Website is still in draft")

    if tenant.last_login_at is None:
        reasons.append("No client login has been recorded")
    elif tenant.last_login_at < now - timedelta(days=30):
        reasons.append("Client has not logged in for more than 30 days")

    if tenant.operational_status == TenantStatus.PAUSED:
        reasons.append(f"Client is paused: {tenant.paused_reason or 'No reason recorded'}")

    if tenant.billing_status == BillingStatus.RESTRICTED:
        label = "Restricted"
    elif reasons:
        label = "Needs attention"
    else:
        label = "Healthy"

    return {
        "label": label,
        "reasons": reasons or ["Billing current, website live, and client recently active"],
        "siteStatus": site_status,
    }


def set_pause_state(
    db: Session,
    *,
    tenant: Tenant,
    paused: bool,
    reason: str,
    actor_user_id: UUID,
) -> Tenant:
    normalized_reason = reason.strip()
    if not normalized_reason:
        raise ValueError("A reason note is required.")

    previous = tenant.operational_status
    target = TenantStatus.PAUSED if paused else TenantStatus.ACTIVE
    tenant.operational_status = target
    tenant.paused_reason = normalized_reason
    tenant.paused_at = datetime.utcnow() if paused else None
    tenant.paused_by_user_id = actor_user_id

    record_audit(
        db,
        actor_user_id=actor_user_id,
        tenant_id=tenant.id,
        entity_type="tenant",
        entity_id=tenant.id,
        action="tenant.paused" if paused else "tenant.unpaused",
        payload={
            "previous": previous.value,
            "current": target.value,
            "reason": normalized_reason,
        },
    )
    return tenant


def append_tenant_note(
    db: Session,
    *,
    tenant: Tenant,
    author_user_id: UUID,
    author_email: str,
    body: str,
) -> TenantNote:
    text = body.strip()
    if not text:
        raise ValueError("Note text is required.")
    if len(text) > 5000:
        raise ValueError("Note text must not exceed 5,000 characters.")

    note = TenantNote(
        tenant_id=tenant.id,
        author_user_id=author_user_id,
        author_email=author_email,
        body=text,
    )
    db.add(note)
    db.flush()
    record_audit(
        db,
        actor_user_id=author_user_id,
        tenant_id=tenant.id,
        entity_type="tenant_note",
        entity_id=note.id,
        action="tenant.note_added",
        payload={"length": len(text)},
    )
    return note


def record_client_login(db: Session, *, user_id: UUID, email: str) -> list[UUID]:
    memberships = db.scalars(
        select(TenantMembership).where(
            TenantMembership.is_active.is_(True),
            or_(TenantMembership.user_id == user_id, TenantMembership.email == email.lower()),
        )
    ).all()
    if not memberships:
        return []

    now = datetime.utcnow()
    tenant_ids: list[UUID] = []
    for membership in memberships:
        tenant = db.get(Tenant, membership.tenant_id)
        if tenant is None:
            continue
        tenant.last_login_at = now
        tenant_ids.append(tenant.id)
        record_audit(
            db,
            actor_user_id=user_id,
            tenant_id=tenant.id,
            entity_type="authentication",
            entity_id=tenant.id,
            action="auth.client_login_recorded",
            payload={"email": email.lower(), "timestamp": now.isoformat()},
        )
    return tenant_ids


def queue_manual_payment_reminder(
    db: Session,
    *,
    tenant: Tenant,
    actor_user_id: UUID,
) -> dict:
    invoice = db.scalar(
        select(Invoice)
        .where(
            Invoice.tenant_id == tenant.id,
            Invoice.invoice_type == InvoiceType.RECURRING,
            Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.OVERDUE]),
        )
        .order_by(Invoice.due_at.asc())
    )
    if invoice is None:
        return {"tenantId": str(tenant.id), "queued": 0, "reason": "no_unpaid_invoice"}

    request_id = str(uuid4())
    variables = {
        "client_name": tenant.name,
        "invoice_number": invoice.number,
        "amount": f"{invoice.total_minor / 100:.2f}",
        "currency": invoice.currency,
        "due_date": invoice.due_at.date().isoformat() if invoice.due_at else "",
    }
    jobs: list[NotificationJob] = []
    if tenant.whatsapp_number:
        jobs.append(
            NotificationJob(
                tenant_id=tenant.id,
                lead_id=None,
                recipient_type="BILLING_WHATSAPP",
                recipient=tenant.whatsapp_number,
                template_name="payment_overdue",
                template_variables=variables,
                charge_micro_usd=0,
                idempotency_key=f"billing:{invoice.id}:manual:{request_id}:whatsapp",
            )
        )
    if tenant.email:
        jobs.append(
            NotificationJob(
                tenant_id=tenant.id,
                lead_id=None,
                recipient_type="BILLING_EMAIL",
                recipient=tenant.email,
                template_name="payment_overdue",
                template_variables=variables,
                charge_micro_usd=0,
                idempotency_key=f"billing:{invoice.id}:manual:{request_id}:email",
            )
        )
    db.add_all(jobs)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor_user_id,
        tenant_id=tenant.id,
        entity_type="billing_reminder",
        entity_id=invoice.id,
        action="billing.payment_reminder_manual",
        payload={
            "invoice_id": str(invoice.id),
            "invoice_number": invoice.number,
            "notification_job_ids": [str(job.id) for job in jobs],
        },
    )
    return {
        "tenantId": str(tenant.id),
        "queued": len(jobs),
        "reason": None if jobs else "no_contact_channel",
    }
