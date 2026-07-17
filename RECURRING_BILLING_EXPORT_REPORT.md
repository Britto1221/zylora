# Recurring Billing, Dunning, and Client Export Report

## Implemented

- Per-tenant monthly amount in minor units.
- Per-tenant USD or INR recurring billing currency.
- Per-tenant monthly due day.
- Super-admin billing configuration API and Invoices-tab UI.
- Separate one-time and recurring invoice types and creation paths.
- Idempotent monthly recurring invoice generation through Celery Beat.
- Current, warned, and restricted tenant billing states.
- Day-3 portal warning and day-10 server-enforced portal restriction.
- Billing/pay-now endpoints remain accessible during restriction.
- Public websites and lead capture remain independent of billing lockout.
- Day-3 and day-8 email/WhatsApp reminder jobs.
- Razorpay recurring-invoice checkout and webhook settlement.
- Super-admin manual lockout override.
- Audit records for configuration, invoice generation, reminders, status changes,
  payment actions, manual overrides, and exports.
- Static standalone client ZIP endpoint and CLI.
- Placeholder-based per-client HTML/CSS export.
- Export `.env.example`, README, and manifest.
- Exclusion of chatbot, Zylora lead backend, RAG/intake code, platform secrets,
  portals, and other tenant data.
- Explicit Alembic revision compatible with PostgreSQL and SQLite test upgrades.

## Verification completed

- Python compilation passed.
- Ruff passed.
- Backend tests: 18 passed.
- Backend coverage: 72.28% against a required 65% threshold.
- Empty SQLite Alembic upgrade, downgrade, and re-upgrade passed.
- OpenAPI contract regenerated.
- TypeScript and TSX syntax transpilation passed.

## Provider setup still required

- Configure live Razorpay credentials and webhook URL.
- Approve the `payment_overdue` WhatsApp template in Meta.
- Configure the production email provider.
- Run the normal frontend dependency install and production build in the target
  development/CI environment before deployment.
