# Deployment

A practical production topology is:

- Next.js on Vercel or the included web container,
- FastAPI container on a managed container platform,
- Celery worker container,
- managed PostgreSQL,
- managed Redis,
- S3-compatible object storage,
- OIDC identity provider,
- wildcard DNS for platform subdomains,
- custom-domain verification and SSL,
- Sentry and Prometheus-compatible monitoring.

Steps:

1. Create production PostgreSQL, Redis, storage, and identity-provider resources.
2. Copy `.env.production.example` and fill every required value.
3. Run `alembic upgrade head`.
4. Build and deploy API and worker containers.
5. Deploy the Next.js application with `API_URL` set to the private/public API.
6. Configure wildcard and application DNS.
7. Register Razorpay and WhatsApp webhook URLs.
8. Run backend, frontend, end-to-end, security, and tenant-isolation tests.
9. Verify a backup and restore before onboarding paying clients.
