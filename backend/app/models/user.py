"""Модель User (ТЗ §12). Реализация — [BE-A1].

Поля: id, full_name, first_name, last_name, role, group_name,
mtuci_user_id, mtuci_role, mtuci_group_id, teacher_id, created_at, updated_at.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserRole(str, enum.Enum):
    """Роли пользователя. Должны соответствовать типу Role на фронте."""

    student = "student"
    teacher = "teacher"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(128))
    last_name: Mapped[str | None] = mapped_column(String(128))

    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    group_name: Mapped[str | None] = mapped_column(String(64))

    # Идентификаторы из внешней системы MTUCI/TECH (ТЗ §5, §6) — используются
    # для сопоставления расписания и профиля, не для авторизации.
    mtuci_user_id: Mapped[str | None] = mapped_column(String(64), unique=True)
    mtuci_role: Mapped[str | None] = mapped_column(String(64))
    mtuci_group_id: Mapped[str | None] = mapped_column(String(64))
    teacher_id: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
