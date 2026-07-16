from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_tenant_access
from app.db.models.entities import CreditAccount, Domain, Lead, NotificationJob, SeoAudit, Site
from app.db.session import get_db
from app.modules.credits.service import get_or_create_account, micro_usd_to_usd

router = APIRouter(prefix="/portal", tags=["client portal"])


@router.get("/{tenant_id}/summary")
def portal_summary(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    site = db.scalar(select(Site).where(Site.tenant_id == tenant_id))
    account = get_or_create_account(db, tenant_id)
    domain = db.scalar(
        select(Domain).where(Domain.tenant_id == tenant_id, Domain.is_primary.is_(True))
    )
    seo = db.scalar(
        select(SeoAudit).where(SeoAudit.tenant_id == tenant_id).order_by(SeoAudit.created_at.desc())
    )
    return {
        "newLeads": db.scalar(
            select(func.count(Lead.id)).where(Lead.tenant_id == tenant_id, Lead.status == "NEW")
        ) or 0,
        "totalLeads": db.scalar(select(func.count(Lead.id)).where(Lead.tenant_id == tenant_id)) or 0,
        "messages": db.scalar(
            select(func.count(NotificationJob.id)).where(NotificationJob.tenant_id == tenant_id)
        ) or 0,
        "creditBalanceUsd": f"{micro_usd_to_usd(account.balance_micro_usd):.4f}",
        "domain": domain.hostname if domain else None,
        "domainExpiresAt": domain.expires_at.isoformat() if domain and domain.expires_at else None,
        "seoScore": seo.score if seo else None,
        "sitePublished": bool(site and site.published_version_id),
    }
