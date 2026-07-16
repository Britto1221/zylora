from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.entities import AuditLog


def record_audit(
    db: Session,
    *,
    actor_user_id: UUID,
    action: str,
    entity_type: str,
    tenant_id: UUID | None = None,
    entity_id: UUID | None = None,
    payload: dict | None = None,
) -> AuditLog:
    log = AuditLog(
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload or {},
    )
    db.add(log)
    db.flush()
    return log
