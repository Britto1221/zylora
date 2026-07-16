from __future__ import annotations

import hashlib
import json
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.entities import NotificationJob
from app.db.models.enums import NotificationStatus
from app.db.session import get_db
from app.modules.payments.service import record_captured_payment, verify_razorpay_signature
from app.modules.webhooks.service import mark_processed, register_webhook_event, verify_hmac_sha256

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()


@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(default=""),
    x_razorpay_event_id: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict:
    body = await request.body()
    if not verify_razorpay_signature(body, x_razorpay_signature):
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
            payment = payload["payload"]["payment"]["entity"]
            notes = payment.get("notes") or {}
            record_captured_payment(
                db,
                tenant_id=UUID(str(notes["tenant_id"])),
                provider_payment_id=str(payment["id"]),
                provider_order_id=payment.get("order_id"),
                charged_amount_minor=int(payment["amount"]),
                charged_currency=str(payment["currency"]),
                usd_credit_micro_amount=int(notes["usd_credit_micro_amount"]),
                event_id=event_id,
                metadata={"email": payment.get("email"), "contact": payment.get("contact")},
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
    request: Request,
    x_hub_signature_256: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict:
    body = await request.body()
    if not verify_hmac_sha256(
        body=body, signature=x_hub_signature_256, secret=settings.whatsapp_app_secret
    ):
        raise HTTPException(status_code=401, detail="Invalid WhatsApp signature.")
    payload = json.loads(body)
    changes = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            changes.append(change)
    status_records = []
    for change in changes:
        statuses = (change.get("value") or {}).get("statuses") or []
        status_records.extend(statuses)
    event_id = (
        str(status_records[0].get("id")) + ":" + str(status_records[0].get("timestamp"))
        if status_records
        else request.headers.get("x-request-id", hashlib.sha256(body).hexdigest())
    )
    event, created = register_webhook_event(
        db, provider="whatsapp", event_id=event_id, event_type="message_status", body=body
    )
    if not created:
        db.rollback()
        return {"status": "duplicate"}

    for record in status_records:
        provider_id = str(record.get("id", ""))
        job = db.scalar(
            select(NotificationJob).where(NotificationJob.provider_message_id == provider_id)
        )
        if not job:
            continue
        provider_status = str(record.get("status", "")).lower()
        mapping = {
            "sent": NotificationStatus.SUBMITTED,
            "delivered": NotificationStatus.DELIVERED,
            "read": NotificationStatus.READ,
            "failed": NotificationStatus.FAILED,
        }
        if provider_status in mapping:
            job.status = mapping[provider_status]
        if provider_status in {"delivered", "read"}:
            job.delivered_at = datetime.utcnow()
        if provider_status == "failed":
            errors = record.get("errors") or []
            job.failure_reason = json.dumps(errors)[:2000]
    mark_processed(event)
    db.commit()
    return {"status": "processed", "updates": len(status_records)}
