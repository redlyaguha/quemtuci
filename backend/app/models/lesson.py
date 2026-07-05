"""Модели Lesson и ExamEvent (ТЗ §7, §12). Реализация — [BE-M4]."""
import uuid
from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, Time, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    group_name: Mapped[str | None] = mapped_column(String(64))
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="mtuci")
    external_id: Mapped[str | None] = mapped_column(String(128))
    date: Mapped[date] = mapped_column(Date, nullable=False)
    day: Mapped[str | None] = mapped_column(String(32))
    parity: Mapped[str | None] = mapped_column(String(32))
    number: Mapped[int | None] = mapped_column(Integer)
    time_start: Mapped[time | None] = mapped_column(Time)
    time_end: Mapped[time | None] = mapped_column(Time)
    discipline: Mapped[str] = mapped_column(String(255), nullable=False)
    lesson_type: Mapped[str | None] = mapped_column(String(64))
    room: Mapped[str | None] = mapped_column(String(64))
    teachers: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    comment: Mapped[str | None] = mapped_column(Text)
    is_online: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_exam: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    raw_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ExamEvent(Base):
    __tablename__ = "exam_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    group_name: Mapped[str | None] = mapped_column(String(64))
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="mtuci")
    external_id: Mapped[str | None] = mapped_column(String(128))
    date: Mapped[date] = mapped_column(Date, nullable=False)
    time_start: Mapped[time | None] = mapped_column(Time)
    time_end: Mapped[time | None] = mapped_column(Time)
    discipline: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str | None] = mapped_column(String(64))
    room: Mapped[str | None] = mapped_column(String(64))
    teachers: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    comment: Mapped[str | None] = mapped_column(Text)
    link: Mapped[str | None] = mapped_column(Text)
    raw_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
