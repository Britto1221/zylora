# Zylora Architecture

Zylora is a managed, multi-tenant platform with:

- `apps/web`: Next.js marketing site, super-admin dashboard, client portal, previews, and public tenant rendering.
- `apps/api`: FastAPI authorization, tenants, sites, leads, publishing, credits, domains, payments, and integrations.
- `apps/worker`: asynchronous WhatsApp, SEO, domain reminder, document, and publishing jobs.
- `packages/zylora-ai`: reusable intake, RAG, agent, reporting, and SEO logic.
- PostgreSQL: source of truth.
- Redis/Celery: asynchronous work.

Public lead capture must succeed even when WhatsApp, AI, or credits are unavailable.
