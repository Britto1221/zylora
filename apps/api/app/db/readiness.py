from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import engine


def verify_database_readiness() -> None:
    settings = get_settings()
    if not settings.is_production:
        return
    if engine.dialect.name != "postgresql":
        raise RuntimeError("Production database must be PostgreSQL.")
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    expected = script.get_current_head()
    with engine.connect() as connection:
        current = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one_or_none()
        if current != expected:
            raise RuntimeError(
                f"Database migration mismatch: expected {expected}, found {current}."
            )
        required = {
            "tenants",
            "sites",
            "site_versions",
            "leads",
            "credit_accounts",
            "payments",
            "tenant_notes",
        }
        rows = connection.execute(
            text("SELECT relname, relrowsecurity FROM pg_class WHERE relname = ANY(:tables)"),
            {"tables": list(required)},
        ).all()
        enabled = {name for name, value in rows if value}
        missing = required - enabled
        if missing:
            raise RuntimeError(f"PostgreSQL RLS is not enabled on: {', '.join(sorted(missing))}")
