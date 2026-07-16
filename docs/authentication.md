# Authentication

Development uses a signed local token and the credentials documented in the
README. This mode is permitted only outside production.

Production requires an OIDC-compatible provider exposing a JWKS endpoint.
Configure `AUTH_ISSUER`, `AUTH_AUDIENCE`, `AUTH_JWKS_URL`, and
`SUPER_ADMIN_EMAILS`.

The API verifies token signature, issuer, audience, expiry, subject, and email.
Tenant roles are loaded from `tenant_memberships`; browser-provided role or tenant
headers are never trusted.

Client invitations bind an email address, tenant, role, expiry, and one-time
token. Acceptance requires an authenticated user whose verified email matches the
invitation.
