from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.entities import Lead, Site
from app.db.session import get_db
from app.modules.leads.schemas import LeadRead, PublicLeadCreate

router = APIRouter(prefix="/leads", tags=["leads"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/public", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def create_public_lead(
    request: Request,
    payload: PublicLeadCreate,
    db: Session = Depends(get_db),
) -> Lead:
    site = db.scalar(select(Site).where(Site.id == payload.site_id))
    if not site:
        raise HTTPException(status_code=404, detail="Site not found.")

    lead = Lead(
        tenant_id=site.tenant_id,
        site_id=site.id,
        name=payload.name,
        email=str(payload.email) if payload.email else None,
        phone=payload.phone,
        service=payload.service,
        message=payload.message,
        whatsapp_consent=payload.whatsapp_consent,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # WhatsApp is intentionally asynchronous and must never block lead capture.
    return lead
