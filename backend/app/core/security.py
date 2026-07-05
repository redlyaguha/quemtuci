"""JWT и RBAC: создание токенов, зависимость get_current_user, проверка ролей.

Реализация — [BE-A3].
Токен содержит все поля UserPublic, чтобы /me и RBAC-проверки не делали DB-запрос.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.models.user import UserRole
from app.schemas.auth import UserPublic

_bearer = HTTPBearer(auto_error=False)


def create_access_token(user: UserPublic) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user.id),
        "name": user.name,
        "role": user.role.value,
        "group": user.group,
        "department": user.department,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def _decode(token: str) -> UserPublic:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный или просроченный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise credentials_error

    sub = payload.get("sub")
    role_str = payload.get("role")
    name = payload.get("name")
    if not sub or not role_str or not name:
        raise credentials_error

    try:
        role = UserRole(role_str)
    except ValueError:
        raise credentials_error

    return UserPublic(
        id=uuid.UUID(sub),
        name=name,
        role=role,
        group=payload.get("group"),
        department=payload.get("department"),
    )


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> UserPublic:
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен отсутствует",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _decode(creds.credentials)


def require_roles(*roles: UserRole) -> Callable[..., UserPublic]:
    """FastAPI-зависимость: проверяет роль текущего пользователя.

    Пример: Depends(require_roles(UserRole.admin, UserRole.teacher))
    """

    def _check(user: UserPublic = Depends(get_current_user)) -> UserPublic:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )
        return user

    return _check
