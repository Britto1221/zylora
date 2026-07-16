from __future__ import annotations

import httpx

from app.config import get_settings

settings = get_settings()


def internal_request(method: str, path: str, *, params: dict | None = None) -> dict:
    response = httpx.request(
        method,
        f"{settings.api_url}/internal{path}",
        headers={"X-Worker-Token": settings.internal_worker_token},
        params=params,
        timeout=60,
    )
    response.raise_for_status()
    if response.status_code == 204:
        return {}
    return response.json()
