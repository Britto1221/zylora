from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_super_admin, require_tenant_access
from app.core.serialization import model_dict
from app.db.models.entities import CreditTransaction
from app.db.models.enums import CreditTransactionType
from app.db.session import get_db
from app.modules.audit.service import record_audit
from app.modules.credits.schemas import ManualTopUp
from app.modules.credits.service import (
    append_transaction, get_or_create_account, micro_usd_to_usd, usd_to_micro_usd
)

router = APIRouter(prefix="/credits", tags=["credits"])


@router.get("/{tenant_id}")
def get_balance(
    tenant_id: UUID,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    account = get_or_create_account(db, tenant_id)
    transactions = db.scalars(
        select(CreditTransaction)
        .where(CreditTransaction.tenant_id == tenant_id)
        .order_by(CreditTransaction.created_at.desc())
        .limit(limit)
    ).all()
    db.commit()
    return {
        "account": {
            **model_dict(account),
            "balanceUsd": f"{micro_usd_to_usd(account.balance_micro_usd):.6f}",
            "reservedUsd": f"{micro_usd_to_usd(account.reserved_micro_usd):.6f}",
            "availableUsd": f"{micro_usd_to_usd(account.balance_micro_usd - account.reserved_micro_usd):.6f}",
        },
        "transactions": [model_dict(item) for item in transactions],
    }


@router.post("/{tenant_id}/manual-top-up")
def manual_top_up(
    tenant_id: UUID,
    payload: ManualTopUp,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    amount = Decimal(payload.amount_usd)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive.")
    reference = payload.external_reference or f"manual:{uuid4()}"
    transaction = append_transaction(
        db,
        tenant_id=tenant_id,
        transaction_type=CreditTransactionType.PURCHASE,
        amount_micro_usd=usd_to_micro_usd(amount),
        description=payload.description,
        external_reference=reference,
        idempotency_key=f"topup:{tenant_id}:{reference}",
    )
    record_audit(
        db, actor_user_id=user.id, tenant_id=tenant_id,
        entity_type="credit_transaction", entity_id=transaction.id,
        action="credits.manual_top_up",
        payload={"amount_usd": str(amount), "reference": reference},
    )
    db.commit()
    return model_dict(transaction)


@router.post("/{tenant_id}/adjust")
def adjust(
    tenant_id: UUID,
    amount_usd: str,
    reason: str,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    amount = Decimal(amount_usd)
    transaction = append_transaction(
        db,
        tenant_id=tenant_id,
        transaction_type=CreditTransactionType.ADJUSTMENT,
        amount_micro_usd=usd_to_micro_usd(amount),
        description=reason,
        idempotency_key=f"adjust:{tenant_id}:{uuid4()}",
    )
    record_audit(
        db, actor_user_id=user.id, tenant_id=tenant_id,
        entity_type="credit_transaction", entity_id=transaction.id,
        action="credits.adjusted", payload={"amount_usd": str(amount), "reason": reason},
    )
    db.commit()
    return model_dict(transaction)
