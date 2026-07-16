from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "zylora-api"}


@router.get("/ready")
def readiness(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        redis = Redis.from_url(settings.redis_url, socket_connect_timeout=2)
        redis.ping()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Service dependencies unavailable.") from exc
    return {"status": "ready"}
