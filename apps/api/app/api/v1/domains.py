from __future__ import annotations

import secrets
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_super_admin, require_tenant_access
from app.core.serialization import model_dict
from app.db.models.entities import Domain, Site
from app.db.models.enums import DomainStatus
from app.db.session import get_db
from app.modules.audit.service import record_audit

router = APIRouter(prefix="/domains", tags=["domains"])


class DomainCreate(BaseModel):
    hostname: str = Field(min_length=3, max_length=255)
    domain_type: str = "custom"
    is_primary: bool = True
    registered_to_client: bool = True
    expires_at: datetime | None = None
    renewal_price_usd: str = "19.00"

    @field_validator("hostname")
    @classmethod
    def normalize_hostname(cls, value: str) -> str:
        host = value.strip().lower().rstrip(".")
        if "://" in host or "/" in host or " " in host:
            raise ValueError("Enter a hostname without protocol or path.")
        return host


@router.get("/{tenant_id}")
def list_domains(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    items = db.scalars(
        select(Domain).where(Domain.tenant_id == tenant_id).order_by(Domain.created_at.desc())
    ).all()
    return {"items": [model_dict(item) for item in items]}


@router.post("/{tenant_id}")
def add_domain(
    tenant_id: UUID,
    payload: DomainCreate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    if db.scalar(select(Domain.id).where(Domain.hostname == payload.hostname)):
        raise HTTPException(status_code=409, detail="Domain is already registered.")
    site = db.scalar(select(Site).where(Site.tenant_id == tenant_id))
    if not site:
        raise HTTPException(status_code=404, detail="Website not found.")
    if payload.is_primary:
        for current in db.scalars(
            select(Domain).where(Domain.site_id == site.id, Domain.is_primary.is_(True))
        ):
            current.is_primary = False
    domain = Domain(
        tenant_id=tenant_id,
        site_id=site.id,
        hostname=payload.hostname,
        domain_type=payload.domain_type,
        is_primary=payload.is_primary,
        registered_to_client=payload.registered_to_client,
        expires_at=payload.expires_at,
        renewal_price_usd=payload.renewal_price_usd,
        verification_token=secrets.token_urlsafe(24),
        status=DomainStatus.PENDING,
    )
    db.add(domain)
    db.flush()
    record_audit(
        db, actor_user_id=user.id, tenant_id=tenant_id,
        entity_type="domain", entity_id=domain.id,
        action="domain.added", payload={"hostname": domain.hostname},
    )
    db.commit()
    return {
        **model_dict(domain),
        "verification": {
            "type": "TXT",
            "name": f"_zylora-verification.{domain.hostname}",
            "value": domain.verification_token,
        },
    }


@router.post("/{tenant_id}/{domain_id}/verify")
def verify_domain(
    tenant_id: UUID,
    domain_id: UUID,
    confirmed: bool = False,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    domain = db.scalar(
        select(Domain).where(Domain.id == domain_id, Domain.tenant_id == tenant_id)
    )
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found.")
    # A manual confirmation is the safe fallback until a DNS provider is configured.
    domain.status = DomainStatus.ACTIVE if confirmed else DomainStatus.VERIFYING
    record_audit(
        db, actor_user_id=user.id, tenant_id=tenant_id,
        entity_type="domain", entity_id=domain.id,
        action="domain.verification_updated", payload={"confirmed": confirmed},
    )
    db.commit()
    return model_dict(domain)


@router.delete("/{tenant_id}/{domain_id}", status_code=204)
def remove_domain(
    tenant_id: UUID,
    domain_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
):
    domain = db.scalar(
        select(Domain).where(Domain.id == domain_id, Domain.tenant_id == tenant_id)
    )
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found.")
    record_audit(
        db, actor_user_id=user.id, tenant_id=tenant_id,
        entity_type="domain", entity_id=domain.id, action="domain.removed",
        payload={"hostname": domain.hostname},
    )
    db.delete(domain)
    db.commit()
