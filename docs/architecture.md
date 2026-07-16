# Architecture

Zylora is a modular monorepo.

## Web

Next.js renders the public marketing website, monochromatic super-admin console,
client portal, previews, and public tenant websites. Public browser operations use
same-origin Next.js proxy routes so custom domains do not depend on permissive
cross-origin configuration.

## API

FastAPI owns authorization and business logic. PostgreSQL is the production
source of truth; SQLite is a development convenience. Business modules cover
tenants, websites, publishing, leads, notifications, credits, payments, domains,
assets, documents, chatbot retrieval, SEO, analytics, changes, invoices, access,
and audit logs.

## Worker

Celery performs slow or retryable operations. The worker uses authenticated
internal API endpoints, so database business rules remain centralized.

## AI package

`packages/zylora-ai` contains provider-independent intake parsing, SSRF-safe
crawling, chunking, deterministic local embeddings, retrieval, evaluation, SEO,
reporting, and orchestration utilities.

## Data flow

```text
Admin edits draft
→ API validates and persists snapshot
→ super admin reviews and approves
→ published version pointer changes atomically
→ public hostname resolves registered tenant site

Visitor submits lead
→ API validates and stores lead
→ notification jobs are stored in same transaction
→ visitor receives success
→ worker reserves credits and sends messages
→ webhook finalizes status, charge, or refund
```
