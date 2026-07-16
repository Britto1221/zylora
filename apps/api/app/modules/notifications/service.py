from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.entities import Lead, NotificationJob, NotificationSetting, Tenant
from app.db.models.enums import NotificationStatus


def get_or_create_settings(db: Session, tenant_id: UUID) -> NotificationSetting:
    setting = db.scalar(
        select(NotificationSetting).where(NotificationSetting.tenant_id == tenant_id)
    )
    if setting:
        return setting
    setting = NotificationSetting(tenant_id=tenant_id)
    db.add(setting)
    db.flush()
    return setting


def create_jobs_for_lead(db: Session, lead: Lead) -> list[NotificationJob]:
    setting = get_or_create_settings(db, lead.tenant_id)
    tenant = db.get(Tenant, lead.tenant_id)
    jobs: list[NotificationJob] = []

    if setting.business_enabled and tenant and tenant.whatsapp_number:
        jobs.append(
            NotificationJob(
                tenant_id=lead.tenant_id,
                lead_id=lead.id,
                recipient_type="BUSINESS",
                recipient=tenant.whatsapp_number,
                template_name=setting.business_template,
                template_variables={
                    "lead_name": lead.name,
                    "service": lead.service or "General enquiry",
                    "phone": lead.phone or "",
                },
                charge_micro_usd=setting.business_charge_micro_usd,
                idempotency_key=f"lead:{lead.id}:business",
            )
        )

    if setting.visitor_enabled and lead.phone:
        if lead.whatsapp_consent:
            jobs.append(
                NotificationJob(
                    tenant_id=lead.tenant_id,
                    lead_id=lead.id,
                    recipient_type="VISITOR",
                    recipient=lead.phone,
                    template_name=setting.visitor_template,
                    template_variables={"lead_name": lead.name},
                    charge_micro_usd=setting.visitor_charge_micro_usd,
                    idempotency_key=f"lead:{lead.id}:visitor",
                )
            )
        else:
            jobs.append(
                NotificationJob(
                    tenant_id=lead.tenant_id,
                    lead_id=lead.id,
                    recipient_type="VISITOR",
                    recipient=lead.phone,
                    template_name=setting.visitor_template,
                    template_variables={"lead_name": lead.name},
                    charge_micro_usd=0,
                    idempotency_key=f"lead:{lead.id}:visitor",
                    status=NotificationStatus.SKIPPED_NO_CONSENT,
                )
            )

    db.add_all(jobs)
    db.flush()
    return jobs
