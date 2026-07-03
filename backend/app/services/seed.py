"""Начальные данные: очередь защиты учебной практики [BE-P1].

Вызывается из lifespan при старте приложения (fault-tolerant).
Если очередь для БПИ2403 на 06.07.2026 уже существует — пропускает создание.
"""
from __future__ import annotations

import logging
import uuid
from datetime import date, time

from sqlalchemy import select

from app.db.session import async_session
from app.models.queue import Queue, QueueStatus, QueueType

log = logging.getLogger(__name__)

_TEACHER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
_PRACTICE_DATE = date(2026, 7, 6)
_PRACTICE_GROUP = "БПИ2403"


async def seed_practice_defense() -> None:
    """Создать очередь «Учебная практика» если её ещё нет."""
    try:
        async with async_session() as session:
            existing = await session.execute(
                select(Queue).where(
                    Queue.date == _PRACTICE_DATE,
                    Queue.group_name == _PRACTICE_GROUP,
                    Queue.type == QueueType.practice,
                )
            )
            if existing.scalars().first() is not None:
                return

            queue = Queue(
                title="Учебная практика (технологическая)",
                discipline="Учебная практика (технологическая)",
                group_name=_PRACTICE_GROUP,
                teacher_id=_TEACHER_ID,
                room="А-310",
                date=_PRACTICE_DATE,
                time_start=time(13, 0),
                time_end=time(14, 30),
                type=QueueType.practice,
                status=QueueStatus.open,
                max_students=30,
                comment="Дифференцированный зачёт. Преподаватель: Мосева М.С.",
            )
            session.add(queue)
            await session.commit()
            log.info("BE-P1: очередь защиты практики создана (id=%s)", queue.id)
    except Exception:
        log.warning("BE-P1: не удалось создать очередь практики (БД недоступна?)", exc_info=True)
