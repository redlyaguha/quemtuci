"""create lessons and exam events

Revision ID: d5e6f7a8b9c3
Revises: c4d5e6f7a8b2
Create Date: 2026-07-04 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "d5e6f7a8b9c3"
down_revision: Union[str, Sequence[str], None] = "c4d5e6f7a8b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("group_name", sa.String(64), nullable=True),
        sa.Column("source", sa.String(32), nullable=False, server_default="mtuci"),
        sa.Column("external_id", sa.String(128), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("day", sa.String(32), nullable=True),
        sa.Column("parity", sa.String(32), nullable=True),
        sa.Column("number", sa.Integer(), nullable=True),
        sa.Column("time_start", sa.Time(), nullable=True),
        sa.Column("time_end", sa.Time(), nullable=True),
        sa.Column("discipline", sa.String(255), nullable=False),
        sa.Column("lesson_type", sa.String(64), nullable=True),
        sa.Column("room", sa.String(64), nullable=True),
        sa.Column("teachers", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("is_online", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_exam", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("raw_json", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_lessons_user_date", "lessons", ["user_id", "date"])

    op.create_table(
        "exam_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("group_name", sa.String(64), nullable=True),
        sa.Column("source", sa.String(32), nullable=False, server_default="mtuci"),
        sa.Column("external_id", sa.String(128), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("time_start", sa.Time(), nullable=True),
        sa.Column("time_end", sa.Time(), nullable=True),
        sa.Column("discipline", sa.String(255), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=True),
        sa.Column("room", sa.String(64), nullable=True),
        sa.Column("teachers", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("link", sa.Text(), nullable=True),
        sa.Column("raw_json", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_exam_events_user_date", "exam_events", ["user_id", "date"])


def downgrade() -> None:
    op.drop_index("ix_exam_events_user_date", table_name="exam_events")
    op.drop_table("exam_events")
    op.drop_index("ix_lessons_user_date", table_name="lessons")
    op.drop_table("lessons")
