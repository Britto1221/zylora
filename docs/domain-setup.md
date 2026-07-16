# Domain setup

Configure a wildcard DNS record for the platform client subdomain and route it to
the Next.js application. Add every custom hostname to the domain table only after
ownership/DNS verification. The public site resolver validates the hostname
against registered active domains.

Use the client's legal registrant details. Keep renewal invoices separate from
messaging balances. Preview routes carry `noindex`; production routes use the
published canonical domain.
