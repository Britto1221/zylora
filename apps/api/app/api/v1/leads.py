from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_tenant_access
from app.core.serialization import model_dict
from app.db.models.entities import Lead, LeadNote, Site
from app.db.models.enums import LeadStatus
from app.db.session import get_db
from app.modules.audit.service import record_audit
from app.modules.leads.schemas import LeadNoteCreate, LeadUpdate, PublicLeadCreate
from app.modules.notifications.service import create_jobs_for_lead

router = APIRouter(prefix="/leads", tags=["leads"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/public", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def create_public_lead(
    request: Request,
    payload: PublicLeadCreate,
    db: Session = Depends(get_db),
) -> dict:
    if payload.metadata.get("website"):
        # Honeypot: return a neutral response without storing spam.
        return {"accepted": True}

    site = db.get(Site, payload.site_id)
    if not site or not site.published_version_id:
        raise HTTPException(status_code=404, detail="Published website not found.")

    metadata = dict(payload.metadata)
    metadata.update(
        {
            "ip": request.client.host if request.client else None,
            "userAgent": request.headers.get("user-agent"),
            "referer": request.headers.get("referer"),
        }
    )
    lead = Lead(
        tenant_id=site.tenant_id,
        site_id=site.id,
        name=payload.name,
        email=str(payload.email) if payload.email else None,
        phone=payload.phone,
        service=payload.service,
        preferred_contact=payload.preferred_contact,
        message=payload.message,
        whatsapp_consent=payload.whatsapp_consent,
        marketing_consent=payload.marketing_consent,
        consented_at=datetime.utcnow() if payload.whatsapp_consent or payload.marketing_consent else None,
        source=payload.source,
        metadata_json=metadata,
    )
    db.add(lead)
    db.flush()
    jobs = create_jobs_for_lead(db, lead)
    # Lead and notification jobs are committed atomically. Sending happens later.
    db.commit()
    return {
        "accepted": True,
        "leadId": str(lead.id),
        "notificationJobs": len(jobs),
    }


@router.get("/tenant/{tenant_id}")
def list_leads(
    tenant_id: UUID,
    search: str = "",
    lead_status: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    statement = select(Lead).where(Lead.tenant_id == tenant_id)
    count_statement = select(func.count(Lead.id)).where(Lead.tenant_id == tenant_id)
    conditions = []
    if search:
        pattern = f"%{search}%"
        conditions.append(or_(Lead.name.ilike(pattern), Lead.email.ilike(pattern), Lead.phone.ilike(pattern)))
    if lead_status:
        try:
            conditions.append(Lead.status == LeadStatus(lead_status))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid lead status.") from exc
    if conditions:
        statement = statement.where(*conditions)
        count_statement = count_statement.where(*conditions)
    total = db.scalar(count_statement) or 0
    leads = db.scalars(
        statement.order_by(Lead.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return {"items": [model_dict(item) for item in leads], "total": total, "page": page, "pageSize": page_size}


@router.get("/tenant/{tenant_id}/{lead_id}")
def get_lead(
    tenant_id: UUID,
    lead_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    lead = db.scalar(select(Lead).where(Lead.id == lead_id, Lead.tenant_id == tenant_id))
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    notes = db.scalars(
        select(LeadNote).where(LeadNote.lead_id == lead.id).order_by(LeadNote.created_at)
    ).all()
    return {"lead": model_dict(lead), "notes": [model_dict(item) for item in notes]}


@router.patch("/tenant/{tenant_id}/{lead_id}")
def update_lead(
    tenant_id: UUID,
    lead_id: UUID,
    payload: LeadUpdate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    lead = db.scalar(select(Lead).where(Lead.id == lead_id, Lead.tenant_id == tenant_id))
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    values = payload.model_dump(exclude_unset=True)
    if "status" in values and values["status"]:
        try:
            lead.status = LeadStatus(values["status"])
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid lead status.") from exc
    if "service" in values:
        lead.service = values["service"]
    record_audit(
        db, actor_user_id=user.id, tenant_id=tenant_id,
        entity_type="lead", entity_id=lead.id, action="lead.updated", payload=values,
    )
    db.commit()
    return model_dict(lead)


@router.post("/tenant/{tenant_id}/{lead_id}/notes")
def add_note(
    tenant_id: UUID,
    lead_id: UUID,
    payload: LeadNoteCreate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    lead = db.scalar(select(Lead).where(Lead.id == lead_id, Lead.tenant_id == tenant_id))
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    note = LeadNote(
        tenant_id=tenant_id, lead_id=lead.id, author_user_id=user.id, body=payload.body
    )
    db.add(note)
    record_audit(
        db, actor_user_id=user.id, tenant_id=tenant_id,
        entity_type="lead_note", entity_id=note.id, action="lead.note_added",
    )
    db.commit()
    return model_dict(note)


@router.get("/tenant/{tenant_id}/export/csv")
def export_csv(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
):
    import csv
    import io
    from fastapi.responses import StreamingResponse

    leads = db.scalars(
        select(Lead).where(Lead.tenant_id == tenant_id).order_by(Lead.created_at.desc())
    ).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Email", "Phone", "Service", "Status", "Source", "Created"])
    for lead in leads:
        writer.writerow([
            lead.name, lead.email or "", lead.phone or "", lead.service or "",
            lead.status.value, lead.source, lead.created_at.isoformat(),
        ])
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="zylora-leads-{tenant_id}.csv"'},
    )
