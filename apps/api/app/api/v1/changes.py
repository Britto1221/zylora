from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_tenant_access
from app.core.serialization import model_dict
from app.db.models.entities import ChangeRequest
from app.db.models.enums import ChangeRequestStatus
from app.db.session import get_db
from app.modules.audit.service import record_audit

router = APIRouter(prefix="/changes", tags=["change requests"])


class ChangeCreate(BaseModel):
    category: str = Field(min_length=2, max_length=80)
    title: str = Field(min_length=2, max_length=220)
    description: str = Field(min_length=2, max_length=10000)
    priority: str = Field(default="NORMAL", max_length=20)


class ChangeUpdate(BaseModel):
    status: str | None = None
    quoted_price_minor: int | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    internal_notes: str | None = Field(default=None, max_length=10000)
    completion_notes: str | None = Field(default=None, max_length=10000)


@router.get("/{tenant_id}")
def list_changes(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    items = db.scalars(
        select(ChangeRequest)
        .where(ChangeRequest.tenant_id == tenant_id)
        .order_by(ChangeRequest.created_at.desc())
    ).all()
    return {"items": [model_dict(item) for item in items]}


@router.post("/{tenant_id}", status_code=status.HTTP_201_CREATED)
def create_change(
    tenant_id: UUID,
    payload: ChangeCreate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    change = ChangeRequest(
        tenant_id=tenant_id,
        category=payload.category,
        title=payload.title,
        description=payload.description,
        priority=payload.priority.upper(),
        requested_by=user.id,
    )
    db.add(change)
    db.flush()
    record_audit(
        db, actor_user_id=user.id, tenant_id=tenant_id,
        entity_type="change_request", entity_id=change.id,
        action="change_request.created",
    )
    db.commit()
    return model_dict(change)


@router.patch("/{tenant_id}/{change_id}")
def update_change(
    tenant_id: UUID,
    change_id: UUID,
    payload: ChangeUpdate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    change = db.scalar(
        select(ChangeRequest).where(
            ChangeRequest.id == change_id, ChangeRequest.tenant_id == tenant_id
        )
    )
    if not change:
        raise HTTPException(status_code=404, detail="Change request not found.")
    values = payload.model_dump(exclude_unset=True)
    if values.get("status"):
        try:
            values["status"] = ChangeRequestStatus(values["status"])
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid change-request status.") from exc
    for key, value in values.items():
        setattr(change, key, value)
    record_audit(
        db, actor_user_id=user.id, tenant_id=tenant_id,
        entity_type="change_request", entity_id=change.id,
        action="change_request.updated",
        payload=payload.model_dump(exclude_unset=True),
    )
    db.commit()
    return model_dict(change)
