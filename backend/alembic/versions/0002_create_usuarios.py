"""create users table

Revision ID: 0002_create_usuarios
Revises: 0001_initial_schema
Create Date: 2026-08-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_create_usuarios"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("rol", sa.String(length=30), nullable=False, server_default="cliente"),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email", name="uq_usuarios_email"),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_table("usuarios")
