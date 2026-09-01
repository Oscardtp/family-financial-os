"""add financial_events table

Revision ID: f1a2b3c4d5e6
Revises: e5f6a7b8c9d0
Create Date: 2026-08-27 10:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('financial_events',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('household_id', sa.String(length=36), nullable=False),
    sa.Column('source', sa.String(length=20), nullable=False),
    sa.Column('source_id', sa.String(length=36), nullable=True),
    sa.Column('type', sa.String(length=20), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.Column('due_date', sa.Date(), nullable=False),
    sa.Column('recommended_date', sa.Date(), nullable=True),
    sa.Column('cutoff_date', sa.Date(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('account_id', sa.String(length=36), nullable=True),
    sa.Column('responsible_member_id', sa.String(length=36), nullable=True),
    sa.Column('is_recurrent', sa.Boolean(), nullable=True),
    sa.Column('recurrence_group_id', sa.String(length=36), nullable=True),
    sa.Column('reminder_days_before', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('paid_at', sa.DateTime(), nullable=True),
    sa.Column('paid_amount', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('paid_by', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['household_id'], ['households.id']),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id']),
    sa.ForeignKeyConstraint(['responsible_member_id'], ['users.id']),
    sa.ForeignKeyConstraint(['paid_by'], ['users.id']),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_financial_events_household_due', 'financial_events', ['household_id', 'due_date'], unique=False)
    op.create_index('ix_financial_events_household_status', 'financial_events', ['household_id', 'status'], unique=False)
    op.create_index('ix_financial_events_source', 'financial_events', ['source', 'source_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_financial_events_source', table_name='financial_events')
    op.drop_index('ix_financial_events_household_status', table_name='financial_events')
    op.drop_index('ix_financial_events_household_due', table_name='financial_events')
    op.drop_table('financial_events')
