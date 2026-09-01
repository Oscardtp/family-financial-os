"""add preferences table and extend savings_goals

Revision ID: e5f6a7b8c9d0
Revises: d0431b0b55d0
Create Date: 2026-08-25 18:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd0431b0b55d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('category_account_preferences',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('household_id', sa.String(length=36), nullable=False),
    sa.Column('category_id', sa.String(length=36), nullable=False),
    sa.Column('account_id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['household_id'], ['households.id']),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id']),
    sa.PrimaryKeyConstraint('id')
    )

    op.add_column('savings_goals', sa.Column('goal_type', sa.String(length=20), nullable=True))
    op.add_column('savings_goals', sa.Column('expected_return_rate', sa.Numeric(precision=5, scale=2), nullable=True))
    op.add_column('savings_goals', sa.Column('horizon_months', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('savings_goals', 'horizon_months')
    op.drop_column('savings_goals', 'expected_return_rate')
    op.drop_column('savings_goals', 'goal_type')
    op.drop_table('category_account_preferences')
