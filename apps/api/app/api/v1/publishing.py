from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_super_admin
from app.db.models.entities import SiteVersion
from app.db.session import get_db
from app.modules.publishing.service import approve_version, publish_version

router = APIRouter(prefix="/publishing", tags=["publishing"])


@router.post("/{version_id}/approve")
def approve(
    version_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    version = db.scalar(select(SiteVersion).where(SiteVersion.id == version_id))
    if not version:
        raise HTTPException(status_code=404, detail="Version not found.")

    try:
        approve_version(db, version=version, approver_user_id=user.id)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {"id": str(version.id), "status": version.status}


@router.post("/{version_id}/publish")
def publish(
    version_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    version = db.scalar(select(SiteVersion).where(SiteVersion.id == version_id))
    if not version:
        raise HTTPException(status_code=404, detail="Version not found.")

    try:
        publish_version(db, version=version)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {"id": str(version.id), "status": version.status}
