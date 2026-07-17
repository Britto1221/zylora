from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_super_admin
from app.core.serialization import model_dict
from app.db.models.entities import Tenant, TenantNote
from app.db.session import get_db
from app.modules.admin_clients.service import (
    append_tenant_note,
    queue_manual_payment_reminder,
    set_pause_state,
)
from app.modules.audit.service import record_audit
from app.modules.billing.service import clear_billing_restriction, oldest_unpaid_recurring_invoice

router = APIRouter(prefix="/admin/clients", tags=["super-admin clients"])


class TenantIdsPayload(BaseModel):
    tenant_ids: list[UUID] = Field(min_length=1, max_length=100)


class PausePayload(BaseModel):
    paused: bool
    reason: str = Field(min_length=3, max_length=1000)


class NotePayload(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


def _load_tenants(db: Session, tenant_ids: list[UUID]) -> list[Tenant]:
    unique_ids = list(dict.fromkeys(tenant_ids))
    tenants = list(db.scalars(select(Tenant).where(Tenant.id.in_(unique_ids))).all())
    found = {tenant.id for tenant in tenants}
    missing = [str(tenant_id) for tenant_id in unique_ids if tenant_id not in found]
    if missing:
        raise HTTPException(
            status_code=404,
            detail={"message": "One or more clients were not found.", "tenantIds": missing},
        )
    return tenants


@router.post("/bulk/payment-reminders")
def bulk_payment_reminders(
    payload: TenantIdsPayload,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    tenants = _load_tenants(db, payload.tenant_ids)
    results = [
        queue_manual_payment_reminder(db, tenant=tenant, actor_user_id=user.id)
        for tenant in tenants
    ]
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=None,
        entity_type="bulk_client_action",
        action="billing.payment_reminder_bulk_requested",
        payload={"tenant_ids": [str(tenant.id) for tenant in tenants]},
    )
    db.commit()
    return {"results": results, "selected": len(tenants)}


@router.post("/bulk/clear-lockouts")
def bulk_clear_lockouts(
    payload: TenantIdsPayload,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    tenants = _load_tenants(db, payload.tenant_ids)
    results: list[dict] = []
    for tenant in tenants:
        invoice = oldest_unpaid_recurring_invoice(db, tenant.id)
        clear_billing_restriction(
            db,
            tenant=tenant,
            actor_user_id=user.id,
            reason="super_admin_bulk_manual_override",
            action="billing.lockout_manual_override",
            override_invoice_id=invoice.id if invoice else None,
        )
        results.append({"tenantId": str(tenant.id), "billingStatus": tenant.billing_status.value})
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=None,
        entity_type="bulk_client_action",
        action="billing.lockout_bulk_override_requested",
        payload={"tenant_ids": [str(tenant.id) for tenant in tenants]},
    )
    db.commit()
    return {"results": results, "selected": len(tenants)}


@router.post("/{tenant_id}/pause")
def update_pause_state(
    tenant_id: UUID,
    payload: PausePayload,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Client not found.")
    try:
        set_pause_state(
            db,
            tenant=tenant,
            paused=payload.paused,
            reason=payload.reason,
            actor_user_id=user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(tenant)
    return model_dict(tenant)


@router.get("/{tenant_id}/notes")
def list_notes(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    if db.get(Tenant, tenant_id) is None:
        raise HTTPException(status_code=404, detail="Client not found.")
    notes = db.scalars(
        select(TenantNote)
        .where(TenantNote.tenant_id == tenant_id)
        .order_by(TenantNote.created_at.desc())
    ).all()
    return {"items": [model_dict(note) for note in notes]}


@router.post("/{tenant_id}/notes")
def add_note(
    tenant_id: UUID,
    payload: NotePayload,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Client not found.")
    try:
        note = append_tenant_note(
            db,
            tenant=tenant,
            author_user_id=user.id,
            author_email=user.email,
            body=payload.text,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(note)
    return model_dict(note)
