"""Расписание и события, включая защиту практики [BE-M4]."""
from __future__ import annotations

from datetime import date, time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, require_roles
from app.db.session import get_session
from app.models.integration import ExternalIntegration, IntegrationProvider
from app.models.queue import Queue, QueueStatus, QueueType
from app.models.user import UserRole
from app.schemas.queues import QueueOut
from app.schemas.auth import UserPublic
from app.api.v1.queues import _queue_to_out
from app.services.mtuci_tech_service import MtuciTechService
from app.services.schedule_normalizer import normalize_exams, normalize_lessons
from app.services.token_crypto import decrypt_token

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("/my")
async def my_schedule(
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> list[dict]:
    """Моё расписание. Пустой результат — не ошибка. [BE-M4]"""
    integration = await _get_mtuci_integration(session, current_user.id)
    if integration is None:
        return []

    token = decrypt_token(integration.encrypted_token)
    raw = await MtuciTechService().get_timetable(token)
    return normalize_lessons(raw)


@router.get("/events")
async def events(
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> list[dict]:
    """События и экзамены. Пустой результат — не ошибка. [BE-M4]"""
    integration = await _get_mtuci_integration(session, current_user.id)
    if integration is None:
        return []

    token = decrypt_token(integration.encrypted_token)
    raw = await MtuciTechService().get_exams(token)
    return normalize_exams(raw)


@router.post("/practice-defense/create-queue", response_model=QueueOut)
async def create_practice_defense_queue(
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_roles(UserRole.teacher, UserRole.admin)),
) -> QueueOut:
    """Создать или вернуть очередь на защиту практики 06.07.2026. [FE-INT]"""
    practice_date = date(2026, 7, 6)
    result = await session.execute(
        select(Queue).where(
            Queue.date == practice_date,
            Queue.group_name == "БПИ2403",
            Queue.type == QueueType.practice,
        )
    )
    queue = result.scalars().first()
    if queue is None:
        queue = Queue(
            title="Учебная практика (технологическая)",
            discipline="Учебная практика (технологическая)",
            group_name="БПИ2403",
            teacher_id=current_user.id,
            room="А-310",
            date=practice_date,
            time_start=time(13, 0),
            time_end=time(14, 30),
            type=QueueType.practice,
            status=QueueStatus.open,
            max_students=30,
            comment="Дифференцированный зачёт. Преподаватель: Мосева М.С.",
        )
        session.add(queue)
        await session.commit()
        await session.refresh(queue)

    return _queue_to_out(queue, teacher_name=current_user.name)


async def _get_mtuci_integration(session: AsyncSession, user_id) -> ExternalIntegration | None:
    result = await session.execute(
        select(ExternalIntegration).where(
            ExternalIntegration.user_id == user_id,
            ExternalIntegration.provider == IntegrationProvider.mtuci,
        )
    )
    return result.scalars().first()
