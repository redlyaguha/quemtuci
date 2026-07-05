"""add content column to documents (original file bytes for download)

Revision ID: e6f7a8b9c3d4
Revises: d5e6f7a8b9c3
Create Date: 2026-07-05 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e6f7a8b9c3d4"
down_revision: Union[str, Sequence[str], None] = "d5e6f7a8b9c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("content", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "content")
