"""Add is_reversed to debt_payments (NEUTRALIZADA — ver HF4)

La columna is_reversed ya es creada por la revision c3d4e5f6g7h8
(fix_schema_gaps_phase2.py:118). Ejecutar add_column aqui duplicaba el DDL y
rompia `alembic upgrade head` en instalaciones limpias.

Esta revision se conserva en la cadena porque es down_revision de
b2c3d4e5f6a7 y de m1a2b3c4d5e6: eliminarla obligaria a reescribir esas dos
revisiones y dejaria inaccesibles las bases ya estampadas en d4e5f6g7h8i9.

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-09-18
"""
from alembic import op

revision = "d4e5f6g7h8i9"
down_revision = "c3d4e5f6g7h8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # HF4: no-op. El ADD COLUMN lo ejecuta c3d4e5f6g7h8 (fix_schema_gaps_phase2.py:118).
    pass


def downgrade() -> None:
    # HF4: no-op. El DROP COLUMN lo ejecuta c3d4e5f6g7h8 (fix_schema_gaps_phase2.py),
    # manteniendo simetría add/drop en la misma revision.
    pass
