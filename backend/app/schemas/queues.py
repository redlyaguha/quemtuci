"""Pydantic-схемы для queues-эндпоинтов.

Контракт совпадает с TypeScript-типами Queue, QueueMember, QueueCreate на фронтенде.
"""
from __future__ import annotations

import uuid
from datetime import date, time

from pydantic import BaseModel, Field

from app.models.queue import QueueStatus, QueueType


class QueueMemberOut(BaseModel):
    id: int
    userId: uuid.UUID
    name: str = ""
    seq: int
    position: int
    passed: bool = False
    grade: int | None = None

    model_config = {"from_attributes": True}


class QueueOut(BaseModel):
    id: int
    title: str
    discipline: str
    qtype: str
    teacher: str = ""
    room: str
    group: str
    when: str          # ISO datetime строка для фронтенда
    max: int
    status: str
    comment: str | None = None
    students: list[QueueMemberOut] = []

    model_config = {"from_attributes": True}


class QueueCreate(BaseModel):
    title: str
    discipline: str
    qtype: QueueType
    group: str
    room: str
    date: date
    time_start: time
    time_end: time | None = None
    max: int = Field(default=30, ge=1, le=200)
    comment: str | None = None


class ReorderRequest(BaseModel):
    order: list[int]  # список member_id в новом порядке
