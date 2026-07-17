# Zylora Launch-Blocker Resolution

This archive replaces the earlier scaffold with executable production boundaries for the blockers identified during review.

## Implemented in code

- OIDC authorization-code login with PKCE, JWKS token verification, secure cookies, invitation flows, password-provider handoff, and a production startup requirement for verified super-admin email addresses.
- Explicit Alembic baseline migration plus a PostgreSQL-only RLS migration copied into the API image. Production startup checks require the database revision to equal Alembic head and require RLS on tenant tables.
- PostgreSQL and Redis TLS validation, a secure Compose reference, database request context for RLS, and cross-tenant/client-viewer authorization tests.
- Server-priced Razorpay credit packs, order creation, browser checkout, checkout signature verification, captured-payment webhooks, replay protection, payment persistence, and idempotent credit issuance.
- Meta WhatsApp Cloud API submission, provider message IDs, webhook signature verification, sent/delivered/read/failed state mapping, retries, credit reservations, and idempotent refunds after failed charged messages.
- S3-compatible presigned storage, strict file-name/extension/MIME/signature/size validation, tenant prefixes, encryption headers, quarantine states, ClamAV scanning, GuardDuty-tag integration, and CLEAN-only downloads.
- API and worker Sentry initialization, structured JSON logging, request IDs, health/readiness/metrics endpoints, alert-webhook support, failed-job visibility, and production configuration validation.
- Privacy, terms, refund, and cookie-policy routes driven by legal environment settings.
- Encrypted PostgreSQL backup, restore, restore-verification tooling, CI verification workflow, retention controls, and recovery documentation.
- k6 load tests, OWASP ZAP DAST workflow, Trivy/Gitleaks scanning, cross-tenant tests, role-escalation tests, and upload-security tests.

## Verification completed in this build environment

- API compilation: passed.
- API Ruff lint: passed.
- API MyPy: passed.
- API tests: 16 passed with 71.30% measured coverage.
- Explicit migrations: upgraded an empty database to `20260717_0002 (head)`.
- OpenAPI generation: 81 paths and 28 schemas.
- Frontend TypeScript: passed.
- Frontend ESLint: passed.
- Frontend unit tests: passed.
- Next.js production build: passed with all application routes generated.
- Shell-script syntax checks: passed.
- Compose and GitHub workflow YAML parsing: passed.

## Actions that cannot be embedded in source code

The application intentionally refuses production startup until real provider and business values are supplied. The operator must still create or activate the external accounts, enter the verified owner email in `SUPER_ADMIN_EMAILS`, register callback/webhook URLs, provide certificates and secrets, run the DAST/load suites against a deployed staging environment, test backup restoration against the chosen managed database, and have the legal templates reviewed for the actual entity and commercial terms.

See `docs/manual-provider-actions.md`, `docs/external-provider-setup.md`, `docs/launch-readiness.md`, and `.env.production.example`.
