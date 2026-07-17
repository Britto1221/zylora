# Verification Report

## Passed

```text
API: python compilation
API: Ruff
API: MyPy
API: Pytest — 16 passed
API coverage — 71.30% (threshold 65%)
Alembic empty-database upgrade — head 20260717_0002
OpenAPI generation — 81 paths, 28 schemas
Web: TypeScript
Web: ESLint
Web: Vitest — 1 passed
Web: Next.js production build
Bash syntax checks
YAML parse checks
```

## Staging-only gates provided but not executed here

- Real OIDC provider login and invitation acceptance.
- Razorpay test-mode checkout and webhook delivery from Razorpay.
- Meta WhatsApp approved-template delivery callbacks.
- S3/GuardDuty or deployed ClamAV upload scanning.
- OWASP ZAP against a deployed staging URL.
- k6 authenticated and public traffic tests against staging.
- Encrypted backup/restore against the selected managed PostgreSQL service.
- Sentry and operator alert delivery.
- Wildcard/custom-domain DNS and TLS issuance.

These gates require external accounts, credentials, DNS, and a running staging environment and therefore cannot be honestly marked as executed inside an offline ZIP-generation environment.
