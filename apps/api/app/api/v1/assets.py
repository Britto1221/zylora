from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import AuthenticatedUser, require_tenant_access, require_tenant_admin
from app.core.serialization import model_dict
from app.db.models.entities import Asset
from app.db.session import get_db
from app.modules.audit.service import record_audit
from app.modules.storage.service import (
    MalwareDetectedError,
    UploadValidationError,
    delete_local,
    guardduty_scan_result,
    inspect_s3_object,
    local_path,
    presigned_download,
    presigned_upload,
    save_local,
    scan_uploaded_bytes,
    storage_key,
    validate_content,
    validate_upload,
)

router = APIRouter(prefix="/assets", tags=["assets"])
settings = get_settings()


class PresignRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(min_length=1, max_length=120)
    size_bytes: int = Field(gt=0)
    category: str = Field(default="general", max_length=80)
    alt_text: str | None = Field(default=None, max_length=500)


class CompleteRequest(BaseModel):
    checksum_sha256: str | None = Field(default=None, min_length=64, max_length=64)


def ready(asset: Asset) -> bool:
    return asset.status == "READY" and asset.scan_status == "CLEAN"


@router.get("/public/{asset_id}")
def public_asset(asset_id: UUID, db: Session = Depends(get_db)):
    from fastapi.responses import FileResponse, RedirectResponse

    asset = db.get(Asset, asset_id)
    if not asset or not ready(asset):
        raise HTTPException(status_code=404, detail="Asset not found.")
    url = presigned_download(key=asset.storage_key)
    if url:
        return RedirectResponse(url)
    path = local_path(asset.storage_key)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Stored file is unavailable.")
    return FileResponse(
        path, media_type=asset.mime_type, headers={"Cache-Control": "public, max-age=86400"}
    )


@router.get("/{tenant_id}")
def list_assets(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    return {
        "items": [
            model_dict(item)
            for item in db.scalars(
                select(Asset).where(Asset.tenant_id == tenant_id).order_by(Asset.created_at.desc())
            ).all()
        ]
    }


@router.post("/{tenant_id}/presign")
def create_presigned_upload(
    tenant_id: UUID,
    payload: PresignRequest,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_admin),
) -> dict:
    try:
        name = validate_upload(
            filename=payload.filename, mime_type=payload.mime_type, size_bytes=payload.size_bytes
        )
    except UploadValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    key = storage_key(tenant_id, name)
    asset = Asset(
        tenant_id=tenant_id,
        filename=name,
        storage_key=key,
        mime_type=payload.mime_type,
        size_bytes=payload.size_bytes,
        category=payload.category,
        alt_text=payload.alt_text,
        status="PENDING",
        scan_status="PENDING",
    )
    db.add(asset)
    db.flush()
    upload = presigned_upload(key=key, mime_type=payload.mime_type, size_bytes=payload.size_bytes)
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="asset",
        entity_id=asset.id,
        action="asset.upload_requested",
    )
    db.commit()
    return {
        "asset": model_dict(asset),
        "upload": upload
        or {
            "url": f"/api/backend/assets/{tenant_id}/{asset.id}/local-upload",
            "method": "POST",
            "localDevelopment": True,
        },
    }


