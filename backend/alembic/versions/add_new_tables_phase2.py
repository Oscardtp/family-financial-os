"""Add new tables: transfers, household_members, import_batch - Phase 2

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-18
"""
from alembic import op
import sqlalchemy as sa

revision = "b2c3d4e5f6g7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Transfers ---
    op.create_table(
        "transfers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("household_id", sa.String(36), sa.ForeignKey("households.id"), nullable=False, index=True),
        sa.Column("from_account_id", sa.String(36), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("to_account_id", sa.String(36), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="COP"),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # --- HouseholdMembers ---
    op.create_table(
        "household_members",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("household_id", sa.String(36), sa.ForeignKey("households.id"), nullable=False, index=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("role", sa.String(20), server_default="member"),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("joined_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("household_id", "user_id", name="uq_household_user"),
    )

    # --- ImportBatch ---
    op.create_table(
        "import_batches",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("household_id", sa.String(36), sa.ForeignKey("households.id"), nullable=False, index=True),
        sa.Column("source_file", sa.String(500), nullable=False),
        sa.Column("imported_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("records_detected", sa.Integer(), server_default="0"),
        sa.Column("records_imported", sa.Integer(), server_default="0"),
        sa.Column("records_rejected", sa.Integer(), server_default="0"),
        sa.Column("error_report", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("import_batches")
    op.drop_table("household_members")
    op.drop_table("transfers")
