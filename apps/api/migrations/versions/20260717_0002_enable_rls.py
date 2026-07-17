"""Enable PostgreSQL row-level security.

Revision ID: 20260717_0002
Revises: 07d641d8e2ec
"""
from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "20260717_0002"
down_revision: str | None = "07d641d8e2ec"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    sql_path = Path(__file__).resolve().parents[1] / "tenant_isolation.sql"
    op.execute(sql_path.read_text(encoding="utf-8"))


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    tables = [
        "analytics_events", "api_credentials", "assets", "audit_logs", "change_requests",
        "chat_conversations", "chat_messages", "client_invitations", "credit_accounts",
        "credit_reservations", "credit_transactions", "document_chunks", "documents", "domains",
        "feature_flags", "invoices", "lead_notes", "leads", "notification_jobs",
        "notification_settings", "payments", "seo_audits", "site_versions", "sites",
        "tenant_memberships", "tenants"
    ]
    for table in tables:
        op.execute(f'DROP POLICY IF EXISTS "{table}_tenant_policy" ON "{table}"')
        op.execute(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY')
