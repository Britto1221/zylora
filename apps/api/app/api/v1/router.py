from fastapi import APIRouter

from app.api.v1 import credits, health, leads, publishing, tenants

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(tenants.router)
api_router.include_router(leads.router)
api_router.include_router(credits.router)
api_router.include_router(publishing.router)
