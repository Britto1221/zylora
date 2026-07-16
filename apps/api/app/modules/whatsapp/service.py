from __future__ import annotations

import httpx

from app.core.config import get_settings

settings = get_settings()


class WhatsAppConfigurationError(RuntimeError):
    pass


def configured() -> bool:
    return bool(settings.whatsapp_access_token and settings.whatsapp_phone_number_id)


def send_template(
    *,
    recipient: str,
    template_name: str,
    language: str,
    variables: dict,
    idempotency_key: str,
) -> dict:
    if not configured():
        if settings.is_production:
            raise WhatsAppConfigurationError("WhatsApp Cloud API is not configured.")
        return {
            "id": f"development-{idempotency_key}",
            "status": "accepted",
            "simulated": True,
        }

    components = []
    values = [str(value) for value in variables.values() if str(value)]
    if values:
        components.append(
            {
                "type": "body",
                "parameters": [{"type": "text", "text": value} for value in values],
            }
        )

    url = (
        f"https://graph.facebook.com/{settings.whatsapp_api_version}/"
        f"{settings.whatsapp_phone_number_id}/messages"
    )
    response = httpx.post(
        url,
        headers={
            "Authorization": f"Bearer {settings.whatsapp_access_token}",
            "Content-Type": "application/json",
        },
        json={
            "messaging_product": "whatsapp",
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
    payload = response.json()
    messages = payload.get("messages") or []
    if not messages:
        raise RuntimeError("WhatsApp accepted no message.")
    return {"id": messages[0]["id"], "status": "accepted", "simulated": False}
