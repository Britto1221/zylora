from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_super_admin
from app.core.serialization import model_dict
from app.db.models.entities import Site, SiteVersion
from app.db.models.enums import SiteVersionStatus
from app.db.session import get_db
from app.modules.audit.service import record_audit
from app.modules.sites.validation import validate_snapshot

router = APIRouter(prefix="/publishing", tags=["publishing"])


def load_version(db: Session, version_id: UUID) -> SiteVersion:
    version = db.get(SiteVersion, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found.")
    return version


@router.post("/{version_id}/submit")
def submit(
    version_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    version = load_version(db, version_id)
    if version.status != SiteVersionStatus.DRAFT:
        raise HTTPException(status_code=409, detail="Only drafts can be submitted.")
    validation = validate_snapshot(
        version.content_snapshot, version.theme_snapshot, version.seo_snapshot
    )
    version.validation_snapshot = validation
    if not validation["valid"]:
        raise HTTPException(status_code=422, detail={"message": "Validation failed.", **validation})
    version.status = SiteVersionStatus.READY_FOR_REVIEW
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=version.tenant_id,
        entity_type="site_version",
        entity_id=version.id,
        action="publishing.submitted",
        payload=validation,
    )
    db.commit()
    return model_dict(version)


@router.post("/{version_id}/request-changes")
def request_changes(
    version_id: UUID,
    reason: str,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    version = load_version(db, version_id)
    version.status = SiteVersionStatus.CHANGES_REQUESTED
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=version.tenant_id,
        entity_type="site_version",
        entity_id=version.id,
        action="publishing.changes_requested",
        payload={"reason": reason},
    )
    db.commit()
    return model_dict(version)


@router.post("/{version_id}/approve")
def approve(
    version_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    version = load_version(db, version_id)
    if version.status not in {
        SiteVersionStatus.READY_FOR_REVIEW,
        SiteVersionStatus.CHANGES_REQUESTED,
    }:
        raise HTTPException(status_code=409, detail="Version is not ready for approval.")
    validation = validate_snapshot(
        version.content_snapshot, version.theme_snapshot, version.seo_snapshot
    )
    if not validation["valid"]:
        raise HTTPException(status_code=422, detail={"message": "Validation failed.", **validation})
    version.status = SiteVersionStatus.APPROVED
    version.approved_by = user.id
    version.approved_at = datetime.utcnow()
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=version.tenant_id,
        entity_type="site_version",
        entity_id=version.id,
        action="publishing.approved",
    )
    db.commit()
    return model_dict(version)


@router.post("/{version_id}/publish")
def publish(
    version_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    version = load_version(db, version_id)
    if version.status != SiteVersionStatus.APPROVED:
        raise HTTPException(status_code=409, detail="Only approved versions may be published.")
    site = db.get(Site, version.site_id)
    if site is None:
        raise HTTPException(status_code=404, detail="Site not found.")
    previous_id = site.published_version_id
    if previous_id:
        previous = db.get(SiteVersion, previous_id)
        if previous and previous.id != version.id:
            previous.status = SiteVersionStatus.ARCHIVED
    version.previous_version_id = previous_id
    version.status = SiteVersionStatus.PUBLISHED
    version.published_at = datetime.utcnow()
    site.published_version_id = version.id
    if site.draft_version_id == version.id:
        site.draft_version_id = None
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=version.tenant_id,
        entity_type="site_version",
        entity_id=version.id,
        action="publishing.published",
        payload={"previous_version_id": str(previous_id) if previous_id else None},
    )
    db.commit()
    return model_dict(version)


@router.post("/{version_id}/rollback")
def rollback(
    version_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    source = load_version(db, version_id)
    site = db.get(Site, source.site_id)
    if site is None:
        raise HTTPException(status_code=404, detail="Site not found.")
    next_number = (
        db.scalar(
            select(func.max(SiteVersion.version_number)).where(SiteVersion.site_id == site.id)
        )
        or 0
    ) + 1
    restored = SiteVersion(
        tenant_id=source.tenant_id,
        site_id=source.site_id,
        version_number=next_number,
        status=SiteVersionStatus.APPROVED,
        content_snapshot=deepcopy(source.content_snapshot),
        theme_snapshot=deepcopy(source.theme_snapshot),
        seo_snapshot=deepcopy(source.seo_snapshot),
        validation_snapshot=deepcopy(source.validation_snapshot),
        created_by=user.id,
        approved_by=user.id,
        approved_at=datetime.utcnow(),
        previous_version_id=site.published_version_id,
    )
    db.add(restored)
    db.flush()
    current = db.get(SiteVersion, site.published_version_id) if site.published_version_id else None
    if current:
        current.status = SiteVersionStatus.ARCHIVED
    restored.status = SiteVersionStatus.PUBLISHED
    restored.published_at = datetime.utcnow()
    site.published_version_id = restored.id
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=restored.tenant_id,
        entity_type="site_version",
        entity_id=restored.id,
        action="publishing.rolled_back",
        payload={"source_version_id": str(source.id)},
    )
    db.commit()
    return model_dict(restored)
