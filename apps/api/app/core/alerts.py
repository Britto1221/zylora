from __future__ import annotations

import httpx

from app.core.config import get_settings

settings = get_settings()


def send_operational_alert(
    *, title: str, message: str, severity: str = "error", metadata: dict | None = None
) -> None:
    if not settings.alert_webhook_url:
        return
    try:
        httpx.post(
            settings.alert_webhook_url,
            json={
                "title": title,
                "message": message[:2000],
                "severity": severity,
                "metadata": metadata or {},
                "environment": settings.environment,
            },
            timeout=5,
        )
    except Exception:
        # Alert delivery must never recursively crash the API.
        return
