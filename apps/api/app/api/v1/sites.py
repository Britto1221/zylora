from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import (
    AuthenticatedUser,
    get_current_user,
    require_super_admin,
    require_tenant_access,
    require_tenant_admin,
)
from app.core.serialization import model_dict
from app.db.models.entities import Domain, FeatureFlag, Site, SiteVersion, Tenant
from app.db.models.enums import DomainStatus, SiteVersionStatus
from app.db.session import get_db
from app.modules.audit.service import record_audit
from app.modules.sites.defaults import TEMPLATE_LABELS, default_content, default_seo, default_theme
from app.modules.sites.validation import validate_snapshot

router = APIRouter(prefix="/sites", tags=["sites"])


class DraftUpdate(BaseModel):
    template_key: str | None = None
    content: dict | None = None
    theme: dict | None = None
    seo: dict | None = None


class CreateDraft(BaseModel):
    copy_from_version_id: UUID | None = None


def get_site_for_tenant(db: Session, tenant_id: UUID) -> Site:
    site = db.scalar(select(Site).where(Site.tenant_id == tenant_id, Site.is_active.is_(True)))
    if not site:
        raise HTTPException(status_code=404, detail="Website not found.")
    return site


def get_draft(db: Session, site: Site) -> SiteVersion:
    version = db.get(SiteVersion, site.draft_version_id) if site.draft_version_id else None
    if version and version.status == SiteVersionStatus.DRAFT:
        return version
    latest = db.scalar(
        select(SiteVersion)
        .where(SiteVersion.site_id == site.id, SiteVersion.status == SiteVersionStatus.DRAFT)
        .order_by(SiteVersion.version_number.desc())
    )
    if latest:
        site.draft_version_id = latest.id
        return latest
    raise HTTPException(status_code=404, detail="No editable draft exists.")


@router.get("/templates")
def templates() -> dict:
    return {
        "items": [
            {"key": key, "label": label, "description": f"Structured {label.lower()} landing page"}
            for key, label in TEMPLATE_LABELS.items()
        ]
    }


@router.get("/tenant/{tenant_id}")
def tenant_site(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    site = get_site_for_tenant(db, tenant_id)
    draft = get_draft(db, site)
    published = (
        db.get(SiteVersion, site.published_version_id) if site.published_version_id else None
    )
    return {
        "site": model_dict(site),
        "draft": model_dict(draft),
        "published": model_dict(published) if published else None,
        "validation": validate_snapshot(
            draft.content_snapshot, draft.theme_snapshot, draft.seo_snapshot
        ),
    }


@router.patch("/tenant/{tenant_id}/draft")
def update_draft(
    tenant_id: UUID,
    payload: DraftUpdate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_admin),
) -> dict:
    site = get_site_for_tenant(db, tenant_id)
    draft = get_draft(db, site)
    if payload.template_key:
        if payload.template_key not in TEMPLATE_LABELS:
            raise HTTPException(status_code=400, detail="Unsupported template.")
        site.template_key = payload.template_key
    if payload.content is not None:
        draft.content_snapshot = payload.content
    if payload.theme is not None:
        draft.theme_snapshot = payload.theme
    if payload.seo is not None:
        draft.seo_snapshot = payload.seo

    validation = validate_snapshot(draft.content_snapshot, draft.theme_snapshot, draft.seo_snapshot)
    draft.validation_snapshot = validation
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="site_version",
        entity_id=draft.id,
        action="site.draft_updated",
        payload={"validation": validation},
    )
    db.commit()
    return {"draft": model_dict(draft), "validation": validation}


@router.post("/tenant/{tenant_id}/draft")
def create_draft(
    tenant_id: UUID,
    payload: CreateDraft,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    site = get_site_for_tenant(db, tenant_id)
    source = None
    if payload.copy_from_version_id:
        source = db.get(SiteVersion, payload.copy_from_version_id)
        if not source or source.site_id != site.id:
            raise HTTPException(status_code=404, detail="Source version not found.")
    elif site.published_version_id:
        source = db.get(SiteVersion, site.published_version_id)
    elif site.draft_version_id:
        source = db.get(SiteVersion, site.draft_version_id)

    next_number = (
        db.scalar(
            select(func.max(SiteVersion.version_number)).where(SiteVersion.site_id == site.id)
        )
        or 0
    ) + 1
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found.")
    version = SiteVersion(
        tenant_id=tenant_id,
        site_id=site.id,
        version_number=next_number,
        content_snapshot=deepcopy(source.content_snapshot)
        if source
        else default_content(tenant.name, site.template_key),
        theme_snapshot=deepcopy(source.theme_snapshot) if source else default_theme(),
        seo_snapshot=deepcopy(source.seo_snapshot) if source else default_seo(tenant.name),
        created_by=user.id,
    )
    db.add(version)
    db.flush()
    site.draft_version_id = version.id
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="site_version",
        entity_id=version.id,
        action="site.draft_created",
        payload={"version": next_number},
    )
    db.commit()
    return model_dict(version)


@router.get("/tenant/{tenant_id}/versions")
def versions(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    site = get_site_for_tenant(db, tenant_id)
    items = db.scalars(
        select(SiteVersion)
        .where(SiteVersion.site_id == site.id)
        .order_by(SiteVersion.version_number.desc())
    ).all()
    return {"items": [model_dict(item) for item in items]}


@router.get("/public/resolve")
def resolve_public_site(
    host: str = Query(min_length=3, max_length=255),
    db: Session = Depends(get_db),
) -> dict:
    normalized = host.lower().split(":")[0]
    domain = db.scalar(
        select(Domain).where(Domain.hostname == normalized, Domain.status == DomainStatus.ACTIVE)
    )
    if not domain:
        # Development convenience: <slug>.localhost resolves by tenant slug.
        slug = normalized.split(".")[0]
        tenant = db.scalar(select(Tenant).where(Tenant.slug == slug))
        site = db.scalar(select(Site).where(Site.tenant_id == tenant.id)) if tenant else None
    else:
        site = db.get(Site, domain.site_id)

    if not site or not site.published_version_id:
        raise HTTPException(status_code=404, detail="Published website not found.")
    version = db.get(SiteVersion, site.published_version_id)
    tenant = db.get(Tenant, site.tenant_id)
    if version is None or tenant is None:
        raise HTTPException(status_code=404, detail="Published website data is incomplete.")
    flags = db.scalars(select(FeatureFlag).where(FeatureFlag.tenant_id == site.tenant_id)).all()
    features = {flag.key: flag.enabled for flag in flags}
    return {
        "siteId": str(site.id),
        "versionId": str(version.id),
        "tenantId": str(site.tenant_id),
        "tenantSlug": tenant.slug,
        "templateKey": site.template_key,
        "content": version.content_snapshot,
        "theme": version.theme_snapshot,
        "seo": version.seo_snapshot,
        "features": features,
    }


@router.get("/preview/{version_id}")
def preview(
    version_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(get_current_user),
) -> dict:
    version = db.get(SiteVersion, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found.")
    site = db.get(Site, version.site_id)
    tenant = db.get(Tenant, version.tenant_id)
    if site is None or tenant is None:
        raise HTTPException(status_code=404, detail="Preview website data is incomplete.")
    return {
        "siteId": str(site.id),
        "versionId": str(version.id),
        "tenantId": str(version.tenant_id),
        "tenantSlug": tenant.slug,
        "templateKey": site.template_key,
        "content": version.content_snapshot,
        "theme": version.theme_snapshot,
        "seo": version.seo_snapshot,
        "features": {},
        "preview": True,
    }
