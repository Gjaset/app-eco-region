"""store exported document bytes in DB for serverless deployments

Revision ID: 0005_solicitud_contenido
Revises: 0004_create_solicitudes
Create Date: 2026-09-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_solicitud_contenido"
down_revision: Union[str, None] = "0004_create_solicitudes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("solicitudes", sa.Column("contenido", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column("solicitudes", "contenido")
