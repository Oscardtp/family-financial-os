"""add balance history, amortization schedules, and detected patterns

Revision ID: l5m6n7o8p9q0
Revises: e265573d3d5c
Create Date: 2026-09-18 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision = 'l5m6n7o8p9q0'
down_revision = 'e265573d3d5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(sa.text(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=:name"
        if bind.dialect.name == 'sqlite'
        else "SELECT tablename FROM pg_tables WHERE tablename=:name"
    ), {'name': table_name})
    return result.fetchone() is not None


def upgrade() -> None:
    # 1. account_balance_history - Historial de saldos por transaccion
    if not table_exists('account_balance_history'):
        op.create_table(
            'account_balance_history',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('account_id', sa.String(36), sa.ForeignKey('accounts.id'), nullable=False, index=True),
            sa.Column('transaction_id', sa.String(36), sa.ForeignKey('transactions.id'), nullable=True, index=True),
            sa.Column('balance_before', sa.Numeric(15, 2), nullable=False),
            sa.Column('balance_after', sa.Numeric(15, 2), nullable=False),
            sa.Column('change_amount', sa.Numeric(15, 2), nullable=False),
            sa.Column('change_type', sa.String(20), nullable=False),  # income, expense, transfer, adjustment
            sa.Column('recorded_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        )

    # 2. amortization_schedules - Tablas de amortizacion de deudas
    if not table_exists('amortization_schedules'):
        op.create_table(
            'amortization_schedules',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('debt_id', sa.String(36), sa.ForeignKey('debts.id'), nullable=False, index=True),
            sa.Column('month_number', sa.Integer, nullable=False),
            sa.Column('payment_date', sa.Date, nullable=False),
            sa.Column('payment_amount', sa.Numeric(15, 2), nullable=False),
            sa.Column('principal_portion', sa.Numeric(15, 2), nullable=False),
            sa.Column('interest_portion', sa.Numeric(15, 2), nullable=False),
            sa.Column('remaining_balance', sa.Numeric(15, 2), nullable=False),
            sa.Column('cumulative_interest', sa.Numeric(15, 2), nullable=False),
            sa.Column('is_paid', sa.Boolean, default=False, nullable=False),
            sa.Column('paid_at', sa.DateTime, nullable=True),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        )

    # 3. detected_patterns - Patrones de gasto recurrente detectados
    if not table_exists('detected_patterns'):
        op.create_table(
            'detected_patterns',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('household_id', sa.String(36), sa.ForeignKey('households.id'), nullable=False, index=True),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('type', sa.String(20), nullable=False),  # income, expense
            sa.Column('avg_amount', sa.Numeric(15, 2), nullable=False),
            sa.Column('avg_day_of_month', sa.Integer, nullable=True),
            sa.Column('frequency', sa.String(20), nullable=False),  # monthly, weekly, biweekly
            sa.Column('occurrences', sa.Integer, nullable=False, default=1),
            sa.Column('confidence', sa.Integer, nullable=False, default=50),  # 0-100
            sa.Column('source', sa.String(50), nullable=False),  # transaction, event, manual
            sa.Column('source_id', sa.String(36), nullable=True),
            sa.Column('category_id', sa.String(36), sa.ForeignKey('categories.id'), nullable=True),
            sa.Column('account_id', sa.String(36), sa.ForeignKey('accounts.id'), nullable=True),
            sa.Column('first_seen', sa.Date, nullable=False),
            sa.Column('last_seen', sa.Date, nullable=False),
            sa.Column('is_confirmed', sa.Boolean, default=False, nullable=False),
            sa.Column('is_rejected', sa.Boolean, default=False, nullable=False),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        )


def downgrade() -> None:
    if table_exists('detected_patterns'):
        op.drop_table('detected_patterns')
    if table_exists('amortization_schedules'):
        op.drop_table('amortization_schedules')
    if table_exists('account_balance_history'):
        op.drop_table('account_balance_history')
