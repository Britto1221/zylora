from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.modules.payments.service import capture_razorpay_credit_payment
from app.modules.webhooks.service import (
    mark_processed,
    register_webhook_event,
    verify_hmac_sha256,
)

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
    if not verify_hmac_sha256(
        body=body,
        signature=x_razorpay_signature,
        secret=settings.razorpay_webhook_secret,
    ):
        raise HTTPException(status_code=401, detail="Invalid Razorpay signature.")

    payload = json.loads(body)
    event_type = str(payload.get("event", "unknown"))
    event_id = x_razorpay_event_id or str(payload.get("event_id", ""))
    if not event_id:
        raise HTTPException(status_code=400, detail="Webhook event ID is required.")

    event, is_new = register_webhook_event(
        db,
        provider="razorpay",
        event_id=event_id,
        event_type=event_type,
        body=body,
    )
    if not is_new:
        db.rollback()
        return {"status": "duplicate"}

    try:
        if event_type in {"payment.captured", "order.paid"}:
            payment_entity = payload["payload"]["payment"]["entity"]
            notes = payment_entity.get("notes") or {}

            capture_razorpay_credit_payment(
                db,
                tenant_id=UUID(str(notes["tenant_id"])),
                provider_payment_id=str(payment_entity["id"]),
                provider_order_id=payment_entity.get("order_id"),
                charged_amount_minor=int(payment_entity["amount"]),
                charged_currency=str(payment_entity["currency"]),
                usd_credit_micro_amount=int(notes["usd_credit_micro_amount"]),
                event_id=event_id,
                metadata={"email": payment_entity.get("email")},
            )

        mark_processed(event)
        db.commit()
    except Exception as exc:
        mark_processed(event, error=str(exc))
        db.commit()
        raise HTTPException(status_code=400, detail="Webhook processing failed.") from exc

    return {"status": "processed"}


@router.get("/whatsapp")
def verify_whatsapp_webhook(
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
        body=body,
        signature=x_hub_signature_256,
        secret=settings.whatsapp_app_secret,
    ):
        raise HTTPException(status_code=401, detail="Invalid WhatsApp signature.")

    payload = json.loads(body)
    event_id = str(payload.get("id") or request.headers.get("x-request-id") or "")
    event, is_new = register_webhook_event(
        db,
        provider="whatsapp",
        event_id=event_id,
        event_type="status_update",
        body=body,
    )
    if not is_new:
        db.rollback()
        return {"status": "duplicate"}

    # Map Meta delivery statuses to NotificationJob before launch.
    mark_processed(event)
    db.commit()
    return {"status": "processed"}
