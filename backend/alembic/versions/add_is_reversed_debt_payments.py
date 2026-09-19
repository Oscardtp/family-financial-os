"""Add is_reversed to debt_payments

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-09-18
"""
from alembic import op
import sqlalchemy as sa

revision = "d4e5f6g7h8i9"
down_revision = "c3d4e5f6g7h8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("debt_payments", sa.Column("is_reversed", sa.Boolean(), server_default="false", nullable=False))


def downgrade() -> None:
    op.drop_column("debt_payments", "is_reversed")
