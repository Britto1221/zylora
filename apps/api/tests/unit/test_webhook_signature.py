import hashlib
import hmac

from app.modules.webhooks.service import verify_hmac_sha256


def test_valid_hmac_signature() -> None:
    body = b'{"event":"payment.captured"}'
    secret = "test-secret"
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    assert verify_hmac_sha256(
        body=body,
        signature=signature,
        secret=secret,
    )


def test_invalid_hmac_signature() -> None:
    assert not verify_hmac_sha256(
        body=b"payload",
        signature="bad-signature",
        secret="test-secret",
    )
