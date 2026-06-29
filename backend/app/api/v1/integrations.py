"""Интеграция MTUCI/TECH: статус, синхронизация, отключение.

Скелет — реализация в issue [BE-M3].
"""
from fastapi import APIRouter

router = APIRouter(prefix="/integrations/mtuci", tags=["integrations"])


@router.get("/status")
async def integration_status() -> dict:
    """Статус подключения интеграции. TODO: [BE-M3]."""
    raise NotImplementedError


@router.post("/sync")
async def integration_sync() -> dict:
    """Синхронизация профиля и расписания по сохранённому токену. TODO: [BE-M3]."""
    raise NotImplementedError


@router.delete("/disconnect")
async def integration_disconnect() -> dict:
    """Отключение интеграции, удаление токена. TODO: [BE-M3]."""
    raise NotImplementedError
