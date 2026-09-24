"""add household_budget_methods table (FASE 6.3B)

Revision ID: f6a7b8c9d0e1
Revises: m1a2b3c4d5e6
Create Date: 2026-09-22 00:00:00.000000

Pure CREATE TABLE — no existing data is read or modified.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = 'm1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "household_budget_methods",
        sa.Column("household_id", sa.String(36), sa.ForeignKey("households.id"), primary_key=True),
        sa.Column("method_type", sa.String(50), nullable=True),
        sa.Column("groups_json", sa.Text(), nullable=True),
        sa.Column("category_groups_json", sa.Text(), nullable=True),
        sa.Column("reference_income_source", sa.String(30), nullable=True),
        sa.Column("reference_income_amount", sa.Numeric(15, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("household_budget_methods")
