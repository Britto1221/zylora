from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.entities import CreditAccount, CreditTransaction
from app.db.models.enums import CreditTransactionType

MICRO_USD = Decimal("1000000")


def usd_to_micro_usd(amount: Decimal) -> int:
    return int((amount * MICRO_USD).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def micro_usd_to_usd(amount: int) -> Decimal:
    return Decimal(amount) / MICRO_USD


def get_or_create_account(db: Session, tenant_id: UUID) -> CreditAccount:
    account = db.scalar(
        select(CreditAccount).where(
            CreditAccount.tenant_id == tenant_id,
            CreditAccount.currency == "USD",
        )
    )
    if account:
        return account

    account = CreditAccount(tenant_id=tenant_id, currency="USD")
    db.add(account)
    db.flush()
    return account


def append_transaction(
    db: Session,
    *,
    tenant_id: UUID,
    transaction_type: CreditTransactionType,
    amount_micro_usd: int,
    description: str,
    external_reference: str | None = None,
    metadata_json: dict | None = None,
) -> CreditTransaction:
    account = get_or_create_account(db, tenant_id)

    new_balance = account.balance_micro_usd + amount_micro_usd
    if new_balance < 0:
        raise ValueError("Insufficient credits.")

    account.balance_micro_usd = new_balance

    transaction = CreditTransaction(
        tenant_id=tenant_id,
        credit_account_id=account.id,
        type=transaction_type,
        amount_micro_usd=amount_micro_usd,
        balance_after_micro_usd=new_balance,
        description=description,
        external_reference=external_reference,
        metadata_json=metadata_json or {},
    )
    db.add(transaction)
    db.flush()
    return transaction
