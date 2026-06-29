"""Расписание и события, включая защиту практики.

Скелет — реализация в issue [BE-M4], [BE-P1], [FE-P2].
"""
from fastapi import APIRouter

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("/my")
async def my_schedule() -> dict:
    """Моё расписание. TODO: [BE-M4]."""
    raise NotImplementedError


@router.get("/events")
async def events() -> list:
    """События (включая защиту практики). TODO: [BE-M4]/[BE-P1]."""
    raise NotImplementedError


@router.post("/practice-defense/create-queue")
async def create_practice_defense_queue() -> dict:
    """Создать очередь на защиту практики 06.07.2026. TODO: [BE-P1]/[FE-P2]."""
    raise NotImplementedError
