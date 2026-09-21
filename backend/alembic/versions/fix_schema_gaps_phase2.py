"""Fix remaining schema gaps: missing tables and columns

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-09-18
"""
from alembic import op
import sqlalchemy as sa

revision = "c3d4e5f6g7h8"
down_revision = "b2c3d4e5f6g7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Missing tables from ORM that were never migrated ---

    # category_account_preferences
    op.create_table(
        "category_account_preferences",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("household_id", sa.String(36), sa.ForeignKey("households.id"), nullable=False),
        sa.Column("category_id", sa.String(36), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("account_id", sa.String(36), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # debt_payment_overrides
    op.create_table(
        "debt_payment_overrides",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("debt_id", sa.String(36), sa.ForeignKey("debts.id"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("is_paid", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("marked_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("marked_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # financial_events
    op.create_table(
        "financial_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("household_id", sa.String(36), sa.ForeignKey("households.id"), nullable=False, index=True),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("source_id", sa.String(36), nullable=True),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="COP"),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("recommended_date", sa.Date(), nullable=True),
        sa.Column("cutoff_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("account_id", sa.String(36), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("responsible_member_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("is_recurrent", sa.Boolean(), server_default="false"),
        sa.Column("recurrence_group_id", sa.String(36), nullable=True),
        sa.Column("reminder_days_before", sa.Integer(), server_default="3"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("confirmed", sa.Boolean(), server_default="true"),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("paid_amount", sa.Numeric(15, 2), nullable=True),
        sa.Column("paid_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("obligation_id", sa.String(36), nullable=True, index=True),
        sa.Column("category_id", sa.String(36), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("visibility", sa.String(12), server_default="confirmed"),
        sa.Column("confidence", sa.Integer(), server_default="100"),
        sa.Column("payment_method", sa.String(12), nullable=True),
        sa.Column("consequence_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # financial_obligations
    op.create_table(
        "financial_obligations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("household_id", sa.String(36), sa.ForeignKey("households.id"), nullable=False, index=True),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("source_id", sa.String(36), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="COP"),
        sa.Column("frequency", sa.String(20), server_default="monthly"),
        sa.Column("anchor_day", sa.Integer(), nullable=True),
        sa.Column("recommended_offset_days", sa.Integer(), server_default="5"),
        sa.Column("cutoff_offset_days", sa.Integer(), nullable=True),
        sa.Column("reminder_days_before", sa.Integer(), server_default="3"),
        sa.Column("account_id", sa.String(36), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("category_id", sa.String(36), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("responsible_member_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("confidence", sa.Integer(), server_default="100"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # --- Missing columns on existing tables ---

    # debts: missing interest_rate_type
    op.add_column("debts", sa.Column("interest_rate_type", sa.String(20), server_default="EA"))

    # liabilities: missing interest_rate_type
    op.add_column("liabilities", sa.Column("interest_rate_type", sa.String(20), server_default="EA"))

    # savings_goals: missing description, goal_type, expected_return_rate, horizon_months, monthly_contribution
    op.add_column("savings_goals", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("savings_goals", sa.Column("goal_type", sa.String(20), server_default="savings"))
    op.add_column("savings_goals", sa.Column("expected_return_rate", sa.Numeric(5, 2), nullable=True))
    op.add_column("savings_goals", sa.Column("horizon_months", sa.Integer(), nullable=True))
    op.add_column("savings_goals", sa.Column("monthly_contribution", sa.Numeric(15, 2), nullable=True))

    # debt_payments: missing is_reversed
    op.add_column("debt_payments", sa.Column("is_reversed", sa.Boolean(), server_default="false", nullable=False))


def downgrade() -> None:
    op.drop_column("savings_goals", "monthly_contribution")
    op.drop_column("savings_goals", "horizon_months")
    op.drop_column("savings_goals", "expected_return_rate")
    op.drop_column("savings_goals", "goal_type")
    op.drop_column("savings_goals", "description")

    op.drop_column("liabilities", "interest_rate_type")
    op.drop_column("debts", "interest_rate_type")

    op.drop_table("financial_obligations")
    op.drop_table("financial_events")
    op.drop_table("debt_payment_overrides")
    op.drop_table("category_account_preferences")
