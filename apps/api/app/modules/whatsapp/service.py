from __future__ import annotations

import re

import httpx

from app.core.config import get_settings

settings = get_settings()


class WhatsAppConfigurationError(RuntimeError):
    pass


def configured() -> bool:
    return bool(settings.whatsapp_access_token and settings.whatsapp_phone_number_id)


def normalize_recipient(recipient: str) -> str:
    normalized = re.sub(r"\D", "", recipient)
    if not 8 <= len(normalized) <= 15:
        raise ValueError("Recipient must be a valid international phone number.")
    return normalized


def send_template(
    *, recipient: str, template_name: str, language: str, variables: dict, idempotency_key: str
) -> dict:
    recipient = normalize_recipient(recipient)
    if not re.fullmatch(r"[a-z0-9_]{1,512}", template_name):
        raise ValueError("Invalid WhatsApp template name.")
    if not configured():
        if settings.is_production:
            raise WhatsAppConfigurationError("WhatsApp Cloud API is not configured.")
        return {"id": f"development-{idempotency_key}", "status": "accepted", "simulated": True}
    values = [str(value)[:1024] for value in variables.values() if str(value)]
    components = (
        [{"type": "body", "parameters": [{"type": "text", "text": value} for value in values]}]
        if values
        else []
    )
    response = httpx.post(
        f"https://graph.facebook.com/{settings.whatsapp_api_version}/{settings.whatsapp_phone_number_id}/messages",
        headers={
            "Authorization": f"Bearer {settings.whatsapp_access_token}",
            "Content-Type": "application/json",
        },
        json={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
                "components": components,
            },
        },
        timeout=20,
    )
    response.raise_for_status()
    messages = response.json().get("messages") or []
    if not messages:
        raise RuntimeError("WhatsApp accepted no message.")
    return {"id": messages[0]["id"], "status": "accepted", "simulated": False}
