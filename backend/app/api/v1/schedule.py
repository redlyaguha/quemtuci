"""Расписание и события, включая защиту практики [BE-M4]."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_session
from app.models.integration import ExternalIntegration, IntegrationProvider
from app.schemas.auth import UserPublic
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


@router.post("/practice-defense/create-queue")
async def create_practice_defense_queue() -> dict:
    """Создать очередь на защиту практики 06.07.2026. TODO: [BE-P1]/[FE-P2]."""
    raise NotImplementedError


async def _get_mtuci_integration(session: AsyncSession, user_id) -> ExternalIntegration | None:
    result = await session.execute(
        select(ExternalIntegration).where(
            ExternalIntegration.user_id == user_id,
            ExternalIntegration.provider == IntegrationProvider.mtuci,
        )
    )
    return result.scalars().first()
