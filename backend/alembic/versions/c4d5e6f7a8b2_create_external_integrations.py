"""create external integrations

Revision ID: c4d5e6f7a8b2
Revises: b3c4d5e6f7a1
Create Date: 2026-07-04 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c4d5e6f7a8b2"
down_revision: Union[str, Sequence[str], None] = "b3c4d5e6f7a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


integration_provider = postgresql.ENUM("mtuci", name="integration_provider")
integration_status = postgresql.ENUM(
    "connected", "error", "disconnected", name="integration_status"
)


def upgrade() -> None:
    op.create_table(
        "external_integrations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", integration_provider, nullable=False),
        sa.Column("encrypted_token", sa.Text(), nullable=False),
        sa.Column(
            "status",
            integration_status,
            nullable=False,
            server_default="connected",
        ),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint(
            "user_id", "provider", name="uq_external_integrations_user_provider"
        ),
    )
    op.create_index("ix_external_integrations_user_id", "external_integrations", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_external_integrations_user_id", table_name="external_integrations")
    op.drop_table("external_integrations")
    integration_status.drop(op.get_bind(), checkfirst=True)
    integration_provider.drop(op.get_bind(), checkfirst=True)
