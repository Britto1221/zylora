# Zylora Architecture

## Overview
Zylora is a multi-tenant AI business automation platform.
Each business (client) is isolated by business_id across all data stores.

## Data Stores
- **Postgres** — businesses, documents, chat_sessions, messages, leads, recommendations
- **Pinecone** — vector embeddings, namespaced per business_id
- **Cloudflare R2** — uploaded PDFs and logos

## Services
- **FastAPI** — REST API (Railway)
- **Next.js** — Admin dashboard (Vercel)
- **LangSmith** — Agent observability

## Agent Flow
Query → Hybrid Retrieval (BM25 + Pinecone) → GPT-4o Mini → Confidence Check → Lead Detection → Response

## Isolation Strategy
Every Pinecone query filters by namespace=business_id.
Every Postgres query filters by business_id.
No cross-client data leakage is possible by design.
