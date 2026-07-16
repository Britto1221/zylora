from __future__ import annotations

import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, get_current_user, require_super_admin, require_tenant_access
from app.core.serialization import model_dict
from app.db.models.entities import (
    CreditAccount, FeatureFlag, NotificationSetting, Site, SiteVersion, Tenant, TenantMembership,
)
from app.db.session import get_db
from app.modules.audit.service import record_audit
from app.modules.sites.defaults import default_content, default_seo, default_theme

router = APIRouter(prefix="/tenants", tags=["tenants"])


class TenantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    slug: str | None = None
    industry: str = "general"
    legal_name: str | None = None
    owner_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    whatsapp_number: str | None = None
    address: str | None = None
    template_key: str = "general"


class TenantUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    industry: str | None = None
    owner_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    whatsapp_number: str | None = None
    address: str | None = None
    is_active: bool | None = None
    onboarding_complete: bool | None = None
    metadata_json: dict | None = None


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "client"


@router.get("")
def list_tenants(
    search: str = "",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    statement = select(Tenant)
    count_statement = select(func.count(Tenant.id))
    if search:
        pattern = f"%{search.strip()}%"
        condition = or_(Tenant.name.ilike(pattern), Tenant.slug.ilike(pattern), Tenant.email.ilike(pattern))
        statement = statement.where(condition)
        count_statement = count_statement.where(condition)
    total = db.scalar(count_statement) or 0
    tenants = db.scalars(
        statement.order_by(Tenant.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return {"items": [model_dict(item) for item in tenants], "total": total, "page": page, "pageSize": page_size}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    base = slugify(payload.slug or payload.name)
    slug = base
    suffix = 2
    while db.scalar(select(Tenant.id).where(Tenant.slug == slug)):
        slug = f"{base}-{suffix}"
        suffix += 1

    tenant = Tenant(
        name=payload.name,
        slug=slug,
        industry=payload.industry,
        legal_name=payload.legal_name,
        owner_name=payload.owner_name,
        email=str(payload.email) if payload.email else None,
        phone=payload.phone,
        whatsapp_number=payload.whatsapp_number,
        address=payload.address,
    )
    db.add(tenant)
    db.flush()

    site = Site(
        tenant_id=tenant.id,
        name=f"{tenant.name} website",
        template_key=payload.template_key,
    )
    db.add(site)
    db.flush()

    version = SiteVersion(
        tenant_id=tenant.id,
        site_id=site.id,
        version_number=1,
        content_snapshot=default_content(tenant.name, payload.template_key),
        theme_snapshot=default_theme(),
        seo_snapshot=default_seo(tenant.name),
        created_by=user.id,
    )
    db.add(version)
    db.flush()
    site.draft_version_id = version.id

    db.add(CreditAccount(tenant_id=tenant.id))
    db.add(NotificationSetting(tenant_id=tenant.id))
    for key, enabled in {
        "client_dashboard": True, "whatsapp": False, "seo": True,
        "chatbot": False, "analytics": True, "custom_domain": True,
    }.items():
        db.add(FeatureFlag(tenant_id=tenant.id, key=key, enabled=enabled))

    record_audit(
        db, actor_user_id=user.id, tenant_id=tenant.id, entity_type="tenant",
        entity_id=tenant.id, action="tenant.created", payload={"site_id": str(site.id)},
    )
    db.commit()
    return {"tenant": model_dict(tenant), "site": model_dict(site), "draft": model_dict(version)}



@router.get("/slug/{slug}")
def get_tenant_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
) -> dict:
    tenant = db.scalar(select(Tenant).where(Tenant.slug == slug))
    if not tenant:
        raise HTTPException(status_code=404, detail="Client not found.")
    if not user.is_super_admin:
        membership = db.scalar(
            select(TenantMembership).where(
                TenantMembership.tenant_id == tenant.id,
                TenantMembership.user_id == user.id,
                TenantMembership.is_active.is_(True),
            )
        )
        if not membership:
            raise HTTPException(status_code=403, detail="Cross-tenant access denied.")
    return {"tenant": model_dict(tenant)}


@router.get("/{tenant_id}")
def get_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Client not found.")
    site = db.scalar(select(Site).where(Site.tenant_id == tenant_id))
    flags = db.scalars(select(FeatureFlag).where(FeatureFlag.tenant_id == tenant_id)).all()
    return {
        "tenant": model_dict(tenant),
        "site": model_dict(site) if site else None,
        "features": {flag.key: flag.enabled for flag in flags},
    }


@router.patch("/{tenant_id}")
def update_tenant(
    tenant_id: UUID,
    payload: TenantUpdate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Client not found.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key == "email" and value is not None:
            value = str(value)
        setattr(tenant, key, value)
    record_audit(
        db, actor_user_id=user.id, tenant_id=tenant.id,
        entity_type="tenant", entity_id=tenant.id, action="tenant.updated",
        payload=payload.model_dump(exclude_unset=True, mode="json"),
    )
    db.commit()
    db.refresh(tenant)
    return model_dict(tenant)


@router.patch("/{tenant_id}/features/{key}")
def update_feature(
    tenant_id: UUID,
    key: str,
    enabled: bool,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    flag = db.scalar(
        select(FeatureFlag).where(FeatureFlag.tenant_id == tenant_id, FeatureFlag.key == key)
    )
    if not flag:
        flag = FeatureFlag(tenant_id=tenant_id, key=key)
        db.add(flag)
    flag.enabled = enabled
    record_audit(
        db, actor_user_id=user.id, tenant_id=tenant_id,
        entity_type="feature_flag", entity_id=flag.id,
        action="feature_flag.updated", payload={"key": key, "enabled": enabled},
    )
    db.commit()
    return {"key": key, "enabled": enabled}
