from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.entities import CreditAccount, CreditReservation, CreditTransaction
from app.db.models.enums import CreditTransactionType

MICRO_USD = Decimal("1000000")


class InsufficientCreditsError(ValueError):
    pass


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
    try:
        db.flush()
        return account
    except IntegrityError:
        db.rollback()
        account = db.scalar(
            select(CreditAccount).where(
                CreditAccount.tenant_id == tenant_id,
                CreditAccount.currency == "USD",
            )
        )
        if not account:
            raise
        return account


def lock_account(db: Session, tenant_id: UUID) -> CreditAccount:
    account = get_or_create_account(db, tenant_id)
    locked = db.scalar(
        select(CreditAccount).where(CreditAccount.id == account.id).with_for_update()
    )
    if not locked:
        raise RuntimeError("Credit account not found.")
    return locked


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
    if existing:
        return existing

    account = lock_account(db, tenant_id)
    new_balance = account.balance_micro_usd + amount_micro_usd
    if new_balance < account.reserved_micro_usd:
        raise InsufficientCreditsError("Insufficient available WhatsApp credits.")

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


def reserve_credits(
    db: Session,
    *,
    tenant_id: UUID,
    amount_micro_usd: int,
    idempotency_key: str,
    reference_type: str,
    reference_id: UUID,
) -> CreditReservation:
    existing = db.scalar(
        select(CreditReservation).where(CreditReservation.idempotency_key == idempotency_key)
    )
    if existing:
        return existing

    account = lock_account(db, tenant_id)
    available = account.balance_micro_usd - account.reserved_micro_usd
    if available < amount_micro_usd:
        raise InsufficientCreditsError("Insufficient available WhatsApp credits.")

    account.reserved_micro_usd += amount_micro_usd
    reservation = CreditReservation(
        tenant_id=tenant_id,
        credit_account_id=account.id,
        amount_micro_usd=amount_micro_usd,
        idempotency_key=idempotency_key,
        status="ACTIVE",
        expires_at=datetime.utcnow() + timedelta(minutes=20),
        reference_type=reference_type,
        reference_id=reference_id,
    )
    db.add(reservation)
    db.flush()
    return reservation


def capture_reservation(
    db: Session,
    *,
    reservation: CreditReservation,
    description: str,
    external_reference: str | None = None,
) -> CreditTransaction:
    if reservation.status == "CAPTURED":
        existing = db.scalar(
            select(CreditTransaction).where(
                CreditTransaction.idempotency_key == f"capture:{reservation.idempotency_key}"
            )
        )
        if not existing:
            raise RuntimeError("Captured reservation has no transaction.")
        return existing

    account = db.scalar(
        select(CreditAccount)
        .where(CreditAccount.id == reservation.credit_account_id)
        .with_for_update()
    )
    if not account:
        raise RuntimeError("Credit account not found.")
    account.reserved_micro_usd = max(0, account.reserved_micro_usd - reservation.amount_micro_usd)
    reservation.status = "CAPTURED"
    return append_transaction(
        db,
        tenant_id=reservation.tenant_id,
        transaction_type=CreditTransactionType.DEDUCTION,
        amount_micro_usd=-reservation.amount_micro_usd,
        description=description,
        external_reference=external_reference,
        idempotency_key=f"capture:{reservation.idempotency_key}",
        metadata_json={"reservation_id": str(reservation.id)},
    )


def release_reservation(db: Session, reservation: CreditReservation, *, reason: str) -> None:
    if reservation.status != "ACTIVE":
        return
    account = db.scalar(
        select(CreditAccount)
        .where(CreditAccount.id == reservation.credit_account_id)
        .with_for_update()
    )
    if account:
        account.reserved_micro_usd = max(0, account.reserved_micro_usd - reservation.amount_micro_usd)
    reservation.status = "RELEASED"
