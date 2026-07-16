from __future__ import annotations

import json

import httpx

from app.core.config import get_settings

settings = get_settings()


def generate_answer(*, system: str, prompt: str) -> str | None:
    if not settings.openai_api_key:
        return None
    response = httpx.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4.1-mini",
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system}]},
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
            ],
            "temperature": 0.2,
            "max_output_tokens": 500,
        },
        timeout=45,
    )
    response.raise_for_status()
    payload = response.json()
    chunks: list[str] = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                chunks.append(content.get("text", ""))
    return "\n".join(chunks).strip() or None
