"""add household performance indexes

Revision ID: k1l2m3n4o5p6
Revises: i4j5k6l7m8n9
Create Date: 2026-09-04 09:03:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision = 'k1l2m3n4o5p6'
down_revision = 'i4j5k6l7m8n9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def index_exists(index_name: str, table_name: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(sa.text(
        "SELECT name FROM sqlite_master WHERE type='index' AND name=:name"
        if bind.dialect.name == 'sqlite'
        else "SELECT indexname FROM pg_indexes WHERE indexname=:name"
    ), {'name': index_name})
    return result.fetchone() is not None


def upgrade() -> None:
    if not index_exists('ix_accounts_household_id', 'accounts'):
        op.create_index('ix_accounts_household_id', 'accounts', ['household_id'])
    if not index_exists('ix_transactions_account_id', 'transactions'):
        op.create_index('ix_transactions_account_id', 'transactions', ['account_id'])
    if not index_exists('ix_debts_household_id', 'debts'):
        op.create_index('ix_debts_household_id', 'debts', ['household_id'])
    if not index_exists('ix_savings_goals_household_id', 'savings_goals'):
        op.create_index('ix_savings_goals_household_id', 'savings_goals', ['household_id'])
    if not index_exists('ix_liabilities_household_id', 'liabilities'):
        op.create_index('ix_liabilities_household_id', 'liabilities', ['household_id'])
    if not index_exists('ix_budgets_household_id', 'budgets'):
        op.create_index('ix_budgets_household_id', 'budgets', ['household_id'])
    if not index_exists('ix_budgets_household_month', 'budgets'):
        op.create_index('ix_budgets_household_month', 'budgets', ['household_id', 'month', 'year'])
    if not index_exists('ix_recurring_payments_household_id', 'recurring_payments'):
        op.create_index('ix_recurring_payments_household_id', 'recurring_payments', ['household_id'])

def downgrade() -> None:
    op.drop_index('ix_recurring_payments_household_id', table_name='recurring_payments')
    op.drop_index('ix_budgets_household_month', table_name='budgets')
    op.drop_index('ix_budgets_household_id', table_name='budgets')
    op.drop_index('ix_liabilities_household_id', table_name='liabilities')
    op.drop_index('ix_savings_goals_household_id', table_name='savings_goals')
    op.drop_index('ix_debts_household_id', table_name='debts')
    op.drop_index('ix_transactions_account_id', table_name='transactions')
    op.drop_index('ix_accounts_household_id', table_name='accounts')
