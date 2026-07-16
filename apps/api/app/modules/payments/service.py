from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.entities import Payment
from app.db.models.enums import CreditTransactionType
from app.modules.credits.service import append_transaction


def capture_razorpay_credit_payment(
    db: Session,
    *,
    tenant_id: UUID,
    provider_payment_id: str,
    provider_order_id: str | None,
    charged_amount_minor: int,
    charged_currency: str,
    usd_credit_micro_amount: int,
    event_id: str,
    metadata: dict,
) -> Payment:
    existing = db.scalar(
        select(Payment).where(
            Payment.provider == "razorpay",
            Payment.provider_payment_id == provider_payment_id,
        )
    )
    if existing is not None:
        return existing

    payment = Payment(
        tenant_id=tenant_id,
        provider="razorpay",
        provider_payment_id=provider_payment_id,
        provider_order_id=provider_order_id,
        charged_amount_minor=charged_amount_minor,
        charged_currency=charged_currency,
        usd_credit_micro_amount=usd_credit_micro_amount,
        status="CAPTURED",
        metadata_json=metadata,
    )
    db.add(payment)
    db.flush()

    append_transaction(
        db,
        tenant_id=tenant_id,
        transaction_type=CreditTransactionType.PURCHASE,
        amount_micro_usd=usd_credit_micro_amount,
        description="Verified Razorpay credit purchase",
        external_reference=provider_payment_id,
        idempotency_key=f"razorpay:{event_id}:{provider_payment_id}",
        metadata_json={"provider": "razorpay", "order_id": provider_order_id},
    )
    return payment
