# Production Readiness

This repository now contains production-oriented controls. It is not ready for
public launch until external systems and operational controls are configured.

## Required before launch

- Configure an OIDC/JWT identity provider.
- Set and test `SUPER_ADMIN_EMAILS`.
- Generate and apply Alembic migrations.
- Enable PostgreSQL TLS and Row Level Security.
- Configure Razorpay signature/webhook secrets.
- Configure WhatsApp verification, app secret, access token, phone ID, and approved templates.
- Map WhatsApp delivery events to `NotificationJob`.
- Configure object storage, upload validation, and malware scanning.
- Configure production Redis.
- Configure Sentry, metrics scraping, and alert routing.
- Configure encrypted backups and test restoration.
- Configure wildcard DNS, SSL, and custom-domain verification.
- Add privacy, terms, consent, refund, tax, and renewal-liability documents.
- Run cross-tenant tests, load tests, container scans, SAST, DAST, and secret scans.

## Non-negotiable invariants

- Lead capture cannot depend on WhatsApp delivery.
- Zero credits stop messaging only.
- Retries and duplicate webhooks cannot charge twice.
- Draft content cannot mutate the published snapshot.
- Client users cannot access another tenant.
- Plaintext secrets cannot enter logs, analytics, or browser responses.
