# Database

Production uses PostgreSQL. Monetary credit values are integers in micro-USD.
Tables include tenants, memberships, invitations, sites, versions, leads, lead
notes, notification settings/jobs, credit accounts/reservations/transactions,
payments, invoices, webhooks, domains, assets, API credentials, documents,
chunks, conversations/messages, SEO audits, analytics, changes, feature flags,
and audit logs.

Run:

```bash
cd apps/api
alembic upgrade head
```

The first migration is a baseline schema migration. Every later change must be
represented by a reviewed Alembic revision. Apply the RLS policies in
`infra/database/policies` only after authenticated tenant context is configured
for each database transaction.
