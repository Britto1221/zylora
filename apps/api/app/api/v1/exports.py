from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.background import BackgroundTask

from app.core.security import AuthenticatedUser, require_super_admin
from app.db.session import get_db
from app.modules.exports.service import build_client_export

router = APIRouter(prefix="/exports", tags=["exports"])


class BulkExportPayload(BaseModel):
    tenant_ids: list[UUID] = Field(min_length=1, max_length=50)


@router.post("/bulk")
def export_multiple_client_sites(
    payload: BulkExportPayload,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> FileResponse:
    directory = Path(tempfile.mkdtemp(prefix="zylora-bulk-export-api-"))
    bundle_path = directory / "zylora-client-exports.zip"
    try:
        tenant_ids = list(dict.fromkeys(payload.tenant_ids))
        with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            for tenant_id in tenant_ids:
                client_zip = build_client_export(
                    db,
                    tenant_id=tenant_id,
                    actor_user_id=user.id,
                    output_dir=directory,
                )
                bundle.write(client_zip, client_zip.name)
        from app.modules.audit.service import record_audit

        record_audit(
            db,
            actor_user_id=user.id,
            tenant_id=None,
            entity_type="bulk_client_action",
            action="client.bulk_export_generated",
            payload={"tenant_ids": [str(value) for value in tenant_ids]},
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        shutil.rmtree(directory, ignore_errors=True)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(
        bundle_path,
        media_type="application/zip",
        filename=bundle_path.name,
        background=BackgroundTask(shutil.rmtree, directory, ignore_errors=True),
    )


@router.post("/{tenant_id}")
def export_client_site(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> FileResponse:
    directory = Path(tempfile.mkdtemp(prefix="zylora-export-api-"))
    try:
        zip_path = build_client_export(
            db,
            tenant_id=tenant_id,
            actor_user_id=user.id,
            output_dir=directory,
        )
        db.commit()
    except ValueError as exc:
        shutil.rmtree(directory, ignore_errors=True)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=zip_path.name,
        background=BackgroundTask(shutil.rmtree, directory, ignore_errors=True),
    )
