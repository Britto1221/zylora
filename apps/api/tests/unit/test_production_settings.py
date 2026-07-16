import pytest

from app.core.config import Settings


def test_production_requires_auth_configuration() -> None:
    settings = Settings(
        environment="production",
        encryption_key="valid-placeholder",
        auth_issuer="",
        auth_jwks_url="",
    )
    with pytest.raises(RuntimeError):
        settings.validate_production()
