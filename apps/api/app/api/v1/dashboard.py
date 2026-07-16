from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_super_admin
from app.db.models.entities import (
    CreditAccount, Domain, Lead, NotificationJob, SeoAudit, Site, SiteVersion, Tenant
)
from app.db.models.enums import NotificationStatus, SeoAuditStatus, SiteVersionStatus
from app.db.session import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    today = datetime.utcnow() - timedelta(days=1)
    scalar = lambda stmt: db.scalar(stmt) or 0
    recent_leads = db.scalars(
        select(Lead).order_by(Lead.created_at.desc()).limit(6)
    ).all()
    expiring_domains = db.scalars(
        select(Domain)
        .where(Domain.expires_at.is_not(None))
        .order_by(Domain.expires_at.asc())
        .limit(6)
    ).all()

    return {
        "metrics": {
            "clients": scalar(select(func.count(Tenant.id))),
            "activeClients": scalar(select(func.count(Tenant.id)).where(Tenant.is_active.is_(True))),
            "publishedSites": scalar(select(func.count(Site.id)).where(Site.published_version_id.is_not(None))),
            "draftSites": scalar(select(func.count(SiteVersion.id)).where(SiteVersion.status == SiteVersionStatus.DRAFT)),
            "newLeads": scalar(select(func.count(Lead.id)).where(Lead.created_at >= today)),
            "pendingSeo": scalar(select(func.count(SeoAudit.id)).where(SeoAudit.status.in_([SeoAuditStatus.QUEUED, SeoAuditStatus.RUNNING]))),
            "failedMessages": scalar(select(func.count(NotificationJob.id)).where(NotificationJob.status == NotificationStatus.FAILED)),
            "creditAlerts": scalar(select(func.count(CreditAccount.id)).where(CreditAccount.balance_micro_usd <= CreditAccount.low_balance_threshold_micro_usd)),
        },
        "recentLeads": [
            {
                "id": str(lead.id), "tenantId": str(lead.tenant_id), "name": lead.name,
                "service": lead.service, "status": lead.status.value,
                "createdAt": lead.created_at.isoformat(),
            }
            for lead in recent_leads
        ],
        "expiringDomains": [
            {
                "id": str(domain.id), "tenantId": str(domain.tenant_id),
                "hostname": domain.hostname, "status": domain.status.value,
                "expiresAt": domain.expires_at.isoformat() if domain.expires_at else None,
            }
            for domain in expiring_domains
        ],
    }
