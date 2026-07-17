from __future__ import annotations

from collections.abc import Generator
from uuid import UUID

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5 if settings.database_url.startswith("sqlite") else 10,
    max_overflow=10 if settings.database_url.startswith("sqlite") else 20,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _set_config(db: Session, key: str, value: str) -> None:
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        db.execute(text("SELECT set_config(:key, :value, true)"), {"key": key, "value": value})


def set_user_context(db: Session, *, user_id: UUID, is_super_admin: bool) -> None:
    _set_config(db, "app.current_user_id", str(user_id))
    _set_config(db, "app.is_super_admin", "true" if is_super_admin else "false")


def set_tenant_context(db: Session, tenant_id: UUID) -> None:
    _set_config(db, "app.current_tenant_id", str(tenant_id))


def set_public_tenant_context(db: Session, tenant_id: UUID) -> None:
    _set_config(db, "app.public_tenant_id", str(tenant_id))


def set_invitation_context(db: Session, token_hash: str) -> None:
    _set_config(db, "app.invitation_token_hash", token_hash)


def clear_request_context(db: Session) -> None:
    for key in (
        "app.current_user_id",
        "app.current_tenant_id",
        "app.public_tenant_id",
        "app.invitation_token_hash",
    ):
        _set_config(db, key, "")
    _set_config(db, "app.is_super_admin", "false")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        clear_request_context(db)
        yield db
    finally:
        db.close()
