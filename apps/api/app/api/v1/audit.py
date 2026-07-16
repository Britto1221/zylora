from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_tenant_access
from app.core.serialization import model_dict
from app.db.models.entities import AuditLog
from app.db.session import get_db

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/{tenant_id}")
def audit_logs(
    tenant_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    items = db.scalars(
        select(AuditLog)
        .where(AuditLog.tenant_id == tenant_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    ).all()
    return {"items": [model_dict(item) for item in items]}
