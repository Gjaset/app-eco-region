"""create drafts table for persistent versioned drafts

Revision ID: 0003_create_drafts
Revises: 0002_create_usuarios
Create Date: 2026-09-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_create_drafts"
down_revision: Union[str, None] = "0002_create_usuarios"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "drafts",
        sa.Column("draft_id", sa.String(128), primary_key=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("data", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("drafts")
