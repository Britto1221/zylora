# Super-admin portfolio operations

## Client list filters

The client list supports server-side filtering by billing status, published-site state,
and last-login range. The returned health status is computed from the tenant billing
status, whether the site is published, the latest recorded client login, and manual
pause state. The API always returns the reasons with the health label.

## Bulk actions

Only verified super administrators may run bulk actions. Bulk reminder, billing
override, and export operations load each tenant from the database and call the same
audited service used by the individual action. Each affected tenant receives its own
audit event, and the overall batch also receives a portfolio-level audit event.

Supported operations:

- queue payment reminders for each selected tenant with an unpaid recurring invoice;
- generate a bundle containing one isolated static self-host ZIP per selected tenant;
- clear billing restrictions using the normal manual-override service.

## Revenue dashboard

The revenue view derives values from Tenant and Invoice records only. MRR, overdue
amounts, and upcoming recurring invoice amounts are reported separately in USD and
INR. No exchange-rate conversion is performed. Paused tenants are excluded from
current billable MRR because recurring invoice generation is suspended.

## Client health

Health labels are:

- `Healthy`: billing is current, the site is published, the client logged in within
  the last 30 days, and the tenant is not paused.
- `Needs attention`: one or more non-restrictive conditions need review, including
  overdue billing, draft site, missing/stale login, or manual pause.
- `Restricted`: billing status is restricted.

The list and detail page expose the underlying reasons; the label is never the only
information presented.

## Manual pause

`operational_status=paused` is independent of both `is_active` and `billing_status`.
A paused tenant keeps its portal, public website, and lead capture. The monthly
billing scheduler skips it. Pause and unpause operations require a reason and create
an audit entry.

## Internal client notes

Tenant notes are append-only records containing author ID, author email, timestamp,
and plain-text body. Only super administrators can list or add these notes. Adding a
note produces an audit event; existing notes cannot be overwritten through the API.
