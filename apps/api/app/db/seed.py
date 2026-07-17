from __future__ import annotations

from uuid import NAMESPACE_DNS, uuid5

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.entities import (
    AnalyticsEvent,
    CreditAccount,
    CreditTransaction,
    Domain,
    FeatureFlag,
    Lead,
    NotificationSetting,
    SeoAudit,
    Site,
    SiteVersion,
    Tenant,
    TenantMembership,
)
from app.db.models.enums import (
    CreditTransactionType,
    DomainStatus,
    LeadStatus,
    MembershipRole,
    SeoAuditStatus,
    SiteVersionStatus,
)
from app.modules.sites.defaults import default_content, default_seo, default_theme

settings = get_settings()


def seed_development(db: Session) -> None:
    if settings.is_production or db.scalar(select(Tenant.id).limit(1)):
        return

    admin_id = uuid5(NAMESPACE_DNS, "admin@zylora.dev")
    samples = [
        ("Northstar Academy", "northstar-academy", "school"),
        ("Apex Learning Studio", "apex-learning", "coaching"),
        ("Harbour Clinic", "harbour-clinic", "clinic"),
    ]
    for index, (name, slug, industry) in enumerate(samples):
        tenant = Tenant(
            name=name,
            legal_name=f"{name} Private Limited",
            slug=slug,
            industry=industry,
            owner_name="Sample Owner",
            email=f"hello@{slug}.example",
            phone="+91 90000 00000",
            whatsapp_number="+91 90000 00000",
            address="Chennai, Tamil Nadu",
            onboarding_complete=True,
        )
        db.add(tenant)
        db.flush()
        db.add(
            TenantMembership(
                tenant_id=tenant.id,
                user_id=admin_id,
                email="admin@zylora.dev",
                role=MembershipRole.CLIENT_ADMIN,
            )
        )
        site = Site(tenant_id=tenant.id, name=f"{name} website", template_key=industry)
        db.add(site)
        db.flush()
        content = default_content(name, industry)
        content["footer"]["email"] = tenant.email
        content["footer"]["phone"] = tenant.phone
        content["footer"]["address"] = tenant.address
        version = SiteVersion(
            tenant_id=tenant.id,
            site_id=site.id,
            version_number=1,
            status=SiteVersionStatus.PUBLISHED if index < 2 else SiteVersionStatus.DRAFT,
            content_snapshot=content,
            theme_snapshot=default_theme(),
            seo_snapshot=default_seo(name),
            validation_snapshot={"valid": True, "errors": [], "warnings": []},
            created_by=admin_id,
            approved_by=admin_id if index < 2 else None,
        )
        db.add(version)
        db.flush()
        site.published_version_id = version.id if index < 2 else None
        site.draft_version_id = None if index < 2 else version.id

        account = CreditAccount(
            tenant_id=tenant.id,
            balance_micro_usd=(25 - index * 7) * 1_000_000,
        )
        db.add(account)
        db.flush()
        db.add(
            CreditTransaction(
                tenant_id=tenant.id,
                credit_account_id=account.id,
                type=CreditTransactionType.PURCHASE,
                amount_micro_usd=account.balance_micro_usd,
                balance_after_micro_usd=account.balance_micro_usd,
                description="Development seed credit",
                external_reference=f"seed-{slug}",
                idempotency_key=f"seed:{slug}",
            )
        )
        db.add(NotificationSetting(tenant_id=tenant.id, visitor_enabled=index == 0))
        for key, enabled in {
            "client_dashboard": True,
            "whatsapp": True,
            "seo": True,
            "chatbot": index == 0,
            "analytics": True,
            "custom_domain": True,
        }.items():
            db.add(FeatureFlag(tenant_id=tenant.id, key=key, enabled=enabled))
        domain = Domain(
            tenant_id=tenant.id,
            site_id=site.id,
            hostname=f"{slug}.localhost",
            domain_type="subdomain",
            status=DomainStatus.ACTIVE,
            is_primary=True,
        )
        db.add(domain)
        if index < 2:
            for lead_index in range(4 - index):
                db.add(
                    Lead(
                        tenant_id=tenant.id,
                        site_id=site.id,
                        name=f"Sample Lead {lead_index + 1}",
                        email=f"lead{lead_index + 1}@example.com",
                        phone="+91 98888 00000",
                        service="Consultation",
                        status=LeadStatus.NEW if lead_index < 2 else LeadStatus.CONTACTED,
                        source="website",
                    )
                )
            db.add(
                SeoAudit(
                    tenant_id=tenant.id,
                    site_id=site.id,
                    version_id=version.id,
                    status=SeoAuditStatus.COMPLETED,
                    score=88 - index * 4,
                    grade="B",
                    summary="Development SEO audit.",
                    issues_json=[],
                    recommendations_json=[],
                )
            )
            for event_index in range(12):
                db.add(
                    AnalyticsEvent(
                        tenant_id=tenant.id,
                        site_id=site.id,
                        session_id=f"session-{index}-{event_index}",
                        event_type="page_view",
                        path="/",
                    )
                )
    db.commit()
