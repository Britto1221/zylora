from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.entities import Lead, NotificationJob
from app.db.models.enums import NotificationStatus


def create_whatsapp_jobs(
    db: Session,
    *,
    lead: Lead,
    client_phone: str | None,
    visitor_template: str | None = None,
    business_template: str | None = None,
) -> list[NotificationJob]:
    jobs: list[NotificationJob] = []

    if client_phone and business_template:
        jobs.append(
            NotificationJob(
                tenant_id=lead.tenant_id,
                lead_id=lead.id,
                recipient_type="BUSINESS",
                recipient=client_phone,
                template_name=business_template,
                status=NotificationStatus.PENDING,
            )
        )

    if lead.phone and lead.whatsapp_consent and visitor_template:
        jobs.append(
            NotificationJob(
                tenant_id=lead.tenant_id,
                lead_id=lead.id,
                recipient_type="VISITOR",
                recipient=lead.phone,
                template_name=visitor_template,
                status=NotificationStatus.PENDING,
            )
        )

    db.add_all(jobs)
    return jobs
