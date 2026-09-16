"""create solicitudes table for exported document copies

Revision ID: 0004_create_solicitudes
Revises: 0003_create_drafts
Create Date: 2026-09-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_create_solicitudes"
down_revision: Union[str, None] = "0003_create_drafts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "solicitudes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False, server_default="fun"),
        sa.Column("nombre_archivo", sa.String(255), nullable=False),
        sa.Column("ruta_archivo", sa.String(512), nullable=False),
        sa.Column("tamano_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("resumen", sa.JSON(), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_solicitudes_usuario_id", "solicitudes", ["usuario_id"])
    op.create_index("ix_solicitudes_creado_en", "solicitudes", ["creado_en"])


def downgrade() -> None:
    op.drop_index("ix_solicitudes_creado_en", table_name="solicitudes")
    op.drop_index("ix_solicitudes_usuario_id", table_name="solicitudes")
    op.drop_table("solicitudes")
