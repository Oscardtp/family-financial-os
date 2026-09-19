"""add debt notes column

Revision ID: e265573d3d5c
Revises: d0431b0b55d0
Create Date: 2026-09-17 17:02:47.023992
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'e265573d3d5c'
down_revision: Union[str, None] = 'd0431b0b55d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('debts', sa.Column('notes', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('debts', 'notes')
