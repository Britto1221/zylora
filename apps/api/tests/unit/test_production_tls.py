import pytest

from app.core.config import Settings


def base() -> dict:
    return dict(
        environment="production",
        auth_issuer="https://idp/",
        auth_jwks_url="https://idp/jwks",
        auth_client_id="client",
        auth_authorization_url="https://idp/authorize",
        auth_token_url="https://idp/token",
        super_admin_emails="owner@company.in",
        redis_url="rediss://redis/0",
        web_origin="https://app.example.in",
        encryption_key="key",
        internal_worker_token="worker",
        razorpay_key_id="id",
        razorpay_key_secret="secret",
        razorpay_webhook_secret="webhook",
        whatsapp_access_token="wa",
        whatsapp_phone_number_id="phone",
        whatsapp_verify_token="verify",
        whatsapp_app_secret="app",
        sentry_dsn="https://sentry",
        legal_contact_email="legal@company.in",
        legal_business_address="India",
        malware_scan_provider="clamav",
    )


def test_production_rejects_postgres_without_tls() -> None:
    values = base()
    values["database_url"] = "postgresql+psycopg://u:p@db/zylora"
    settings = Settings(**values)
    with pytest.raises(RuntimeError, match="sslmode"):
        settings.validate_production()
