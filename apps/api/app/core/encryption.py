from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class SecretCipher:
    def __init__(self) -> None:
        key = get_settings().encryption_key
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
