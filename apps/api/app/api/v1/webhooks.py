from __future__ import annotations

import hashlib
import json
from datetime import datetime
from uuid import NAMESPACE_DNS, uuid5

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.entities import NotificationJob, Payment
from app.db.models.enums import CreditTransactionType, NotificationStatus
from app.db.session import get_db
from app.modules.credits.service import append_transaction
from app.modules.payments.service import (
    record_captured_invoice_payment,
    record_captured_payment,
    verify_razorpay_webhook_signature,
)
from app.modules.webhooks.service import mark_processed, register_webhook_event, verify_hmac_sha256

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()
webhook_actor_id = uuid5(NAMESPACE_DNS, "zylora-razorpay-webhook")


@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(default=""),
    x_razorpay_event_id: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict:
    body = await request.body()
    if not verify_razorpay_webhook_signature(body, x_razorpay_signature):
        raise HTTPException(status_code=401, detail="Invalid Razorpay signature.")
    payload = json.loads(body)
    event_type = str(payload.get("event", "unknown"))
    event_id = x_razorpay_event_id or str(payload.get("event_id", ""))
    if not event_id:
        raise HTTPException(status_code=400, detail="Event ID is required.")
    event, created = register_webhook_event(
        db, provider="razorpay", event_id=event_id, event_type=event_type, body=body
    )
    if not created:
        db.rollback()
        return {"status": "duplicate"}
    try:
        if event_type in {"payment.captured", "order.paid"}:
            provider_payment = payload["payload"]["payment"]["entity"]
            order_id = provider_payment.get("order_id")
            stored = db.scalar(
                select(Payment).where(
                    Payment.provider == "razorpay",
                    Payment.provider_order_id == order_id,
                )
            )
            if stored is None:
                raise ValueError("Payment does not match a server-created Razorpay order.")
            common = {
                "provider_payment_id": str(provider_payment["id"]),
                "provider_order_id": order_id,
                "charged_amount_minor": int(provider_payment["amount"]),
                "charged_currency": str(provider_payment["currency"]),
                "event_id": event_id,
                "metadata": {
                    "email": provider_payment.get("email"),
                    "contact": provider_payment.get("contact"),
                },
            }
            if stored.purpose == "recurring_invoice":
                record_captured_invoice_payment(
                    db,
                    actor_user_id=webhook_actor_id,
                    **common,
                )
            else:
                record_captured_payment(
                    db,
                    tenant_id=stored.tenant_id,
                    usd_credit_micro_amount=stored.usd_credit_micro_amount,
                    **common,
                )
        mark_processed(event)
        db.commit()
    except Exception as exc:
        mark_processed(event, str(exc))
        db.commit()
        raise HTTPException(status_code=400, detail="Webhook processing failed.") from exc
    return {"status": "processed"}


@router.get("/whatsapp")
def verify_whatsapp(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> Response:
    if hub_mode != "subscribe" or hub_verify_token != settings.whatsapp_verify_token:
        raise HTTPException(status_code=403, detail="WhatsApp verification failed.")
    return Response(content=hub_challenge, media_type="text/plain")


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request, x_hub_signature_256: str = Header(default=""), db: Session = Depends(get_db)
) -> dict:
    body = await request.body()
    if not verify_hmac_sha256(
        body=body, signature=x_hub_signature_256, secret=settings.whatsapp_app_secret
    ):
        raise HTTPException(status_code=401, detail="Invalid WhatsApp signature.")
    payload = json.loads(body)
    statuses: list[dict[str, object]] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            statuses.extend((change.get("value") or {}).get("statuses") or [])
    event_id = (
        f"{statuses[0].get('id')}:{statuses[0].get('timestamp')}"
        if statuses
        else request.headers.get("x-request-id", hashlib.sha256(body).hexdigest())
    )
    event, created = register_webhook_event(
        db, provider="whatsapp", event_id=event_id, event_type="message_status", body=body
    )
    if not created:
        db.rollback()
        return {"status": "duplicate"}
    for record in statuses:
        provider_id = str(record.get("id", ""))
        job = db.scalar(
            select(NotificationJob)
            .where(NotificationJob.provider_message_id == provider_id)
            .with_for_update()
        )
        if not job:
            continue
        provider_status = str(record.get("status", "")).lower()
        try:
            occurred_at = datetime.utcfromtimestamp(int(str(record.get("timestamp", "0"))))
        except (TypeError, ValueError):
            occurred_at = datetime.utcnow()
        job.provider_status = provider_status
        job.provider_timestamp = occurred_at
        if provider_status == "sent":
            job.status = NotificationStatus.SUBMITTED
            job.submitted_at = job.submitted_at or occurred_at
        elif provider_status == "delivered":
            job.status = NotificationStatus.DELIVERED
            job.delivered_at = occurred_at
        elif provider_status == "read":
            job.status = NotificationStatus.READ
            job.delivered_at = job.delivered_at or occurred_at
            job.read_at = occurred_at
        elif provider_status == "failed":
            errors = record.get("errors") or []
            job.failure_reason = json.dumps(errors)[:2000]
            if job.charge_micro_usd > 0:
                append_transaction(
                    db,
                    tenant_id=job.tenant_id,
                    transaction_type=CreditTransactionType.REFUND,
                    amount_micro_usd=job.charge_micro_usd,
                    description="Refund for failed WhatsApp notification",
                    external_reference=provider_id,
                    idempotency_key=f"notification-refund:{job.id}",
                    metadata_json={"errors": errors},
                )
                job.status = NotificationStatus.REFUNDED
                job.refunded_at = occurred_at
            else:
                job.status = NotificationStatus.FAILED
    mark_processed(event)
    db.commit()
    return {"status": "processed", "updates": len(statuses)}
