from __future__ import annotations

import hashlib
import hmac
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

import httpx
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.entities import Payment
from app.db.models.enums import CreditTransactionType
from app.modules.credits.service import append_transaction

settings = get_settings()


@dataclass(frozen=True)
class CreditPack:
    id: str
    credit_usd: Decimal
    label: str

    @property
    def micro_usd(self) -> int:
        return int(self.credit_usd * Decimal("1000000"))


CREDIT_PACKS = (
    CreditPack("mini", Decimal("10.00"), "$10 messaging credits"),
    CreditPack("standard", Decimal("25.00"), "$25 messaging credits"),
    CreditPack("business", Decimal("50.00"), "$50 messaging credits"),
    CreditPack("growth", Decimal("100.00"), "$100 messaging credits"),
)


def pack_by_id(pack_id: str) -> CreditPack:
    for pack in CREDIT_PACKS:
        if pack.id == pack_id:
            return pack
    raise ValueError("Unsupported credit pack.")


def pack_price_minor(pack: CreditPack, currency: str | None = None) -> int:
    selected = (currency or settings.payment_currency).upper()
    if selected == "USD":
        return int((pack.credit_usd * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if selected == "INR":
        return int(
            (pack.credit_usd * Decimal(settings.usd_inr_rate) * 100).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )
    raise ValueError("Unsupported payment currency.")


def public_packs() -> list[dict]:
    currency = settings.payment_currency.upper()
    return [
        {
            **asdict(pack),
            "credit_usd": f"{pack.credit_usd:.2f}",
            "usd_credit_micro_amount": pack.micro_usd,
            "charged_currency": currency,
            "charged_amount_minor": pack_price_minor(pack, currency),
        }
        for pack in CREDIT_PACKS
    ]


def verify_razorpay_webhook_signature(body: bytes, signature: str) -> bool:
    if not settings.razorpay_webhook_secret:
        return False
    expected = hmac.new(settings.razorpay_webhook_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def verify_checkout_signature(*, order_id: str, payment_id: str, signature: str) -> bool:
    if not settings.razorpay_key_secret:
        return False
    expected = hmac.new(
        settings.razorpay_key_secret.encode(), f"{order_id}|{payment_id}".encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def create_provider_order(*, amount_minor: int, currency: str, receipt: str, notes: dict) -> dict:
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        if settings.is_production:
            raise RuntimeError("Razorpay is not configured.")
        return {
            "id": f"order_development_{receipt}",
            "amount": amount_minor,
            "currency": currency,
            "receipt": receipt,
            "notes": notes,
            "status": "created",
            "simulated": True,
        }
    response = httpx.post(
        "https://api.razorpay.com/v1/orders",
        auth=(settings.razorpay_key_id, settings.razorpay_key_secret),
        json={"amount": amount_minor, "currency": currency, "receipt": receipt, "notes": notes},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    payload["simulated"] = False
    return payload


def create_checkout_order(
    db: Session, *, tenant_id: UUID, pack_id: str, receipt: str
) -> tuple[Payment, dict]:
    pack = pack_by_id(pack_id)
    currency = settings.payment_currency.upper()
    amount = pack_price_minor(pack, currency)
    provider_order = create_provider_order(
        amount_minor=amount,
        currency=currency,
        receipt=receipt,
        notes={
            "tenant_id": str(tenant_id),
            "pack_id": pack.id,
            "usd_credit_micro_amount": str(pack.micro_usd),
        },
    )
    order_id = str(provider_order["id"])
    existing = db.scalar(
        select(Payment).where(Payment.provider == "razorpay", Payment.provider_order_id == order_id)
    )
    if existing:
        return existing, provider_order
    payment = Payment(
        tenant_id=tenant_id,
        provider="razorpay",
        provider_payment_id=None,
        provider_order_id=order_id,
        pack_id=pack.id,
        charged_amount_minor=amount,
        charged_currency=currency,
        usd_credit_micro_amount=pack.micro_usd,
        status="ORDER_CREATED",
        metadata_json={"receipt": receipt, "simulated": provider_order.get("simulated", False)},
    )
    db.add(payment)
    db.flush()
    return payment, provider_order


def mark_checkout_verified(
    db: Session,
    *,
    tenant_id: UUID,
    provider_order_id: str,
    provider_payment_id: str,
    signature: str,
) -> Payment:
    if not verify_checkout_signature(
        order_id=provider_order_id, payment_id=provider_payment_id, signature=signature
    ):
        raise ValueError("Invalid Razorpay checkout signature.")
    payment = db.scalar(
        select(Payment).where(
            Payment.tenant_id == tenant_id,
            Payment.provider == "razorpay",
            Payment.provider_order_id == provider_order_id,
        )
    )
    if payment is None:
        raise ValueError("Unknown Razorpay order.")
    if payment.provider_payment_id and payment.provider_payment_id != provider_payment_id:
        raise ValueError("This order is already linked to another payment.")
    payment.provider_payment_id = provider_payment_id
    payment.checkout_verified_at = datetime.utcnow()
    if payment.status != "CAPTURED":
        payment.status = "CHECKOUT_VERIFIED"
    db.flush()
    return payment


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
    payment = db.scalar(
        select(Payment).where(
            Payment.provider == "razorpay",
            or_(
                Payment.provider_payment_id == provider_payment_id,
                Payment.provider_order_id == provider_order_id,
            ),
        )
    )
    if payment is None:
        raise ValueError("Captured payment does not match a server-created order.")
    if (
        payment.tenant_id != tenant_id
        or payment.charged_amount_minor != charged_amount_minor
        or payment.charged_currency.upper() != charged_currency.upper()
        or payment.usd_credit_micro_amount != usd_credit_micro_amount
    ):
        raise ValueError("Captured payment does not match the server-created order.")
    payment.provider_payment_id = provider_payment_id
    payment.status = "CAPTURED"
    payment.captured_at = datetime.utcnow()
    payment.metadata_json = {**(payment.metadata_json or {}), **metadata}
    append_transaction(
        db,
        tenant_id=tenant_id,
        transaction_type=CreditTransactionType.PURCHASE,
        amount_micro_usd=usd_credit_micro_amount,
        description="Verified Razorpay credit purchase",
        external_reference=provider_payment_id,
        idempotency_key=f"razorpay:{event_id}:{provider_payment_id}",
    )
    db.flush()
    return payment


def create_invoice_checkout_order(
    db: Session,
    *,
    tenant_id: UUID,
    invoice_id: UUID,
    receipt: str,
) -> tuple[Payment, dict]:
    from app.db.models.entities import Invoice
    from app.db.models.enums import InvoiceStatus, InvoiceType

    invoice = db.scalar(
        select(Invoice).where(
            Invoice.id == invoice_id,
            Invoice.tenant_id == tenant_id,
            Invoice.invoice_type == InvoiceType.RECURRING,
            Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.OVERDUE]),
        )
    )
    if invoice is None:
        raise ValueError("Unpaid recurring invoice not found.")
    provider_order = create_provider_order(
        amount_minor=invoice.total_minor,
        currency=invoice.currency,
        receipt=receipt,
        notes={
            "tenant_id": str(tenant_id),
            "invoice_id": str(invoice.id),
            "purpose": "recurring_invoice",
        },
    )
    order_id = str(provider_order["id"])
    existing = db.scalar(
        select(Payment).where(
            Payment.provider == "razorpay",
            Payment.provider_order_id == order_id,
        )
    )
    if existing:
        return existing, provider_order
    payment = Payment(
        tenant_id=tenant_id,
        provider="razorpay",
        provider_payment_id=None,
        provider_order_id=order_id,
        pack_id=None,
        invoice_id=invoice.id,
        purpose="recurring_invoice",
        charged_amount_minor=invoice.total_minor,
        charged_currency=invoice.currency,
        usd_credit_micro_amount=0,
        status="ORDER_CREATED",
        metadata_json={
            "receipt": receipt,
            "invoice_number": invoice.number,
            "simulated": provider_order.get("simulated", False),
        },
    )
    db.add(payment)
    db.flush()
    return payment, provider_order


def record_captured_invoice_payment(
    db: Session,
    *,
    provider_payment_id: str,
    provider_order_id: str | None,
    charged_amount_minor: int,
    charged_currency: str,
    event_id: str,
    metadata: dict,
    actor_user_id: UUID,
) -> Payment:
    from app.db.models.entities import Invoice, Tenant
    from app.db.models.enums import InvoiceStatus
    from app.modules.audit.service import record_audit
    from app.modules.billing.service import clear_billing_restriction

    payment = db.scalar(
        select(Payment).where(
            Payment.provider == "razorpay",
            or_(
                Payment.provider_payment_id == provider_payment_id,
                Payment.provider_order_id == provider_order_id,
            ),
            Payment.purpose == "recurring_invoice",
        )
    )
    if payment is None or payment.invoice_id is None:
        raise ValueError("Captured recurring payment does not match a server-created order.")
    if (
        payment.charged_amount_minor != charged_amount_minor
        or payment.charged_currency.upper() != charged_currency.upper()
    ):
        raise ValueError(
            "Captured recurring payment amount or currency does not match the invoice."
        )
    invoice = db.get(Invoice, payment.invoice_id)
    tenant = db.get(Tenant, payment.tenant_id)
    if invoice is None or tenant is None:
        raise ValueError("Recurring invoice or tenant no longer exists.")

    payment.provider_payment_id = provider_payment_id
    payment.status = "CAPTURED"
    payment.captured_at = datetime.utcnow()
    payment.metadata_json = {
        **(payment.metadata_json or {}),
        **metadata,
        "webhook_event_id": event_id,
    }
    invoice.status = InvoiceStatus.PAID
    invoice.paid_at = datetime.utcnow()
    clear_billing_restriction(
        db,
        tenant=tenant,
        actor_user_id=actor_user_id,
        reason="verified_razorpay_recurring_invoice_payment",
        action="billing.lockout_cleared_by_payment",
    )
    record_audit(
        db,
        actor_user_id=actor_user_id,
        tenant_id=tenant.id,
        entity_type="invoice",
        entity_id=invoice.id,
        action="invoice.recurring_paid",
        payload={
            "payment_id": provider_payment_id,
            "order_id": provider_order_id,
            "amount_minor": charged_amount_minor,
            "currency": charged_currency,
        },
    )
    db.flush()
    return payment
