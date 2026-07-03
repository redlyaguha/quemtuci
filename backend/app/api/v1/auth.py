"""Авторизация: демо-вход, текущий пользователь.

BE-A2: POST /auth/demo — выдаёт JWT для тестовых ролей.
BE-A3: GET  /auth/me  — возвращает профиль по JWT.
BE-M3: POST /auth/mtuci-token — вход по токену MTUCI/TECH (TODO).
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from app.core.security import create_access_token, get_current_user
from app.models.user import UserRole
from app.schemas.auth import AuthResponse, DemoLoginRequest, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])

# Тестовые пользователи из README / ТЗ §12 — фиксированные UUID для воспроизводимости.
_DEMO_USERS: dict[UserRole, UserPublic] = {
    UserRole.student: UserPublic(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        name="Вадим Рыбаченок",
        role=UserRole.student,
        group="БПИ2403",
    ),
    UserRole.teacher: UserPublic(
        id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        name="Мосева Марина Сергеевна",
        role=UserRole.teacher,
        department="Кафедра",
    ),
    UserRole.admin: UserPublic(
        id=uuid.UUID("00000000-0000-0000-0000-000000000003"),
        name="Администратор",
        role=UserRole.admin,
    ),
}


@router.post(
    "/demo",
    response_model=AuthResponse,
    summary="Демо-вход",
    response_description="JWT-токен и профиль пользователя",
    responses={
        422: {"description": "Недопустимое значение role (ожидается student / teacher / admin)"},
    },
)
async def demo_login(body: DemoLoginRequest) -> AuthResponse:
    """Выдаёт JWT без пароля для тестирования.

    Укажите желаемую роль — получите токен с соответствующими правами.
    Срок действия токена — 24 часа.
    """
    user = _DEMO_USERS[body.role]
    return AuthResponse(access_token=create_access_token(user), user=user)


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Профиль текущего пользователя",
    response_description="Данные из JWT-токена (без обращения к БД)",
    responses={
        401: {"description": "Токен отсутствует, истёк или недействителен"},
    },
)
async def me(current_user: UserPublic = Depends(get_current_user)) -> UserPublic:
    """Возвращает профиль, закодированный в JWT.

    Не выполняет запрос к базе данных — все данные берутся из токена.
    """
    return current_user


@router.post(
    "/mtuci-token",
    summary="Вход по токену МТУСИ (не реализован)",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    include_in_schema=False,
)
async def mtuci_token_login() -> dict:
    """Вход по пользовательскому MTUCI/TECH-токену. TODO: [BE-M3]."""
    raise NotImplementedError
