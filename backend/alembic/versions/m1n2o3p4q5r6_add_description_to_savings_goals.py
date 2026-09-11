"""add description to savings_goals

Revision ID: m1n2o3p4q5r6
Revises: k1l2m3n4o5p6
Create Date: 2026-09-07

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision = 'm1n2o3p4q5r6'
down_revision = 'k1l2m3n4o5p6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    result = bind.execute(sa.text(
        "PRAGMA table_info(savings_goals)"
    ))
    columns = [row[1] for row in result.fetchall()]
    if 'description' not in columns:
        op.add_column('savings_goals', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('savings_goals', 'description')
