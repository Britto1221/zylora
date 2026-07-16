from __future__ import annotations

import hashlib
import hmac
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.entities import Payment
from app.db.models.enums import CreditTransactionType
from app.modules.credits.service import append_transaction

settings = get_settings()


def verify_razorpay_signature(body: bytes, signature: str) -> bool:
    if not settings.razorpay_webhook_secret:
        return False
    expected = hmac.new(
        settings.razorpay_webhook_secret.encode(), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def create_order(*, amount_minor: int, currency: str, receipt: str, notes: dict) -> dict:
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        if settings.is_production:
            raise RuntimeError("Razorpay is not configured.")
        return {
            "id": f"order_development_{receipt}",
            "amount": amount_minor,
            "currency": currency,
            "receipt": receipt,
            "notes": notes,
            "simulated": True,
        }
    response = httpx.post(
        "https://api.razorpay.com/v1/orders",
        auth=(settings.razorpay_key_id, settings.razorpay_key_secret),
        json={
            "amount": amount_minor,
            "currency": currency,
            "receipt": receipt,
            "notes": notes,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def record_captured_payment(
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
    if existing:
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
    )
    return payment
