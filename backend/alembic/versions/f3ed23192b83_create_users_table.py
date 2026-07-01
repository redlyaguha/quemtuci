"""create users table

Revision ID: f3ed23192b83
Revises: 
Create Date: 2026-06-30 23:26:12.526859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f3ed23192b83'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_role = postgresql.ENUM("student", "teacher", "admin", name="user_role")


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=128), nullable=True),
        sa.Column("last_name", sa.String(length=128), nullable=True),
        sa.Column("role", user_role, nullable=False),
        sa.Column("group_name", sa.String(length=64), nullable=True),
        sa.Column("mtuci_user_id", sa.String(length=64), nullable=True),
        sa.Column("mtuci_role", sa.String(length=64), nullable=True),
        sa.Column("mtuci_group_id", sa.String(length=64), nullable=True),
        sa.Column("teacher_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint("uq_users_mtuci_user_id", "users", ["mtuci_user_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
    user_role.drop(op.get_bind(), checkfirst=True)
