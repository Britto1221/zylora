# Zylora v2 Migration Report

Generated: 20260716_221447

## Preserved prototype

The original prototype was moved to:

`legacy/20260716_221447/`

## Added

- Next.js web application
- FastAPI application
- Celery worker
- PostgreSQL and Redis development services
- Alembic configuration
- Tenant, membership, site, site-version, lead, credit, notification, domain,
  API-credential, and audit-log models
- USD credit transaction service
- Graceful WhatsApp job boundary
- Publishing approval service
- Tenant guard
- Secret encryption helper
- Initial security tests
- Three website templates
- Client override registry
- CI workflows
- Architecture and operating documentation

## Still requires provider setup

- Production authentication provider
- Razorpay or Stripe account and verified webhooks
- WhatsApp Cloud API account and approved templates
- Domain registrar/provider automation
- Production object storage
- Monitoring and alerting
- Production database backups
- Deployment configuration
