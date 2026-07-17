from __future__ import annotations

from pathlib import Path


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


path = Path(".env.production")
if not path.exists():
    raise SystemExit(
        ".env.production is missing. Run scripts/configure_production.py first."
    )

values = load_env(path)
required = [
    "DATABASE_URL",
    "REDIS_URL",
    "AUTH_ISSUER",
    "AUTH_JWKS_URL",
    "AUTH_CLIENT_ID",
    "AUTH_AUTHORIZATION_URL",
    "AUTH_TOKEN_URL",
    "SUPER_ADMIN_EMAILS",
    "ENCRYPTION_KEY",
    "RAZORPAY_KEY_ID",
    "RAZORPAY_KEY_SECRET",
    "RAZORPAY_WEBHOOK_SECRET",
    "WHATSAPP_ACCESS_TOKEN",
    "WHATSAPP_PHONE_NUMBER_ID",
    "WHATSAPP_VERIFY_TOKEN",
    "WHATSAPP_APP_SECRET",
    "SENTRY_DSN",
    "LEGAL_CONTACT_EMAIL",
    "LEGAL_BUSINESS_ADDRESS",
]
missing = [key for key in required if not values.get(key)]
if missing:
    raise SystemExit("Missing production values: " + ", ".join(missing))

database_url = values["DATABASE_URL"]
redis_url = values["REDIS_URL"]
admin_emails = values["SUPER_ADMIN_EMAILS"].lower()

if not database_url.startswith("postgresql") or "sslmode=" not in database_url:
    raise SystemExit("DATABASE_URL must be PostgreSQL with TLS sslmode.")
if not redis_url.startswith("rediss://"):
    raise SystemExit("REDIS_URL must use rediss://.")
if "example.com" in admin_emails or "your_real_verified_email" in admin_emails:
    raise SystemExit("Replace SUPER_ADMIN_EMAILS with real verified email addresses.")

print("Production environment passes static validation.")
