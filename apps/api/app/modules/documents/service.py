from __future__ import annotations

import io

from pypdf import PdfReader

from app.core.config import get_settings
from app.db.models.entities import Asset
from app.modules.storage.service import local_path, s3_client

settings = get_settings()


def asset_bytes(asset: Asset) -> bytes:
    client = s3_client()
    if client:
        response = client.get_object(Bucket=settings.s3_bucket, Key=asset.storage_key)
        return response["Body"].read(settings.max_upload_bytes + 1)
    path = local_path(asset.storage_key)
    if not path.exists():
        raise FileNotFoundError("Stored asset is unavailable.")
    return path.read_bytes()


def extract_text(asset: Asset) -> str:
    data = asset_bytes(asset)
    if len(data) > settings.max_upload_bytes:
        raise ValueError("Stored document exceeds the configured extraction limit.")
    if asset.mime_type == "text/plain":
        return data.decode("utf-8", errors="replace")
    if asset.mime_type == "application/pdf":
        reader = PdfReader(io.BytesIO(data))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
        return "\n\n".join(page for page in pages if page)
    raise ValueError("Only plain-text and PDF assets can be extracted.")
