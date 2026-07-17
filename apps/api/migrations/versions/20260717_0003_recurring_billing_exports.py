"""recurring billing, dunning, and standalone exports

Revision ID: 20260717_0003
Revises: 20260717_0002
Create Date: 2026-07-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260717_0003"
down_revision: str | None = "20260717_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        billing_status_type = postgresql.ENUM(
            "CURRENT", "WARNED", "RESTRICTED", name="billingstatus"
        )
        invoice_type = postgresql.ENUM("ONE_TIME", "RECURRING", name="invoicetype")
        billing_status_type.create(bind, checkfirst=True)
        invoice_type.create(bind, checkfirst=True)
        billing_column_type: sa.types.TypeEngine = postgresql.ENUM(
            "CURRENT", "WARNED", "RESTRICTED", name="billingstatus", create_type=False
        )
        invoice_column_type: sa.types.TypeEngine = postgresql.ENUM(
            "ONE_TIME", "RECURRING", name="invoicetype", create_type=False
        )
    else:
        billing_column_type = sa.String(length=20)
        invoice_column_type = sa.String(length=20)

    op.add_column(
        "tenants",
        sa.Column("monthly_amount_minor", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "tenants",
        sa.Column("billing_currency", sa.String(length=3), nullable=False, server_default="USD"),
    )
    op.add_column(
        "tenants",
        sa.Column("billing_day", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "tenants",
        sa.Column(
            "billing_status",
            billing_column_type,
            nullable=False,
            server_default="CURRENT",
        ),
    )

    if is_postgres:
        op.create_check_constraint(
            "ck_tenants_billing_currency",
            "tenants",
            "billing_currency IN ('USD', 'INR')",
        )
        op.create_check_constraint(
            "ck_tenants_billing_day",
            "tenants",
            "billing_day >= 1 AND billing_day <= 31",
        )
        op.create_check_constraint(
            "ck_tenants_monthly_amount_nonnegative",
            "tenants",
            "monthly_amount_minor >= 0",
        )

    op.add_column(
        "invoices",
        sa.Column(
            "invoice_type",
            invoice_column_type,
            nullable=False,
            server_default="ONE_TIME",
        ),
    )
    op.add_column("invoices", sa.Column("billing_period", sa.String(length=7), nullable=True))
    op.add_column(
        "invoices",
        sa.Column("auto_generated", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    if is_postgres:
        op.create_unique_constraint(
            "uq_recurring_invoice_period",
            "invoices",
            ["tenant_id", "invoice_type", "billing_period"],
        )
        op.alter_column("notification_jobs", "lead_id", existing_type=sa.Uuid(), nullable=True)
    else:
        with op.batch_alter_table("invoices") as batch_op:
            batch_op.create_unique_constraint(
                "uq_recurring_invoice_period",
                ["tenant_id", "invoice_type", "billing_period"],
            )
        with op.batch_alter_table("notification_jobs") as batch_op:
            batch_op.alter_column("lead_id", existing_type=sa.Uuid(), nullable=True)

    op.add_column("payments", sa.Column("invoice_id", sa.Uuid(), nullable=True))
    op.add_column(
        "payments",
        sa.Column("purpose", sa.String(length=40), nullable=False, server_default="credits"),
    )
    op.create_index("ix_payments_invoice_id", "payments", ["invoice_id"], unique=False)

    if is_postgres:
        op.create_foreign_key(
            "fk_payments_invoice_id_invoices",
            "payments",
            "invoices",
            ["invoice_id"],
            ["id"],
            ondelete="SET NULL",
        )
    else:
        with op.batch_alter_table("payments") as batch_op:
            batch_op.create_foreign_key(
                "fk_payments_invoice_id_invoices",
                "invoices",
                ["invoice_id"],
                ["id"],
                ondelete="SET NULL",
            )


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        op.drop_constraint("fk_payments_invoice_id_invoices", "payments", type_="foreignkey")
    else:
        with op.batch_alter_table("payments") as batch_op:
            batch_op.drop_constraint("fk_payments_invoice_id_invoices", type_="foreignkey")

    op.drop_index("ix_payments_invoice_id", table_name="payments")
    op.drop_column("payments", "purpose")
    op.drop_column("payments", "invoice_id")

    if is_postgres:
        op.alter_column("notification_jobs", "lead_id", existing_type=sa.Uuid(), nullable=False)
        op.drop_constraint("uq_recurring_invoice_period", "invoices", type_="unique")
    else:
        with op.batch_alter_table("notification_jobs") as batch_op:
            batch_op.alter_column("lead_id", existing_type=sa.Uuid(), nullable=False)
        with op.batch_alter_table("invoices") as batch_op:
            batch_op.drop_constraint("uq_recurring_invoice_period", type_="unique")

    op.drop_column("invoices", "auto_generated")
    op.drop_column("invoices", "billing_period")
    op.drop_column("invoices", "invoice_type")

    if is_postgres:
        op.drop_constraint("ck_tenants_monthly_amount_nonnegative", "tenants", type_="check")
        op.drop_constraint("ck_tenants_billing_day", "tenants", type_="check")
        op.drop_constraint("ck_tenants_billing_currency", "tenants", type_="check")

    op.drop_column("tenants", "billing_status")
    op.drop_column("tenants", "billing_day")
    op.drop_column("tenants", "billing_currency")
    op.drop_column("tenants", "monthly_amount_minor")

    if is_postgres:
        postgresql.ENUM(name="invoicetype").drop(bind, checkfirst=True)
        postgresql.ENUM(name="billingstatus").drop(bind, checkfirst=True)
