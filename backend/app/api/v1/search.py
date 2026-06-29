"""Поиск по базе знаний и история запросов.

Скелет — реализация в issue [BE-S3], [BE-S4].
"""
from fastapi import APIRouter

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
async def search(q: str) -> dict:
    """Полнотекстовый поиск (multi_match по text), с подсветкой. TODO: [BE-S3]."""
    raise NotImplementedError


@router.get("/history")
async def search_history() -> list:
    """История запросов пользователя. TODO: [BE-S4]."""
    raise NotImplementedError


@router.delete("/history")
async def clear_search_history() -> dict:
    """Очистка истории запросов. TODO: [BE-S4]."""
    raise NotImplementedError
