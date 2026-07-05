"""Интеграция с tech.mtuci.ru по пользовательскому токену [BE-M2]."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.core.config import settings


_MOCK_PROFILE: dict[str, Any] = {
    "mtuci_user_id": "mock-student-001",
    "full_name": "Вадим Рыбаченок",
    "first_name": "Вадим",
    "last_name": "Рыбаченок",
    "role": "student",
    "group_name": "БПИ2403",
    "mtuci_role": "student",
    "mtuci_group_id": "2403",
}

_MOCK_TIMETABLE: list[dict[str, Any]] = [
    {
        "external_id": "lesson-2026-07-06-1",
        "date": "2026-07-06",
        "day": "Понедельник",
        "parity": "both",
        "number": 1,
        "time_start": "09:00",
        "time_end": "10:30",
        "discipline": "Алгоритмы и структуры данных",
        "lesson_type": "Лекция",
        "room": "А-310",
        "teachers": ["Иванов И.И."],
        "comment": "",
        "is_online": False,
    },
    {
        "external_id": "placeholder-empty",
        "date": "2026-07-06",
        "discipline": "--",
    },
]

_MOCK_EXAMS: list[dict[str, Any]] = [
    {
        "external_id": "exam-2026-07-10",
        "date": "2026-07-10",
        "time_start": "12:00",
        "time_end": "13:30",
        "discipline": "Базы данных",
        "event_type": "Экзамен",
        "room": "Б-204",
        "teachers": ["Петров П.П."],
        "comment": "",
        "link": None,
    },
    {
        "external_id": "placeholder-blank",
        "date": "2026-07-11",
        "discipline": "",
    },
]


class MtuciTechService:
    """Клиент MTUCI/TECH.

    В mock-режиме все методы возвращают локальные фикстуры и не выполняют сеть.
    Live-интеграция оставлена за границей текущего релиза, чтобы не хранить
    догадки о закрытом API портала в production-коде.
    """

    def __init__(self, mock: bool | None = None) -> None:
        self.mock = settings.mtuci_mock if mock is None else mock

    async def authenticate_by_token(self, token: str) -> dict[str, Any]:
        if not token.strip():
            raise ValueError("MTUCI token is empty")
        return await self.get_profile(token)

    async def get_profile(self, session: str) -> dict[str, Any]:
        self._ensure_mock(session)
        return deepcopy(_MOCK_PROFILE)

    async def get_timetable(self, session: str) -> list[dict[str, Any]]:
        self._ensure_mock(session)
        return deepcopy(_MOCK_TIMETABLE)

    async def get_timetable_week(self, session: str, week: int) -> list[dict[str, Any]]:
        self._ensure_mock(session)
        if week < 1:
            raise ValueError("week must be positive")
        return deepcopy(_MOCK_TIMETABLE)

    async def get_exams(self, session: str) -> list[dict[str, Any]]:
        self._ensure_mock(session)
        return deepcopy(_MOCK_EXAMS)

    async def sync_user_data(self, user: Any, token: str) -> dict[str, Any]:
        return {
            "profile": await self.get_profile(token),
            "timetable": await self.get_timetable(token),
            "exams": await self.get_exams(token),
        }

    def _ensure_mock(self, token_or_session: str) -> None:
        if not token_or_session.strip():
            raise ValueError("MTUCI session is empty")
        if not self.mock:
            raise NotImplementedError("Live MTUCI/TECH API client is not configured")
