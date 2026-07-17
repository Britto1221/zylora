from functools import lru_cache
from urllib.parse import parse_qs, urlparse

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    app_name: str = "Zylora"
    database_url: str = "sqlite:///./zylora-dev.db"
    redis_url: str = "redis://localhost:6379/0"
    web_origin: str = "http://localhost:3000"
    public_api_url: str = "http://localhost:8000/api/v1"

    auth_issuer: str = ""
    auth_audience: str = "zylora-api"
    auth_jwks_url: str = ""
    auth_client_id: str = ""
    auth_client_secret: str = ""
    auth_authorization_url: str = ""
    auth_token_url: str = ""
    auth_end_session_url: str = ""
    auth_redirect_uri: str = "http://localhost:3000/api/auth/callback"
    auth_algorithms: str = "RS256"
    super_admin_emails: str = "admin@zylora.dev"
    dev_auth_secret: str = "zylora-development-secret-change-me"
    dev_admin_password: str = "zylora-admin"

    encryption_key: str = ""
    internal_worker_token: str = "zylora-worker-development-token"

    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""
    payment_currency: str = "INR"
    usd_inr_rate: str = "84.00"

    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = ""
    whatsapp_app_secret: str = ""
    whatsapp_api_version: str = "v21.0"

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""

    s3_endpoint: str = ""
    s3_region: str = ""
    s3_bucket: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_server_side_encryption: str = "AES256"
    s3_malware_scan_tag_key: str = "GuardDutyMalwareScanStatus"
    storage_local_path: str = "./storage"
    max_upload_bytes: int = 10_000_000
    malware_scan_provider: str = "none"
    clamav_host: str = "localhost"
    clamav_port: int = 3310

    email_provider: str = "console"
    email_from: str = "notifications@zylora.local"
    resend_api_key: str = ""

    sentry_dsn: str = ""
    alert_webhook_url: str = ""
    log_level: str = "INFO"
    trusted_hosts: str = "localhost,127.0.0.1,testserver"

    legal_entity_name: str = "Zylora"
    legal_contact_email: str = ""
    legal_business_address: str = ""
    legal_jurisdiction: str = "India"
    refund_window_days: int = 7

    model_config = SettingsConfigDict(
        env_file=("../../.env", ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def auth_algorithm_list(self) -> list[str]:
        return [v.strip() for v in self.auth_algorithms.split(",") if v.strip()]

    @property
    def super_admin_email_set(self) -> set[str]:
        return {v.strip().lower() for v in self.super_admin_emails.split(",") if v.strip()}

    @property
    def trusted_host_list(self) -> list[str]:
        return [v.strip() for v in self.trusted_hosts.split(",") if v.strip()]

    @field_validator("encryption_key")
    @classmethod
    def validate_encryption_key(cls, value: str, info) -> str:
        if str(info.data.get("environment", "development")).lower() == "production" and not value:
            raise ValueError("ENCRYPTION_KEY is required in production.")
        return value

    def validate_production(self) -> None:
        if not self.is_production:
            return
        required = {
            "AUTH_ISSUER": self.auth_issuer,
            "AUTH_JWKS_URL": self.auth_jwks_url,
            "AUTH_CLIENT_ID": self.auth_client_id,
            "AUTH_AUTHORIZATION_URL": self.auth_authorization_url,
            "AUTH_TOKEN_URL": self.auth_token_url,
            "SUPER_ADMIN_EMAILS": self.super_admin_emails,
            "DATABASE_URL": self.database_url,
            "REDIS_URL": self.redis_url,
            "WEB_ORIGIN": self.web_origin,
            "ENCRYPTION_KEY": self.encryption_key,
            "INTERNAL_WORKER_TOKEN": self.internal_worker_token,
            "RAZORPAY_KEY_ID": self.razorpay_key_id,
            "RAZORPAY_KEY_SECRET": self.razorpay_key_secret,
            "RAZORPAY_WEBHOOK_SECRET": self.razorpay_webhook_secret,
            "WHATSAPP_ACCESS_TOKEN": self.whatsapp_access_token,
            "WHATSAPP_PHONE_NUMBER_ID": self.whatsapp_phone_number_id,
            "WHATSAPP_VERIFY_TOKEN": self.whatsapp_verify_token,
            "WHATSAPP_APP_SECRET": self.whatsapp_app_secret,
            "SENTRY_DSN": self.sentry_dsn,
            "LEGAL_CONTACT_EMAIL": self.legal_contact_email,
            "LEGAL_BUSINESS_ADDRESS": self.legal_business_address,
        }
        missing = sorted(name for name, value in required.items() if not value)
        if missing:
            raise RuntimeError(f"Missing required production settings: {', '.join(missing)}")
        if self.database_url.startswith("sqlite"):
            raise RuntimeError("SQLite must not be used in production.")
        parsed = urlparse(self.database_url.replace("postgresql+psycopg", "postgresql", 1))
        if parsed.scheme not in {"postgresql", "postgres"}:
            raise RuntimeError("Production DATABASE_URL must use PostgreSQL.")
        sslmode = parse_qs(parsed.query).get("sslmode", [""])[0]
        if sslmode not in {"require", "verify-ca", "verify-full"}:
            raise RuntimeError(
                "Production PostgreSQL must use sslmode=require, verify-ca, or verify-full."
            )
        if not self.redis_url.startswith("rediss://"):
            raise RuntimeError("Production Redis must use TLS (rediss://).")
        if not self.super_admin_email_set or any(
            email.endswith("@example.com") for email in self.super_admin_email_set
        ):
            raise RuntimeError(
                "SUPER_ADMIN_EMAILS must contain real verified administrator email addresses."
            )
        if self.malware_scan_provider.lower() not in {"clamav", "guardduty"}:
            raise RuntimeError("Production malware scanning must use clamav or guardduty.")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production()
    return settings
