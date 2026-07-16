# Zylora API Reference

Base URL: http://localhost:8000 (dev) | https://api.zylora.ai (prod)

## Intake
POST /api/intake/create-client    — Create new business
POST /api/intake/build-index      — Build RAG index from documents

## Chat
POST /api/chat/                   — Send message, get RAG answer

## Leads
GET  /api/leads/{business_id}     — Get all leads for a business

## Reports
POST /api/reports/generate/{id}   — Generate PDF report
