"""add interest_rate_type column to debts and liabilities

Revision ID: i4j5k6l7m8n9
Revises: h3i4j5k6l7m8
Create Date: 2026-09-04 10:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'i4j5k6l7m8n9'
down_revision: Union[str, None] = 'h3i4j5k6l7m8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(sa.text(
        f"PRAGMA table_info({table_name})"
    ))
    return any(row[1] == column_name for row in result.fetchall())


def upgrade() -> None:
    if not column_exists('debts', 'interest_rate_type'):
        op.add_column('debts', sa.Column('interest_rate_type', sa.String(length=20), server_default='EA', nullable=False))
    if not column_exists('liabilities', 'interest_rate_type'):
        op.add_column('liabilities', sa.Column('interest_rate_type', sa.String(length=20), server_default='EA', nullable=False))


def downgrade() -> None:
    if column_exists('debts', 'interest_rate_type'):
        op.drop_column('debts', 'interest_rate_type')
    if column_exists('liabilities', 'interest_rate_type'):
        op.drop_column('liabilities', 'interest_rate_type')
