"""add estado to solicitudes for admin panel tracking

Revision ID: 0006_solicitud_estado
Revises: 0005_solicitud_contenido
Create Date: 2026-09-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_solicitud_estado"
down_revision: Union[str, None] = "0005_solicitud_contenido"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("solicitudes", sa.Column("estado", sa.String(30), nullable=False, server_default="pendiente"))


def downgrade() -> None:
    op.drop_column("solicitudes", "estado")