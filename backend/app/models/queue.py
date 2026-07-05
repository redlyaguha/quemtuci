"""Модели Queue и QueueMember (ТЗ §3, §12). Реализация — [BE-Q1]."""
import enum
import uuid
from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, Time, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class QueueType(str, enum.Enum):
    lab      = "Лабораторная"
    consult  = "Консультация"
    defense  = "Защита"
    retake   = "Пересдача"
    practice = "practice_defense"


class QueueStatus(str, enum.Enum):
    open   = "open"
    live   = "live"
    closed = "closed"


class Queue(Base):
    __tablename__ = "queues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    discipline: Mapped[str] = mapped_column(String(255), nullable=False)
    group_name: Mapped[str] = mapped_column(String(64), nullable=False)
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    room: Mapped[str] = mapped_column(String(64), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    time_start: Mapped[time] = mapped_column(Time, nullable=False)
    time_end: Mapped[time | None] = mapped_column(Time, nullable=True)
    type: Mapped[QueueType] = mapped_column(
        Enum(QueueType, name="queue_type", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    status: Mapped[QueueStatus] = mapped_column(
        Enum(QueueStatus, name="queue_status"), nullable=False, default=QueueStatus.open
    )
    max_students: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    members: Mapped[list["QueueMember"]] = relationship(
        "QueueMember", back_populates="queue",
        cascade="all, delete-orphan", order_by="QueueMember.position",
        lazy="selectin",
    )


class QueueMember(Base):
    __tablename__ = "queue_members"
    __table_args__ = (
        UniqueConstraint("queue_id", "student_id", name="uq_queue_members_queue_student"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    queue_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("queues.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    # Стабильный номер-талон — не меняется при перемещениях других участников
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    queue: Mapped["Queue"] = relationship("Queue", back_populates="members")
