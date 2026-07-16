import hashlib
import hmac

from app.modules.webhooks.service import verify_hmac_sha256


def test_hmac_signature_verification() -> None:
    body = b'{"event":"test"}'
    secret = "secret"
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    assert verify_hmac_sha256(body=body, signature=signature, secret=secret)
    assert not verify_hmac_sha256(body=body, signature="bad", secret=secret)
