"""create initial application schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    estado_tramite = postgresql.ENUM(
        "BORRADOR",
        "EN_REVISION",
        "LISTO_RADICAR",
        "RADICADO",
        "APROBADO",
        "DEVUELTO",
        name="estadotramite",
        create_type=False,
    )
    tipo_estado = postgresql.ENUM(
        "BORRADOR",
        "EN_REVISION",
        "LISTO_RADICAR",
        "RADICADO",
        "APROBADO",
        "DEVUELTO",
        name="estadotramite",
    )
    tipo_estado.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("nit", sa.String(), nullable=False),
        sa.Column("representante_legal", sa.String()),
        sa.Column("direccion", sa.String()),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("nit", name="uq_clientes_nit"),
    )
    op.create_table(
        "tramites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cliente_id", sa.Integer(), sa.ForeignKey("clientes.id")),
        sa.Column("tipo_tramite", sa.String(), nullable=True),
        sa.Column("estado", estado_tramite, nullable=True),
        sa.Column("datos_formulario", sa.JSON(), nullable=True),
        sa.Column("datos_normalizados", sa.JSON(), nullable=True),
        sa.Column("autoridad_sigla", sa.String(), nullable=True),
        sa.Column("municipio_dane", sa.String(), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("radicado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("numero_radicado", sa.String(), nullable=True),
    )
    op.create_table(
        "documentos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tramite_id", sa.Integer(), sa.ForeignKey("tramites.id")),
        sa.Column("tipo", sa.String(), nullable=True),
        sa.Column("nombre", sa.String(), nullable=True),
        sa.Column("ruta", sa.String(), nullable=True),
        sa.Column("generado_en", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("documentos")
    op.drop_table("tramites")
    op.drop_table("clientes")
    postgresql.ENUM(name="estadotramite").drop(op.get_bind(), checkfirst=True)
