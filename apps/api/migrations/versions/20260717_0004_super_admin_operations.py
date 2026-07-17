"""super-admin operations, client health, pause state, and notes

Revision ID: 20260717_0004
Revises: 20260717_0003
Create Date: 2026-07-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260717_0004"
down_revision: str | None = "20260717_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        tenant_status = postgresql.ENUM("ACTIVE", "PAUSED", name="tenantstatus")
        tenant_status.create(bind, checkfirst=True)
        status_type: sa.types.TypeEngine = postgresql.ENUM(
            "ACTIVE", "PAUSED", name="tenantstatus", create_type=False
        )
    else:
        status_type = sa.String(length=20)

    op.add_column(
        "tenants",
        sa.Column(
            "operational_status",
            status_type,
            nullable=False,
            server_default="ACTIVE",
        ),
    )
    op.add_column("tenants", sa.Column("paused_reason", sa.Text(), nullable=True))
    op.add_column("tenants", sa.Column("paused_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tenants", sa.Column("paused_by_user_id", sa.Uuid(), nullable=True))
    op.add_column("tenants", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_tenants_billing_status", "tenants", ["billing_status"], unique=False)
    op.create_index("ix_tenants_operational_status", "tenants", ["operational_status"], unique=False)
    op.create_index("ix_tenants_last_login_at", "tenants", ["last_login_at"], unique=False)

    op.create_table(
        "tenant_notes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("author_user_id", sa.Uuid(), nullable=False),
        sa.Column("author_email", sa.String(length=320), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tenant_notes_tenant_id", "tenant_notes", ["tenant_id"], unique=False)
    op.create_index(
        "ix_tenant_notes_author_user_id", "tenant_notes", ["author_user_id"], unique=False
    )
    op.create_index(
        "ix_tenant_notes_tenant_created",
        "tenant_notes",
        ["tenant_id", "created_at"],
        unique=False,
    )

    if is_postgres:
        op.execute("ALTER TABLE tenant_notes ENABLE ROW LEVEL SECURITY")
        op.execute("ALTER TABLE tenant_notes FORCE ROW LEVEL SECURITY")
        op.execute(
            """
            CREATE POLICY tenant_notes_private ON tenant_notes FOR ALL
            USING (zylora_is_super_admin() OR tenant_id = zylora_current_tenant())
            WITH CHECK (zylora_is_super_admin() OR tenant_id = zylora_current_tenant())
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        op.execute("DROP POLICY IF EXISTS tenant_notes_private ON tenant_notes")
    op.drop_index("ix_tenant_notes_tenant_created", table_name="tenant_notes")
    op.drop_index("ix_tenant_notes_author_user_id", table_name="tenant_notes")
    op.drop_index("ix_tenant_notes_tenant_id", table_name="tenant_notes")
    op.drop_table("tenant_notes")

    op.drop_index("ix_tenants_last_login_at", table_name="tenants")
    op.drop_index("ix_tenants_operational_status", table_name="tenants")
    op.drop_index("ix_tenants_billing_status", table_name="tenants")
    op.drop_column("tenants", "last_login_at")
    op.drop_column("tenants", "paused_by_user_id")
    op.drop_column("tenants", "paused_at")
    op.drop_column("tenants", "paused_reason")
    op.drop_column("tenants", "operational_status")

    if is_postgres:
        postgresql.ENUM(name="tenantstatus").drop(bind, checkfirst=True)
