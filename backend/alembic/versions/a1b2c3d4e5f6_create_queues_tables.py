"""create queues and queue_members tables

Revision ID: a1b2c3d4e5f6
Revises: 95efa6218fcb
Create Date: 2026-07-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '95efa6218fcb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


queue_type = postgresql.ENUM(
    "Лабораторная", "Консультация", "Защита", "Пересдача", "practice_defense",
    name="queue_type",
)
queue_status = postgresql.ENUM("open", "live", "closed", name="queue_status")


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "queues",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("discipline", sa.String(255), nullable=False),
        sa.Column("group_name", sa.String(64), nullable=False),
        sa.Column(
            "teacher_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("room", sa.String(64), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("time_start", sa.Time(), nullable=False),
        sa.Column("time_end", sa.Time(), nullable=True),
        sa.Column("type", queue_type, nullable=False),
        sa.Column("status", queue_status, nullable=False, server_default="open"),
        sa.Column("max_students", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "queue_members",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "queue_id",
            sa.Integer(),
            sa.ForeignKey("queues.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("grade", sa.Integer(), nullable=True),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index("ix_queue_members_queue_id", "queue_members", ["queue_id"])
    op.create_index("ix_queue_members_student_id", "queue_members", ["student_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("queue_members")
    op.drop_table("queues")
    queue_status.drop(op.get_bind(), checkfirst=True)
    queue_type.drop(op.get_bind(), checkfirst=True)
