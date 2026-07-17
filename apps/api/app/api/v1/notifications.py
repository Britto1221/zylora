from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_tenant_access, require_tenant_admin
from app.core.serialization import model_dict
from app.db.models.entities import NotificationJob
from app.db.models.enums import NotificationStatus
from app.db.session import get_db
from app.modules.audit.service import record_audit
from app.modules.notifications.service import get_or_create_settings

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationSettingsUpdate(BaseModel):
    business_enabled: bool | None = None
    visitor_enabled: bool | None = None
    business_template: str | None = Field(default=None, max_length=120)
    visitor_template: str | None = Field(default=None, max_length=120)
    business_charge_micro_usd: int | None = Field(default=None, ge=0)
    visitor_charge_micro_usd: int | None = Field(default=None, ge=0)


@router.get("/{tenant_id}")
def overview(
    tenant_id: UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    setting = get_or_create_settings(db, tenant_id)
    total = (
        db.scalar(
            select(func.count(NotificationJob.id)).where(NotificationJob.tenant_id == tenant_id)
        )
        or 0
    )
    jobs = db.scalars(
        select(NotificationJob)
        .where(NotificationJob.tenant_id == tenant_id)
        .order_by(NotificationJob.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    db.commit()
    return {
        "settings": model_dict(setting),
        "jobs": [model_dict(job) for job in jobs],
        "total": total,
        "page": page,
        "pageSize": page_size,
    }


@router.patch("/{tenant_id}/settings")
def update_settings(
    tenant_id: UUID,
    payload: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_admin),
) -> dict:
    setting = get_or_create_settings(db, tenant_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(setting, key, value)
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="notification_setting",
        entity_id=setting.id,
        action="notifications.settings_updated",
        payload=payload.model_dump(exclude_unset=True),
    )
    db.commit()
    return model_dict(setting)


@router.post("/{tenant_id}/jobs/{job_id}/retry")
def retry_job(
    tenant_id: UUID,
    job_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_admin),
) -> dict:
    job = db.scalar(
        select(NotificationJob).where(
            NotificationJob.id == job_id, NotificationJob.tenant_id == tenant_id
        )
    )
    if not job:
        raise HTTPException(status_code=404, detail="Notification job not found.")
    if job.status not in {
        NotificationStatus.FAILED,
        NotificationStatus.SKIPPED_INSUFFICIENT_CREDITS,
    }:
        raise HTTPException(status_code=409, detail="This job cannot be retried.")
    job.status = NotificationStatus.PENDING
    job.failure_reason = None
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="notification_job",
        entity_id=job.id,
        action="notifications.retry_requested",
    )
    db.commit()
    return model_dict(job)
