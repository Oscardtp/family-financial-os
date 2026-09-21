"""merge alembic heads d4e5f6g7h8i9 and d4e5f6a7b8c9

Revision ID: m1a2b3c4d5e6
Revises: d4e5f6g7h8i9, d4e5f6a7b8c9
Create Date: 2026-09-20 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'm1a2b3c4d5e6'
down_revision: Union[str, None] = ('d4e5f6g7h8i9', 'd4e5f6a7b8c9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
