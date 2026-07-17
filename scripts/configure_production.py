from __future__ import annotations

import getpass
from pathlib import Path

FIELDS = [
    ("WEB_ORIGIN", "Public application URL"),
    ("PUBLIC_API_URL", "Public API URL including /api/v1"),
    ("DATABASE_URL", "PostgreSQL TLS URL (sslmode=verify-full)"),
    ("REDIS_URL", "Redis TLS URL (rediss://)"),
    ("AUTH_ISSUER", "OIDC issuer"),
    ("AUTH_AUDIENCE", "API audience"),
    ("AUTH_JWKS_URL", "JWKS URL"),
    ("AUTH_CLIENT_ID", "OIDC client ID"),
    ("AUTH_CLIENT_SECRET", "OIDC client secret"),
    ("AUTH_AUTHORIZATION_URL", "OIDC authorization URL"),
    ("AUTH_TOKEN_URL", "OIDC token URL"),
    ("AUTH_REDIRECT_URI", "OIDC callback URL"),
    ("SUPER_ADMIN_EMAILS", "Comma-separated verified administrator emails"),
    ("ENCRYPTION_KEY", "Fernet encryption key"),
    ("INTERNAL_WORKER_TOKEN", "Random internal worker token"),
    ("RAZORPAY_KEY_ID", "Razorpay key ID"),
    ("RAZORPAY_KEY_SECRET", "Razorpay key secret"),
    ("RAZORPAY_WEBHOOK_SECRET", "Razorpay webhook secret"),
    ("WHATSAPP_ACCESS_TOKEN", "WhatsApp access token"),
    ("WHATSAPP_PHONE_NUMBER_ID", "WhatsApp phone number ID"),
    ("WHATSAPP_VERIFY_TOKEN", "WhatsApp webhook verification token"),
    ("WHATSAPP_APP_SECRET", "Meta app secret"),
    ("SENTRY_DSN", "Sentry DSN"),
    ("LEGAL_CONTACT_EMAIL", "Legal/contact email"),
    ("LEGAL_BUSINESS_ADDRESS", "Business address"),
]

values = {"ENVIRONMENT": "production", "NEXT_PUBLIC_ENABLE_DEV_LOGIN": "false"}
for key, label in FIELDS:
    secret = any(word in key for word in ("SECRET", "TOKEN", "KEY")) and key not in {"RAZORPAY_KEY_ID", "WHATSAPP_PHONE_NUMBER_ID"}
    value = getpass.getpass(f"{label}: ") if secret else input(f"{label}: ")
    values[key] = value.strip()
values["NEXT_PUBLIC_API_URL"] = values["PUBLIC_API_URL"]
values["API_URL"] = values["PUBLIC_API_URL"]
Path(".env.production").write_text("\n".join(f"{k}={v}" for k, v in values.items()) + "\n")
print("Wrote .env.production. Keep it outside Git and run scripts/verify_production_env.py.")
