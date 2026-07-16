# Zylora

Managed multi-tenant landing pages, leads, optional WhatsApp follow-up, SEO,
client dashboards, domains, credits, and paid custom development.

## Local setup

```bash
cp .env.example .env
docker compose up -d

python -m venv .venv
source .venv/Scripts/activate  # Git Bash on Windows
# source .venv/bin/activate    # macOS/Linux

python -m pip install --upgrade pip
python -m pip install -e ./packages/zylora-ai
python -m pip install -e "./apps/api[dev]"
python -m pip install -e "./apps/worker[dev]"

npm install

cd apps/api
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
cd ../..

npm run dev:web
```

In another terminal:

```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
cd apps/worker
python -m app.main
```

## Important

The repository now contains production-oriented boundaries, but external
authentication, Razorpay/Stripe, WhatsApp Cloud API, domain-provider APIs,
storage, and deployment accounts still require real credentials and provider setup.
