from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_super_admin, require_tenant_access
from app.db.models.enums import CreditTransactionType
from app.db.session import get_db
from app.modules.credits.schemas import CreditBalanceRead, ManualTopUp
from app.modules.credits.service import (
    append_transaction,
    get_or_create_account,
    micro_usd_to_usd,
    usd_to_micro_usd,
)

router = APIRouter(prefix="/credits", tags=["credits"])


@router.get("/{tenant_id}", response_model=CreditBalanceRead)
def get_balance(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> CreditBalanceRead:
    account = get_or_create_account(db, tenant_id)
    db.commit()
    return CreditBalanceRead(
        tenant_id=tenant_id,
        currency="USD",
        balance_usd=f"{micro_usd_to_usd(account.balance_micro_usd):.4f}",
    )


@router.post("/{tenant_id}/manual-top-up", response_model=CreditBalanceRead)
def manual_top_up(
    tenant_id: UUID,
    payload: ManualTopUp,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_super_admin),
) -> CreditBalanceRead:
    amount = Decimal(payload.amount_usd)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive.")

    transaction = append_transaction(
        db,
        tenant_id=tenant_id,
        transaction_type=CreditTransactionType.PURCHASE,
        amount_micro_usd=usd_to_micro_usd(amount),
        description=payload.description,
        external_reference=payload.external_reference,
        idempotency_key=(
            payload.external_reference
            or f"manual-top-up:{tenant_id}:{payload.amount_usd}:{payload.description}"
        ),
    )
    db.commit()

    return CreditBalanceRead(
        tenant_id=tenant_id,
        currency="USD",
        balance_usd=f"{micro_usd_to_usd(transaction.balance_after_micro_usd):.4f}",
    )
