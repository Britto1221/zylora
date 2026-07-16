# Tenant Isolation

Every tenant-owned row includes `tenant_id`.

Controls:

1. Verified authenticated identity.
2. Membership lookup.
3. Server-side tenant guard.
4. PostgreSQL Row Level Security.
5. Cross-tenant security tests.
6. No client-supplied tenant identifier is trusted without authorization.
