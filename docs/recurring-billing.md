# Recurring Billing and Dunning

Recurring monthly service invoices are configured independently for each client.
The amount is stored in the smallest currency unit and the currency is either
`USD` or `INR`.

## Tenant configuration

- `monthly_amount_minor`: recurring monthly charge in cents or paise.
- `billing_currency`: `USD` or `INR`.
- `billing_day`: due day from 1 through 31. Short months are clamped to their
  final calendar day.
- `billing_status`: `current`, `warned`, or `restricted`.

Only the super admin can change recurring billing configuration. Configuration
changes are written to the audit log.

## Invoice separation

Recurring invoices use `invoice_type=RECURRING`, a `YYYY-MM` billing period,
and an idempotent tenant/type/period database constraint. Existing one-time
invoices use `invoice_type=ONE_TIME` and retain their original manual creation
flow. One-time and recurring invoice creation are separate services and API
operations.

## Scheduler

Celery Beat schedules:

- `zylora.generate_monthly_recurring_invoices` on the first day of each month.
- `zylora.evaluate_billing_dunning` daily.

The API also evaluates a tenant's billing state when the client portal reads
billing status, so access control does not depend solely on the scheduler.

## Dunning policy

- Fewer than 3 days overdue: status remains `current`; no client-facing change.
- 3 through 9 days overdue: status becomes `warned`; the portal shows a
  persistent payment-overdue banner while all portal features remain available.
- 10 or more days overdue: status becomes `restricted`; tenant-scoped API
  operations using normal portal authorization return HTTP 402. Billing status,
  pay-now, and verified checkout endpoints remain accessible.

Public published-site resolution, analytics ingestion, chatbot-public boundaries,
and lead capture do not depend on client-portal billing access. The live website
and lead form therefore remain available during restriction.

## Reminders

Idempotent email and WhatsApp reminder jobs are created at day 3 and day 8.
They use the existing notification worker and WhatsApp provider integration.
The `payment_overdue` WhatsApp template must be approved in Meta before launch.
Reminder queueing, state transitions, payments, configuration changes, and
manual overrides are audited.

## Payment clearing

A recurring invoice checkout order is created from server-side invoice data.
The stored amount and currency are authoritative. Razorpay webhook processing
marks the invoice paid and returns the tenant to `current`. A super admin can
also clear the lockout manually; that override is tied to the current overdue
invoice so the daily dunning job does not immediately re-lock the tenant.
