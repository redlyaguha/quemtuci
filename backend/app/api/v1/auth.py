"""Авторизация: демо-вход, вход по MTUCI/TECH-токену, текущий пользователь.

Скелет — реализация в issue [BE-A2], [BE-A3], [BE-M3].
"""
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/demo")
async def demo_login() -> dict:
    """Демо-вход для ролей student/teacher/admin. TODO: [BE-A2]."""
    raise NotImplementedError


@router.post("/mtuci-token")
async def mtuci_token_login() -> dict:
    """Вход по пользовательскому MTUCI/TECH-токену. TODO: [BE-M3]."""
    raise NotImplementedError


@router.get("/me")
async def me() -> dict:
    """Текущий пользователь по JWT. TODO: [BE-A3]."""
    raise NotImplementedError
