"""add category_id to financial_events

Revision ID: h3i4j5k6l7m8
Revises: g2h3i4j5k6l7
Create Date: 2026-09-01 10:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'h3i4j5k6l7m8'
down_revision: Union[str, None] = 'g2h3i4j5k6l7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(sa.text(
        f"PRAGMA table_info({table_name})"
    ))
    return any(row[1] == column_name for row in result.fetchall())


def upgrade() -> None:
    if not column_exists('financial_events', 'category_id'):
        op.add_column('financial_events', sa.Column('category_id', sa.String(length=36), nullable=True))
        op.create_foreign_key('fk_financial_events_category', 'financial_events', 'categories', ['category_id'], ['id'])


def downgrade() -> None:
    if column_exists('financial_events', 'category_id'):
        op.drop_constraint('fk_financial_events_category', 'financial_events', type_='foreignkey')
        op.drop_column('financial_events', 'category_id')
