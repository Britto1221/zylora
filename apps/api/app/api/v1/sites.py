from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_super_admin
from app.db.models.entities import Domain, Site, SiteVersion
from app.db.session import get_db
from app.modules.sites.schemas import PublishedSiteRead

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("/public/resolve", response_model=PublishedSiteRead)
def resolve_public_site(
    host: str = Query(min_length=3, max_length=255),
    db: Session = Depends(get_db),
) -> PublishedSiteRead:
    domain = db.scalar(select(Domain).where(Domain.hostname == host.lower()))
    if domain is None:
        raise HTTPException(status_code=404, detail="Domain not found.")

    site = db.scalar(select(Site).where(Site.id == domain.site_id))
    if site is None or site.published_version_id is None:
        raise HTTPException(status_code=404, detail="Published site not found.")

    version = db.scalar(
        select(SiteVersion).where(SiteVersion.id == site.published_version_id)
    )
    if version is None:
        raise HTTPException(status_code=404, detail="Published version not found.")

    return PublishedSiteRead(
        site_id=site.id,
        version_id=version.id,
        tenant_id=site.tenant_id,
        template_key=site.template_key,
        content=version.content_snapshot,
        theme=version.theme_snapshot,
    )


@router.get("/preview/{version_id}", response_model=PublishedSiteRead)
def preview_site_version(
    version_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_super_admin),
) -> PublishedSiteRead:
    version = db.scalar(select(SiteVersion).where(SiteVersion.id == version_id))
    if version is None:
        raise HTTPException(status_code=404, detail="Version not found.")

    site = db.scalar(select(Site).where(Site.id == version.site_id))
    if site is None:
        raise HTTPException(status_code=404, detail="Site not found.")

    return PublishedSiteRead(
        site_id=site.id,
        version_id=version.id,
        tenant_id=site.tenant_id,
        template_key=site.template_key,
        content=version.content_snapshot,
        theme=version.theme_snapshot,
    )
