"""create documents tables

Revision ID: 194413662b03
Revises: f3ed23192b83
Create Date: 2026-06-30 23:54:18.367603

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '194413662b03'
down_revision: Union[str, Sequence[str], None] = 'f3ed23192b83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

document_type = postgresql.ENUM("PDF", "DOCX", name="document_type")
document_status = postgresql.ENUM("uploading", "indexing", "done", "error", name="document_status")


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_type", document_type, nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("status", document_status, nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_id", sa.String(length=128), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("elasticsearch_id", sa.String(length=128), nullable=True),
    )
    op.create_unique_constraint("uq_document_chunks_chunk_id", "document_chunks", ["chunk_id"])
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("document_chunks")
    op.drop_table("documents")
    document_status.drop(op.get_bind(), checkfirst=True)
    document_type.drop(op.get_bind(), checkfirst=True)