@router.post("/{tenant_id}/{asset_id}/local-upload")
async def local_upload(
    tenant_id: UUID,
    asset_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_admin),
) -> dict:
    if settings.is_production:
        raise HTTPException(status_code=404, detail="Not found.")
    asset = db.scalar(select(Asset).where(Asset.id == asset_id, Asset.tenant_id == tenant_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found.")
    data = await file.read(settings.max_upload_bytes + 1)
    if len(data) != asset.size_bytes:
        raise HTTPException(status_code=422, detail="Uploaded file size does not match.")
    try:
        detected = validate_content(data=data, declared_mime_type=asset.mime_type)
        scan = scan_uploaded_bytes(data)
    except MalwareDetectedError as exc:
        asset.status = "QUARANTINED"
        asset.scan_status = "INFECTED"
        db.commit()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except (UploadValidationError, RuntimeError) as exc:
        asset.status = "REJECTED"
        asset.scan_status = "FAILED"
        db.commit()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    _, checksum = save_local(asset.storage_key, data)
    asset.detected_mime_type = detected
    asset.checksum_sha256 = checksum
    asset.scan_provider = scan["provider"]
    asset.scan_status = scan["status"]
    asset.scan_details = scan
    asset.scanned_at = datetime.utcnow()
    asset.status = "READY" if scan["status"] == "CLEAN" else "SCANNING"
    asset.public_url = f"/api/v1/assets/public/{asset.id}" if asset.status == "READY" else None
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="asset",
        entity_id=asset.id,
        action="asset.uploaded",
    )
    db.commit()
    return model_dict(asset)


@router.post("/{tenant_id}/{asset_id}/complete")
def complete_upload(
    tenant_id: UUID,
    asset_id: UUID,
    payload: CompleteRequest,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_admin),
) -> dict:
    asset = db.scalar(select(Asset).where(Asset.id == asset_id, Asset.tenant_id == tenant_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found.")
    try:
        info = inspect_s3_object(key=asset.storage_key)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if info["size_bytes"] != asset.size_bytes or info["mime_type"] != asset.mime_type:
        asset.status = "REJECTED"
        db.commit()
        raise HTTPException(
            status_code=422, detail="Uploaded object metadata does not match the request."
        )
    scan_status = guardduty_scan_result(info["scan_status"])
    asset.checksum_sha256 = payload.checksum_sha256 or info["etag"]
    asset.detected_mime_type = info["mime_type"]
    asset.scan_provider = "guardduty"
    asset.scan_status = scan_status
    asset.scanned_at = datetime.utcnow()
    asset.status = (
        "READY"
        if scan_status == "CLEAN"
        else ("QUARANTINED" if scan_status == "INFECTED" else "SCANNING")
    )
    asset.public_url = f"/api/v1/assets/public/{asset.id}" if asset.status == "READY" else None
    db.commit()
    return model_dict(asset)


@router.post("/{tenant_id}/{asset_id}/refresh-scan")
def refresh_scan(
    tenant_id: UUID,
    asset_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_admin),
) -> dict:
    asset = db.scalar(select(Asset).where(Asset.id == asset_id, Asset.tenant_id == tenant_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found.")
    info = inspect_s3_object(key=asset.storage_key)
    asset.scan_status = guardduty_scan_result(info["scan_status"])
    asset.scanned_at = datetime.utcnow()
    asset.status = (
        "READY"
        if asset.scan_status == "CLEAN"
        else ("QUARANTINED" if asset.scan_status == "INFECTED" else "SCANNING")
    )
    asset.public_url = f"/api/v1/assets/public/{asset.id}" if asset.status == "READY" else None
    db.commit()
    return model_dict(asset)


@router.get("/{tenant_id}/{asset_id}/download")
def download_asset(
    tenant_id: UUID,
    asset_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
):
    from fastapi.responses import FileResponse, RedirectResponse

    asset = db.scalar(select(Asset).where(Asset.id == asset_id, Asset.tenant_id == tenant_id))
    if not asset or not ready(asset):
        raise HTTPException(status_code=404, detail="Asset not found.")
    url = presigned_download(key=asset.storage_key)
    if url:
        return RedirectResponse(url)
    path = local_path(asset.storage_key)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Stored file is unavailable.")
    return FileResponse(path, media_type=asset.mime_type, filename=asset.filename)


@router.delete("/{tenant_id}/{asset_id}", status_code=204)
def delete_asset(
    tenant_id: UUID,
    asset_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_admin),
):
    asset = db.scalar(select(Asset).where(Asset.id == asset_id, Asset.tenant_id == tenant_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found.")
    if not settings.s3_bucket:
        delete_local(asset.storage_key)
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="asset",
        entity_id=asset.id,
        action="asset.deleted",
    )
    db.delete(asset)
    db.commit()
