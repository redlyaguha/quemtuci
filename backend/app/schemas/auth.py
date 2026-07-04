"""Pydantic-схемы для auth-эндпоинтов.

Контракт соответствует TypeScript-типам User и AuthResponse на фронтенде.
"""
from __future__ import annotations

import uuid

from pydantic import BaseModel

from app.models.user import UserRole


class DemoLoginRequest(BaseModel):
    role: UserRole

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"role": "student"},
                {"role": "teacher"},
                {"role": "admin"},
            ]
        }
    }


class UserPublic(BaseModel):
    """Публичное представление пользователя (ответ /auth/demo и /auth/me)."""

    id: uuid.UUID
    name: str
    role: UserRole
    group: str | None = None
    department: str | None = None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
