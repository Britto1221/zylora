from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID, NAMESPACE_DNS, uuid5

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_worker_token
from app.core.serialization import model_dict
from app.db.models.entities import (
    CreditAccount,
    CreditReservation,
    Domain,
    NotificationJob,
    SeoAudit,
    Site,
    SiteVersion,
    Tenant,
)
from app.db.models.enums import (
    DomainStatus,
    NotificationStatus,
    SeoAuditStatus,
)
from app.db.session import get_db
from app.modules.audit.service import record_audit
from app.modules.credits.service import (
    InsufficientCreditsError,
    capture_reservation,
    release_reservation,
    reserve_credits,
)
from app.modules.email.service import send_email
from app.modules.whatsapp.service import send_template
from zylora_ai.seo import audit_snapshot

router = APIRouter(
    prefix="/internal",
    tags=["internal"],
    dependencies=[Depends(require_worker_token)],
)
worker_id = uuid5(NAMESPACE_DNS, "zylora-worker")


@router.get("/notification-jobs")
def pending_jobs(limit: int = 25, db: Session = Depends(get_db)) -> dict:
    jobs = db.scalars(
        select(NotificationJob)
        .where(NotificationJob.status == NotificationStatus.PENDING)
        .order_by(NotificationJob.created_at)
        .limit(min(max(limit, 1), 100))
        .with_for_update(skip_locked=True)
    ).all()
    return {"items": [model_dict(item) for item in jobs]}


@router.post("/notification-jobs/{job_id}/process")
def process_job(job_id: UUID, db: Session = Depends(get_db)) -> dict:
    job = db.get(NotificationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Notification job not found.")
    if job.status in {NotificationStatus.DELIVERED, NotificationStatus.READ}:
        return model_dict(job)
    if job.status not in {
        NotificationStatus.PENDING,
        NotificationStatus.CREDIT_RESERVED,
        NotificationStatus.FAILED,
    }:
        return model_dict(job)

    job.attempts += 1
    reservation = None
    try:
        reservation = reserve_credits(
            db,
            tenant_id=job.tenant_id,
            amount_micro_usd=job.charge_micro_usd,
            idempotency_key=f"notification:{job.id}",
            reference_type="notification_job",
            reference_id=job.id,
        )
        job.status = NotificationStatus.CREDIT_RESERVED
        result = send_template(
            recipient=job.recipient,
            template_name=job.template_name,
            language=job.template_language,
            variables=job.template_variables,
            idempotency_key=job.idempotency_key,
        )
        job.provider_message_id = result["id"]
        job.status = NotificationStatus.SUBMITTED
        capture_reservation(
            db,
            reservation=reservation,
            description=f"WhatsApp {job.recipient_type.lower()} notification",
            external_reference=result["id"],
        )
        db.commit()
    except InsufficientCreditsError:
        if reservation:
            release_reservation(db, reservation, reason="insufficient")
        job.status = NotificationStatus.SKIPPED_INSUFFICIENT_CREDITS
        job.failure_reason = "Insufficient credits."
        db.commit()
    except Exception as exc:
        if reservation:
            release_reservation(db, reservation, reason="send_failed")
        job.status = NotificationStatus.FAILED
        job.failure_reason = str(exc)[:2000]
        db.commit()
    return model_dict(job)


@router.post("/domain-reminders/run")
def run_domain_reminders(db: Session = Depends(get_db)) -> dict:
    now = datetime.utcnow()
    sent: list[dict] = []
    domains = db.scalars(
        select(Domain).where(
            Domain.expires_at.is_not(None),
            Domain.status.in_([DomainStatus.ACTIVE, DomainStatus.EXPIRING]),
        )
    ).all()
    for domain in domains:
        days = (domain.expires_at.date() - now.date()).days
        threshold = next((value for value in [60, 30, 15, 7] if days <= value and (domain.last_reminder_days is None or domain.last_reminder_days > value)), None)
        if threshold is None:
            continue
        tenant = db.get(Tenant, domain.tenant_id)
        if not tenant or not tenant.email:
            continue
        result = send_email(
            to=tenant.email,
            subject=f"Domain renewal reminder: {domain.hostname}",
            text=(
                f"{domain.hostname} expires in approximately {days} days. "
                "Renewal payment is separate from WhatsApp credits. "
                "After the final 7-day reminder, non-renewal remains the client's responsibility."
            ),
            idempotency_key=f"domain:{domain.id}:{threshold}",
        )
        domain.last_reminder_days = threshold
        domain.status = DomainStatus.EXPIRING if days <= 60 else domain.status
        record_audit(
            db,
            actor_user_id=worker_id,
            tenant_id=domain.tenant_id,
            entity_type="domain",
            entity_id=domain.id,
            action="domain.renewal_reminder_sent",
            payload={"days": threshold, "provider_id": result.get("id")},
        )
        sent.append({"domain": domain.hostname, "days": threshold})
    db.commit()
    return {"sent": sent, "count": len(sent)}


@router.post("/credit-reservations/cleanup")
def cleanup_reservations(db: Session = Depends(get_db)) -> dict:
    expired = db.scalars(
        select(CreditReservation)
        .where(
            CreditReservation.status == "ACTIVE",
            CreditReservation.expires_at.is_not(None),
            CreditReservation.expires_at < datetime.utcnow(),
        )
        .with_for_update(skip_locked=True)
    ).all()
    for reservation in expired:
        release_reservation(db, reservation, reason="expired")
    db.commit()
    return {"released": len(expired)}


@router.post("/seo/{tenant_id}/run")
def internal_seo_audit(tenant_id: UUID, db: Session = Depends(get_db)) -> dict:
    site = db.scalar(select(Site).where(Site.tenant_id == tenant_id))
    if not site:
        raise HTTPException(status_code=404, detail="Website not found.")
    version_id = site.draft_version_id or site.published_version_id
    version = db.get(SiteVersion, version_id) if version_id else None
    if not version:
        raise HTTPException(status_code=404, detail="No website version.")
    audit = SeoAudit(
        tenant_id=tenant_id,
        site_id=site.id,
        version_id=version.id,
        status=SeoAuditStatus.RUNNING,
    )
    db.add(audit)
    db.flush()
    result = audit_snapshot(version.content_snapshot, version.seo_snapshot)
    audit.status = SeoAuditStatus.COMPLETED
    audit.score = result["score"]
    audit.grade = result["grade"]
    audit.summary = result["summary"]
    audit.issues_json = result["issues"]
    audit.recommendations_json = result["recommendations"]
    db.commit()
    return model_dict(audit)
