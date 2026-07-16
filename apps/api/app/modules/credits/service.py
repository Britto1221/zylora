from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import InsufficientCreditsError
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
    if account is not None:
        return account

    account = CreditAccount(tenant_id=tenant_id, currency="USD")
    db.add(account)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        account = db.scalar(
            select(CreditAccount).where(
                CreditAccount.tenant_id == tenant_id,
                CreditAccount.currency == "USD",
            )
        )
        if account is None:
            raise
    return account


def append_transaction(
    db: Session,
    *,
    tenant_id: UUID,
    transaction_type: CreditTransactionType,
    amount_micro_usd: int,
    description: str,
    idempotency_key: str,
    external_reference: str | None = None,
    metadata_json: dict | None = None,
) -> CreditTransaction:
    existing = db.scalar(
        select(CreditTransaction).where(
            CreditTransaction.tenant_id == tenant_id,
            CreditTransaction.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        return existing

    account = get_or_create_account(db, tenant_id)
    account = db.scalar(
        select(CreditAccount)
        .where(CreditAccount.id == account.id)
        .with_for_update()
    )
    if account is None:
        raise RuntimeError("Credit account disappeared during transaction.")

    new_balance = account.balance_micro_usd + amount_micro_usd
    if new_balance < 0:
        raise InsufficientCreditsError("Insufficient WhatsApp credits.")

    account.balance_micro_usd = new_balance
    transaction = CreditTransaction(
        tenant_id=tenant_id,
        credit_account_id=account.id,
        type=transaction_type,
        amount_micro_usd=amount_micro_usd,
        balance_after_micro_usd=new_balance,
        description=description,
        external_reference=external_reference,
        idempotency_key=idempotency_key,
        metadata_json=metadata_json or {},
    )
    db.add(transaction)
    db.flush()
    return transaction
