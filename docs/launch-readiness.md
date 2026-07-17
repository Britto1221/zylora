# Zylora Launch Readiness

The repository contains the implementation boundaries required for production, but a release is permitted only after the checks below pass against the real staging and production accounts.

## Automated gates

- `alembic upgrade head` succeeds from an empty database.
- API test suite passes, including cross-tenant and role tests.
- `npm run typecheck:web`, `npm run lint:web`, and `npm run build:web` pass.
- DAST workflow passes against staging.
- k6 thresholds pass against staging.
- Encrypted backup and restore verification passes.
- Secret and dependency scans pass.

## Provider gates

- OIDC authorization-code/PKCE flow works with the production redirect URL.
- `SUPER_ADMIN_EMAILS` contains the verified owner email and no placeholder.
- Razorpay order, checkout signature, captured-payment webhook, duplicate webhook, and refund paths are tested in test mode.
- WhatsApp templates are approved and sent/delivered/read/failed callbacks update notification jobs.
- Object storage uploads remain quarantined until ClamAV or GuardDuty returns CLEAN.
- Sentry receives API and worker exceptions; alert webhook reaches the operator.
- Wildcard and custom-domain TLS is verified.

## Legal gate

The included privacy, terms, refund, and cookie pages are implementation templates, not legal advice. Replace environment placeholders, align the text with the actual business entity, tax treatment, processor list, support process, retention schedule, and refund commitments, then obtain qualified legal review before accepting production customers.
