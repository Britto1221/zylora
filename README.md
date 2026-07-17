# Zylora

Zylora is a managed multi-tenant platform for building, publishing, and operating
business landing pages. The repository includes a monochromatic super-admin
console, client portal, reusable website templates, leads, publishing versions,
domains, prepaid messaging credits, WhatsApp jobs, SEO audits, documents,
grounded chatbot retrieval, analytics, invoices, payments, change requests,
feature flags, audit logs, and background workers.

## Repository

- `apps/web` — Next.js marketing site, monochromatic admin console, client portal,
  previews, and public client websites.
- `apps/api` — FastAPI application and PostgreSQL/SQLite persistence.
- `apps/worker` — Celery jobs for notifications, SEO, documents, reminders, and cleanup.
- `packages/zylora-ai` — reusable intake, SEO, RAG, agent, and report utilities.
- `infra` — database policies and deployment boundaries.
- `docs` — architecture, security, provider, deployment, and operating guidance.

## Super-admin portfolio operations

Zylora includes filtered client health views, audited multi-client actions, a
separate-currency revenue dashboard, deliberate client pause controls, and
append-only internal client notes. See `docs/super-admin-portfolio.md`.

## Local development

Requirements:

- Python 3.11+
- Node.js 22+
- Docker Desktop for PostgreSQL and Redis, or use the default SQLite development DB

Create the environment:

```bash
cp .env.example .env

python -m venv .venv
source .venv/Scripts/activate   # Git Bash on Windows
# source .venv/bin/activate     # macOS/Linux

python -m pip install --upgrade pip
python -m pip install -e ./packages/zylora-ai
python -m pip install -e "./apps/api[dev]"
python -m pip install -e "./apps/worker[dev]"

npm install
```

Start the API:

```bash
source .venv/Scripts/activate
cd apps/api
uvicorn app.main:app --reload --port 8000
```

Start the web application:

```bash
npm run dev:web
```

Start Redis and the worker when testing background jobs:

```bash
docker compose up -d redis

source .venv/Scripts/activate
cd apps/worker
celery -A app.main:app worker --loglevel=INFO
```

Development login:

```text
Email:    admin@zylora.dev
Password: zylora-admin
```

The development database is seeded automatically with school, clinic, and
coaching examples. Development authentication is disabled when
`ENVIRONMENT=production`.

## Database migrations

For PostgreSQL:

```bash
docker compose up -d postgres redis

cd apps/api
alembic upgrade head
```

The included baseline migration creates the complete initial schema. Future
schema changes must use explicit Alembic revisions.

## Tests and quality

Backend:

```bash
cd apps/api
pytest
ruff check app tests
mypy app
```

Frontend:

```bash
npm run typecheck:web
npm run lint:web
npm run test:web
npm run build:web
```

End-to-end:

```bash
npm run dev:web
npm run test:e2e
```

Generate the API contract:

```bash
python scripts/generate_openapi.py
```

## Production

Copy and complete the production environment:

```bash
cp .env.production.example .env
```

Build containers:

```bash
docker compose -f docker-compose.prod.yml build
```

External accounts and credentials still require manual setup. See
`docs/manual-provider-actions.md` and `docs/deployment.md`.

## Core guarantees

- A lead is committed before notification processing.
- WhatsApp failures and zero credits never disable websites or lead capture.
- Credit movements use integer micro-USD values, row locks, and idempotency keys.
- Drafts and published snapshots are separate.
- Only the super admin can approve, publish, or roll back a site.
- Tenant membership is enforced by the API; production uses verified OIDC/JWT tokens.
- Client API keys are encrypted and never returned after storage.
- Webhook events are signature-verified and deduplicated.

## Launch-hardening workflow

```bash
cp .env.production.example .env.production
python scripts/configure_production.py
python scripts/verify_production_env.py

cd apps/api
alembic upgrade head
pytest
cd ../..

npm install
npm run typecheck:web
npm run lint:web
npm run build:web
```

The API refuses to start in production when required authentication, administrator, TLS, payment, messaging, malware-scanning, monitoring or legal-contact configuration is missing. It also verifies that the database is at the Alembic head and that PostgreSQL RLS is enabled.

Review `docs/launch-readiness.md` and `docs/manual-provider-actions.md` before accepting customers.

## Recurring billing

Recurring billing is configured per client from the super-admin Invoices tab.
Each tenant can be billed in USD or INR, with an independent amount and due day.
The monthly Celery task creates `RECURRING` invoices without changing the
existing `ONE_TIME` invoice flow.

Dunning is server-enforced: day 3 produces a portal warning, day 10 restricts
portal API access to billing and pay-now operations, and verified payment or a
super-admin override restores access. Public websites and lead capture are never
restricted. See `docs/recurring-billing.md`.

## Standalone client export

Generate a static handoff package with:

```bash
python scripts/export_client.py --client_id=<TENANT_UUID> --output_dir=exports
```

The resulting ZIP contains only the selected client's static site, blank
third-party configuration examples, and deployment instructions. It excludes
Zylora platform code, secrets, chatbot/RAG functionality, backend lead capture,
and every other tenant's data. See `docs/client-export.md`.
