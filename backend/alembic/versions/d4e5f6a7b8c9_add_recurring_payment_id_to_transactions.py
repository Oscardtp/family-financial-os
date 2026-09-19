"""add recurring_payment_id to transactions

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-09-19 23:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'transactions',
        sa.Column('recurring_payment_id', sa.String(36), sa.ForeignKey('recurring_payments.id'), nullable=True)
    )
    op.create_index(
        'ix_transactions_recurring_payment_id',
        'transactions',
        ['recurring_payment_id'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_transactions_recurring_payment_id', table_name='transactions')
    op.drop_column('transactions', 'recurring_payment_id')
