# Zylora — AI Business Automation Copilot

Zylora onboards any local business via URL or documents, builds a business profile,
deploys a RAG-powered chatbot with lead capture, and outputs analytics and PDF reports.

## Structure

- `frontend/` — Next.js admin dashboard + embeddable widget
- `backend/` — FastAPI REST API
- `core/` — All AI logic (intake, RAG, agent, leads, reports)
- `scripts/` — Admin and utility scripts
- `docs/` — Architecture and API documentation

## Quick Start

```bash
# Start Postgres and Redis
docker-compose up -d

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install



npm run dev
```

## Phase Roadmap

- Phase 0: Foundation
- Phase 1: Business Intake Engine
- Phase 2: RAG Knowledge Base
- Phase 3: Chatbot + Lead Capture
- Phase 4: Automation Recommendations
- Phase 5: PDF Report + Dashboard
- Phase 6: Polish + Deploy
