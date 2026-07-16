from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_tenant_access
from app.core.serialization import model_dict
from app.db.models.entities import Payment
from app.db.session import get_db
from app.modules.payments.service import create_order

router = APIRouter(prefix="/payments", tags=["payments"])


class OrderCreate(BaseModel):
    charged_amount_minor: int = Field(gt=0)
    charged_currency: str = Field(default="INR", min_length=3, max_length=3)
    usd_credit_micro_amount: int = Field(gt=0)


@router.get("/{tenant_id}")
def payment_history(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    items = db.scalars(
        select(Payment).where(Payment.tenant_id == tenant_id).order_by(Payment.created_at.desc())
    ).all()
    return {"items": [model_dict(item) for item in items]}


@router.post("/{tenant_id}/orders")
def new_order(
    tenant_id: UUID,
    payload: OrderCreate,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    # In production, acceptable packs and FX conversion must come from a server-side price table.
    if payload.usd_credit_micro_amount not in {10_000_000, 25_000_000, 50_000_000, 100_000_000}:
        raise HTTPException(status_code=400, detail="Unsupported credit pack.")
    receipt = f"zylora-{tenant_id}-{uuid4().hex[:12]}"
    return create_order(
        amount_minor=payload.charged_amount_minor,
        currency=payload.charged_currency.upper(),
        receipt=receipt,
        notes={
            "tenant_id": str(tenant_id),
            "usd_credit_micro_amount": str(payload.usd_credit_micro_amount),
        },
    )
