from functools import lru_cache

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
    auth_algorithms: str = "RS256"
    super_admin_emails: str = "admin@zylora.dev"
    dev_auth_secret: str = "zylora-development-secret-change-me"
    dev_admin_password: str = "zylora-admin"

    encryption_key: str = ""
    internal_worker_token: str = "zylora-worker-development-token"

    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""

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
    storage_local_path: str = "./storage"
    max_upload_bytes: int = 10_000_000

    email_provider: str = "console"
    email_from: str = "notifications@zylora.local"
    resend_api_key: str = ""

    sentry_dsn: str = ""
    log_level: str = "INFO"
    trusted_hosts: str = "localhost,127.0.0.1,testserver"

    model_config = SettingsConfigDict(
        env_file=("../../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def auth_algorithm_list(self) -> list[str]:
        return [value.strip() for value in self.auth_algorithms.split(",") if value.strip()]

    @property
    def super_admin_email_set(self) -> set[str]:
        return {
            value.strip().lower()
            for value in self.super_admin_emails.split(",")
            if value.strip()
        }

    @property
    def trusted_host_list(self) -> list[str]:
        return [value.strip() for value in self.trusted_hosts.split(",") if value.strip()]

    @field_validator("encryption_key")
    @classmethod
    def validate_encryption_key(cls, value: str, info) -> str:
        environment = str(info.data.get("environment", "development")).lower()
        if environment == "production" and not value:
            raise ValueError("ENCRYPTION_KEY is required in production.")
        return value

    def validate_production(self) -> None:
        if not self.is_production:
            return
        required = {
            "AUTH_ISSUER": self.auth_issuer,
            "AUTH_JWKS_URL": self.auth_jwks_url,
            "AUTH_AUDIENCE": self.auth_audience,
            "DATABASE_URL": self.database_url,
            "REDIS_URL": self.redis_url,
            "WEB_ORIGIN": self.web_origin,
            "ENCRYPTION_KEY": self.encryption_key,
            "INTERNAL_WORKER_TOKEN": self.internal_worker_token,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(
                f"Missing required production settings: {', '.join(sorted(missing))}"
            )
        if self.database_url.startswith("sqlite"):
            raise RuntimeError("SQLite must not be used in production.")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production()
    return settings
