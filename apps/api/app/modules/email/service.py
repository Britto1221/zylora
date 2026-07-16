from __future__ import annotations

import httpx

from app.core.config import get_settings

settings = get_settings()


def send_email(*, to: str, subject: str, text: str, idempotency_key: str) -> dict:
    if settings.email_provider == "console" and not settings.is_production:
        return {
            "id": f"console:{idempotency_key}",
            "to": to,
            "subject": subject,
            "simulated": True,
        }
    if settings.email_provider == "resend" and settings.resend_api_key:
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "Content-Type": "application/json",
                "Idempotency-Key": idempotency_key,
            },
            json={
                "from": settings.email_from,
                "to": [to],
                "subject": subject,
                "text": text,
            },
            timeout=20,
        )
        response.raise_for_status()
        return {**response.json(), "simulated": False}
    raise RuntimeError("A production email provider is not configured.")
