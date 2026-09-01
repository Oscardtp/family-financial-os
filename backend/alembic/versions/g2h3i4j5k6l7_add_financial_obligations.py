"""add financial_obligations and extend financial_events

Revision ID: g2h3i4j5k6l7
Revises: f1a2b3c4d5e6
Create Date: 2026-08-27 15:19:00.000000
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op


revision: str = 'g2h3i4j5k6l7'
down_revision: Union[str, None] = ('f1a2b3c4d5e6', 'b3c4d5e6f7a8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'financial_obligations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('household_id', sa.String(length=36), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('source_id', sa.String(length=36), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('frequency', sa.String(length=20), nullable=True),
        sa.Column('anchor_day', sa.Integer(), nullable=True),
        sa.Column('recommended_offset_days', sa.Integer(), nullable=True),
        sa.Column('cutoff_offset_days', sa.Integer(), nullable=True),
        sa.Column('reminder_days_before', sa.Integer(), nullable=True),
        sa.Column('account_id', sa.String(length=36), nullable=True),
        sa.Column('category_id', sa.String(length=36), nullable=True),
        sa.Column('responsible_member_id', sa.String(length=36), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('confidence', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['household_id'], ['households.id']),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id']),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.ForeignKeyConstraint(['responsible_member_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_financial_obligations_household',
        'financial_obligations',
        ['household_id'],
        unique=False,
    )
    op.create_index(
        'ix_financial_obligations_source',
        'financial_obligations',
        ['source', 'source_id'],
        unique=False,
    )

    op.add_column('financial_events', sa.Column('obligation_id', sa.String(length=36), nullable=True))
    op.add_column('financial_events', sa.Column('visibility', sa.String(length=12), nullable=True))
    op.add_column('financial_events', sa.Column('confidence', sa.Integer(), nullable=True))
    op.add_column('financial_events', sa.Column('payment_method', sa.String(length=12), nullable=True))
    op.add_column('financial_events', sa.Column('consequence_note', sa.Text(), nullable=True))

    op.create_index(
        'ix_financial_events_obligation',
        'financial_events',
        ['obligation_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_financial_events_obligation', table_name='financial_events')
    op.drop_column('financial_events', 'consequence_note')
    op.drop_column('financial_events', 'payment_method')
    op.drop_column('financial_events', 'confidence')
    op.drop_column('financial_events', 'visibility')
    op.drop_column('financial_events', 'obligation_id')
    op.drop_index('ix_financial_obligations_source', table_name='financial_obligations')
    op.drop_index('ix_financial_obligations_household', table_name='financial_obligations')
    op.drop_table('financial_obligations')
