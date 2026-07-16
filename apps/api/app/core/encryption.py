from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class SecretCipher:
    def __init__(self) -> None:
        settings = get_settings()
        key = settings.encryption_key
        if not key and not settings.is_production:
            digest = hashlib.sha256(settings.dev_auth_secret.encode()).digest()
            key = base64.urlsafe_b64encode(digest).decode()
        if not key:
            raise RuntimeError("ENCRYPTION_KEY must be configured.")
        self._fernet = Fernet(key.encode())

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken as exc:
            raise RuntimeError("Unable to decrypt stored secret.") from exc


def mask_secret(secret: str) -> str:
    if len(secret) <= 4:
        return "••••"
    return f"••••••••{secret[-4:]}"
