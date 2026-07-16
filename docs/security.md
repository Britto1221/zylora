# Security

Controls implemented in code:

- verified OIDC/JWT authentication in production,
- server-side membership authorization,
- cross-tenant tests,
- encrypted API credentials,
- secret masking,
- webhook HMAC verification and deduplication,
- integer monetary storage and credit row locks,
- idempotency keys,
- rate limiting,
- honeypot spam detection,
- SSRF-safe crawling,
- safe filenames, MIME/size validation, and tenant object prefixes,
- trusted hosts, restrictive CORS, request IDs, and security headers,
- generic production errors,
- audit logs,
- CI secret and vulnerability scans.

Before launch, run an independent penetration test, enable PostgreSQL RLS, test
backup restoration, configure malware scanning, and validate all legal consent
copy.
