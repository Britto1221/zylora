from __future__ import annotations

import hashlib
import hmac
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.entities import WebhookEvent


def verify_hmac_sha256(*, body: bytes, signature: str, secret: str) -> bool:
    if not signature or not secret:
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.removeprefix("sha256="))


def register_webhook_event(
    db: Session,
    *,
    provider: str,
    event_id: str,
    event_type: str,
    body: bytes,
) -> tuple[WebhookEvent, bool]:
    existing = db.scalar(
        select(WebhookEvent).where(
            WebhookEvent.provider == provider, WebhookEvent.event_id == event_id
        )
    )
    if existing:
        return existing, False
    event = WebhookEvent(
        provider=provider,
        event_id=event_id,
        event_type=event_type,
        payload_hash=hashlib.sha256(body).hexdigest(),
    )
    db.add(event)
    db.flush()
    return event, True


def mark_processed(event: WebhookEvent, error: str | None = None) -> None:
    event.processed = error is None
    event.processing_error = error
    event.processed_at = datetime.utcnow()
