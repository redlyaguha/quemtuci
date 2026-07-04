"""Интеграция MTUCI/TECH: статус, синхронизация, отключение [BE-M3]."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_session
from app.models.integration import ExternalIntegration, IntegrationProvider, IntegrationStatus
from app.schemas.auth import UserPublic
from app.services.mtuci_tech_service import MtuciTechService
from app.services.token_crypto import decrypt_token

router = APIRouter(prefix="/integrations/mtuci", tags=["integrations"])


@router.get("/status")
async def integration_status(
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> dict:
    """Статус подключения интеграции. [BE-M3]"""
    integration = await _get_integration(session, current_user.id)
    if integration is None:
        return {"connected": False, "status": "disconnected"}

    return {
        "connected": integration.status == IntegrationStatus.connected,
        "status": integration.status.value,
        "last_sync_at": integration.last_sync_at,
        "error_message": integration.error_message,
    }


@router.post("/sync")
async def integration_sync(
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> dict:
    """Синхронизация профиля и расписания по сохранённому токену. [BE-M3]"""
    integration = await _get_integration(session, current_user.id)
    if integration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Интеграция не подключена")

    token = decrypt_token(integration.encrypted_token)
    service = MtuciTechService()
    try:
        payload = await service.sync_user_data(current_user, token)
    except Exception as exc:
        integration.status = IntegrationStatus.error
        integration.error_message = str(exc)
        await session.commit()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Ошибка синхронизации")

    integration.status = IntegrationStatus.connected
    integration.error_message = None
    integration.last_sync_at = datetime.now(timezone.utc)
    await session.commit()
    return {
        "status": "connected",
        "profile": payload["profile"],
        "timetable_count": len(payload["timetable"]),
        "exams_count": len(payload["exams"]),
    }


@router.delete("/disconnect")
async def integration_disconnect(
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> dict:
    """Отключение интеграции, удаление токена. [BE-M3]"""
    integration = await _get_integration(session, current_user.id)
    if integration is not None:
        await session.delete(integration)
        await session.commit()
    return {"connected": False, "status": "disconnected"}


async def _get_integration(session: AsyncSession, user_id) -> ExternalIntegration | None:
    result = await session.execute(
        select(ExternalIntegration).where(
            ExternalIntegration.user_id == user_id,
            ExternalIntegration.provider == IntegrationProvider.mtuci,
        )
    )
    return result.scalars().first()
