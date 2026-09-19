"""add auditlog household FK

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6, d4e5f6g7h8i9
Create Date: 2026-09-19 14:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = ('a1b2c3d4e5f6', 'd4e5f6g7h8i9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_foreign_key(
        'fk_audit_logs_household_id',
        'audit_logs',
        'households',
        ['household_id'],
        ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('fk_audit_logs_household_id', 'audit_logs', type_='foreignkey')
