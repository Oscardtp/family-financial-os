"""add refresh_tokens table (guardada para instalaciones existentes)

HF4.5: la tabla de RefreshTokenModel (app/infrastructure/models/models.py:441)
nunca tuvo migración. Existía solo en la DB real (creada fuera de Alembic),
por lo que una instalación limpia quedaba sin ella y `POST /auth/register` y
`/auth/login` respondían 500 (app/presentation/deps.py:60 inserta en
refresh_tokens).

El CREATE es condicional: en las bases que ya la tienen esta revisión no
hace nada, así que es segura para la DB existente.

Revision ID: g7h8i9j0k1l2
Revises: f6a7b8c9d0e1
Create Date: 2026-09-25
"""
from alembic import op
import sqlalchemy as sa

revision = "g7h8i9j0k1l2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if sa.inspect(op.get_bind()).has_table("refresh_tokens"):
        return

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("jti", sa.String(36), nullable=False, unique=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    # Simétrico al upgrade: si la tabla existe se elimina. Sin este paso,
    # `alembic downgrade base` falla porque refresh_tokens_user_id_fkey
    # impide dropear users. Una reinstalación posterior la recrea vacía;
    # solo se invalidan sesiones (los datos financieros no se tocan).
    if sa.inspect(op.get_bind()).has_table("refresh_tokens"):
        op.drop_table("refresh_tokens")
