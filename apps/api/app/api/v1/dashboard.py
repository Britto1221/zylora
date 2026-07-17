from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_super_admin
from app.db.models.entities import (
    CreditAccount,
    Domain,
    Invoice,
    Lead,
    NotificationJob,
    SeoAudit,
    Site,
    SiteVersion,
    Tenant,
)
from app.db.models.enums import (
    BillingStatus,
    InvoiceStatus,
    InvoiceType,
    NotificationStatus,
    SeoAuditStatus,
    SiteVersionStatus,
    TenantStatus,
)
from app.db.session import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    today = datetime.utcnow() - timedelta(days=1)

    def scalar(stmt):
        return db.scalar(stmt) or 0

    recent_leads = db.scalars(select(Lead).order_by(Lead.created_at.desc()).limit(6)).all()
    expiring_domains = db.scalars(
        select(Domain)
        .where(Domain.expires_at.is_not(None))
        .order_by(Domain.expires_at.asc())
        .limit(6)
    ).all()

    return {
        "metrics": {
            "clients": scalar(select(func.count(Tenant.id))),
            "activeClients": scalar(
                select(func.count(Tenant.id)).where(Tenant.is_active.is_(True))
            ),
            "publishedSites": scalar(
                select(func.count(Site.id)).where(Site.published_version_id.is_not(None))
            ),
            "draftSites": scalar(
                select(func.count(SiteVersion.id)).where(
                    SiteVersion.status == SiteVersionStatus.DRAFT
                )
            ),
            "newLeads": scalar(select(func.count(Lead.id)).where(Lead.created_at >= today)),
            "pendingSeo": scalar(
                select(func.count(SeoAudit.id)).where(
                    SeoAudit.status.in_([SeoAuditStatus.QUEUED, SeoAuditStatus.RUNNING])
                )
            ),
            "failedMessages": scalar(
                select(func.count(NotificationJob.id)).where(
                    NotificationJob.status == NotificationStatus.FAILED
                )
            ),
            "creditAlerts": scalar(
                select(func.count(CreditAccount.id)).where(
                    CreditAccount.balance_micro_usd <= CreditAccount.low_balance_threshold_micro_usd
                )
            ),
        },
        "recentLeads": [
            {
                "id": str(lead.id),
                "tenantId": str(lead.tenant_id),
                "name": lead.name,
                "service": lead.service,
                "status": lead.status.value,
                "createdAt": lead.created_at.isoformat(),
            }
            for lead in recent_leads
        ],
        "expiringDomains": [
            {
                "id": str(domain.id),
                "tenantId": str(domain.tenant_id),
                "hostname": domain.hostname,
                "status": domain.status.value,
                "expiresAt": domain.expires_at.isoformat() if domain.expires_at else None,
            }
            for domain in expiring_domains
        ],
    }


@router.get("/revenue")
def revenue_dashboard(
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    now = datetime.utcnow()
    in_7_days = now + timedelta(days=7)
    in_30_days = now + timedelta(days=30)

    billable_tenants = db.scalars(
        select(Tenant).where(
            Tenant.is_active.is_(True),
            Tenant.operational_status == TenantStatus.ACTIVE,
            Tenant.monthly_amount_minor > 0,
        )
    ).all()
    mrr = {"USD": 0, "INR": 0}
    for tenant in billable_tenants:
        if tenant.billing_currency in mrr:
            mrr[tenant.billing_currency] += tenant.monthly_amount_minor

    unpaid = db.scalars(
        select(Invoice).where(
            Invoice.invoice_type == InvoiceType.RECURRING,
            Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.OVERDUE]),
            Invoice.due_at.is_not(None),
        )
    ).all()
    upcoming_7 = {"count": 0, "USD": 0, "INR": 0}
    upcoming_30 = {"count": 0, "USD": 0, "INR": 0}
    overdue = {"count": 0, "USD": 0, "INR": 0}
    upcoming_items: list[dict] = []
    overdue_items: list[dict] = []

    tenant_names = {
        tenant.id: tenant.name
        for tenant in db.scalars(select(Tenant)).all()
    }
    for invoice in unpaid:
        currency = invoice.currency if invoice.currency in {"USD", "INR"} else None
        if invoice.due_at and now <= invoice.due_at <= in_30_days:
            upcoming_30["count"] += 1
            if currency:
                upcoming_30[currency] += invoice.total_minor
            if invoice.due_at <= in_7_days:
                upcoming_7["count"] += 1
                if currency:
                    upcoming_7[currency] += invoice.total_minor
            upcoming_items.append(
                {
                    "invoiceId": str(invoice.id),
                    "tenantId": str(invoice.tenant_id),
                    "client": tenant_names.get(invoice.tenant_id, "Unknown client"),
                    "number": invoice.number,
                    "currency": invoice.currency,
                    "amountMinor": invoice.total_minor,
                    "dueAt": invoice.due_at.isoformat(),
                }
            )
        elif invoice.due_at and invoice.due_at < now:
            overdue["count"] += 1
            if currency:
                overdue[currency] += invoice.total_minor
            overdue_items.append(
                {
                    "invoiceId": str(invoice.id),
                    "tenantId": str(invoice.tenant_id),
                    "client": tenant_names.get(invoice.tenant_id, "Unknown client"),
                    "number": invoice.number,
                    "currency": invoice.currency,
                    "amountMinor": invoice.total_minor,
                    "dueAt": invoice.due_at.isoformat(),
                }
            )

    billing_counts = {status.value: 0 for status in BillingStatus}
    for tenant in db.scalars(select(Tenant)).all():
        billing_counts[tenant.billing_status.value] += 1

    return {
        "mrr": mrr,
        "billableClients": len(billable_tenants),
        "upcoming7Days": upcoming_7,
        "upcoming30Days": upcoming_30,
        "overdue": overdue,
        "billingStatusCounts": billing_counts,
        "upcomingItems": sorted(upcoming_items, key=lambda item: item["dueAt"])[:25],
        "overdueItems": sorted(overdue_items, key=lambda item: item["dueAt"])[:25],
        "generatedAt": now.isoformat(),
    }
