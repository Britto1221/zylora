from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.entities import Site, SiteVersion
from app.db.models.enums import SiteVersionStatus


def approve_version(
    db: Session,
    *,
    version: SiteVersion,
    approver_user_id: UUID,
) -> SiteVersion:
    if version.status not in {
        SiteVersionStatus.READY_FOR_REVIEW,
        SiteVersionStatus.CHANGES_REQUESTED,
    }:
        raise ValueError("Version is not ready for approval.")

    version.status = SiteVersionStatus.APPROVED
    version.approved_by = approver_user_id
    version.approved_at = datetime.utcnow()
    db.flush()
    return version


def publish_version(db: Session, *, version: SiteVersion) -> SiteVersion:
    if version.status is not SiteVersionStatus.APPROVED:
        raise ValueError("Only approved versions may be published.")

    site = db.scalar(select(Site).where(Site.id == version.site_id))
    if not site:
        raise ValueError("Site not found.")

    previous_version_id = site.published_version_id
    version.previous_version_id = previous_version_id
    version.status = SiteVersionStatus.PUBLISHED
    version.published_at = datetime.utcnow()
    site.published_version_id = version.id
    db.flush()
    return version
