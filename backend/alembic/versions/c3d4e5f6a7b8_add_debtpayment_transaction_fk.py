"""add debtpayment transaction FK with RESTRICT ondelete

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7, a1b2c3d4e5f6
Create Date: 2026-09-19 15:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = ('b2c3d4e5f6a7', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_foreign_key(
        'fk_debt_payments_transaction_id',
        'debt_payments',
        'transactions',
        ['transaction_id'],
        ['id'],
        ondelete='RESTRICT',
    )


def downgrade() -> None:
    op.drop_constraint('fk_debt_payments_transaction_id', 'debt_payments', type_='foreignkey')
