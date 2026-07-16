from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_tenant_access
from app.db.models.entities import AnalyticsEvent, Lead
from app.db.session import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])


class AnalyticsEventCreate(BaseModel):
    tenant_id: UUID
    site_id: UUID | None = None
    session_id: str | None = Field(default=None, max_length=120)
    event_type: str = Field(min_length=1, max_length=80)
    path: str | None = Field(default=None, max_length=500)
    referrer: str | None = Field(default=None, max_length=500)
    metadata: dict = Field(default_factory=dict)


@router.post("/public", status_code=202)
def capture_event(payload: AnalyticsEventCreate, db: Session = Depends(get_db)) -> dict:
    event = AnalyticsEvent(
        tenant_id=payload.tenant_id,
        site_id=payload.site_id,
        session_id=payload.session_id,
        event_type=payload.event_type,
        path=payload.path,
        referrer=payload.referrer,
        metadata_json=payload.metadata,
    )
    db.add(event)
    db.commit()
    return {"accepted": True}


@router.get("/{tenant_id}")
def overview(
    tenant_id: UUID,
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    since = datetime.utcnow() - timedelta(days=days)
    rows = db.execute(
        select(AnalyticsEvent.event_type, func.count(AnalyticsEvent.id))
        .where(AnalyticsEvent.tenant_id == tenant_id, AnalyticsEvent.created_at >= since)
        .group_by(AnalyticsEvent.event_type)
    ).all()
    page_views = dict(rows).get("page_view", 0)
    lead_count = db.scalar(
        select(func.count(Lead.id)).where(Lead.tenant_id == tenant_id, Lead.created_at >= since)
    ) or 0
    top_pages = db.execute(
        select(AnalyticsEvent.path, func.count(AnalyticsEvent.id).label("count"))
        .where(
            AnalyticsEvent.tenant_id == tenant_id,
            AnalyticsEvent.created_at >= since,
            AnalyticsEvent.event_type == "page_view",
        )
        .group_by(AnalyticsEvent.path)
        .order_by(func.count(AnalyticsEvent.id).desc())
        .limit(10)
    ).all()
    return {
        "periodDays": days,
        "events": {key: value for key, value in rows},
        "pageViews": page_views,
        "leads": lead_count,
        "conversionRate": round((lead_count / page_views * 100), 2) if page_views else 0,
        "topPages": [{"path": path or "/", "views": count} for path, count in top_pages],
    }
