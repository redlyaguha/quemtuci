"""Авторизация: демо-вход, текущий пользователь.

BE-A2: POST /auth/demo — выдаёт JWT для тестовых ролей.
BE-A3: GET  /auth/me  — возвращает профиль по JWT.
BE-M3: POST /auth/mtuci-token — вход по токену MTUCI/TECH (TODO).
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_current_user
from app.db.session import get_session
from app.models.integration import ExternalIntegration, IntegrationProvider, IntegrationStatus
from app.models.user import User, UserRole
from app.schemas.auth import AuthResponse, DemoLoginRequest, MtuciTokenLoginRequest, UserPublic
from app.services.mtuci_tech_service import MtuciTechService
from app.services.token_crypto import encrypt_token

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
    response_model=AuthResponse,
    summary="Вход по токену МТУСИ",
    response_description="JWT-токен и профиль локального пользователя",
    responses={
        400: {"description": "Пустой или недействительный MTUCI/TECH-токен"},
    },
)
async def mtuci_token_login(
    body: MtuciTokenLoginRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """Вход по пользовательскому MTUCI/TECH-токену. [BE-M3]"""
    token = body.token.strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пустой MTUCI-токен")

    service = MtuciTechService()
    try:
        profile = await service.authenticate_by_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except NotImplementedError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Живая интеграция MTUCI/TECH не настроена",
        )

    user = await _upsert_mtuci_user(session, profile)
    public = _user_to_public(user)
    await _upsert_mtuci_integration(session, user.id, token)
    await session.commit()

    return AuthResponse(access_token=create_access_token(public), user=public)


async def _upsert_mtuci_user(session: AsyncSession, profile: dict) -> User:
    mtuci_user_id = profile["mtuci_user_id"]
    result = await session.execute(select(User).where(User.mtuci_user_id == mtuci_user_id))
    user = result.scalars().first()

    role = UserRole(profile.get("role") or UserRole.student.value)
    if user is None:
        user = User(full_name=profile["full_name"], role=role)
        if profile.get("id") is not None:
            user.id = profile["id"]
        session.add(user)

    user.full_name = profile["full_name"]
    user.first_name = profile.get("first_name")
    user.last_name = profile.get("last_name")
    user.role = role
    user.group_name = profile.get("group_name")
    user.mtuci_user_id = mtuci_user_id
    user.mtuci_role = profile.get("mtuci_role")
    user.mtuci_group_id = profile.get("mtuci_group_id")
    user.teacher_id = profile.get("teacher_id")
    await session.flush()
    return user


async def _upsert_mtuci_integration(session: AsyncSession, user_id, token: str) -> None:
    result = await session.execute(
        select(ExternalIntegration).where(
            ExternalIntegration.user_id == user_id,
            ExternalIntegration.provider == IntegrationProvider.mtuci,
        )
    )
    integration = result.scalars().first()
    if integration is None:
        integration = ExternalIntegration(
            user_id=user_id,
            provider=IntegrationProvider.mtuci,
            encrypted_token=encrypt_token(token),
            status=IntegrationStatus.connected,
        )
        session.add(integration)
    else:
        integration.encrypted_token = encrypt_token(token)
        integration.status = IntegrationStatus.connected
        integration.error_message = None


def _user_to_public(user: User) -> UserPublic:
    return UserPublic(
        id=user.id,
        name=user.full_name,
        role=user.role,
        group=user.group_name if user.role == UserRole.student else None,
        department="Кафедра" if user.role == UserRole.teacher else None,
    )
