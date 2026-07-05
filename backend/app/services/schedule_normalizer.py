"""Нормализация расписания и сессии MTUCI/TECH [BE-M4]."""
from __future__ import annotations

from datetime import date, time
from typing import Any


_PLACEHOLDER_DISCIPLINES = {"", "--", "—", "-", "нет", "none", "null"}


def normalize_lessons(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in items:
        discipline = _clean_text(item.get("discipline"))
        if _is_placeholder_discipline(discipline):
            continue

        normalized.append(
            {
                "external_id": item.get("external_id"),
                "date": _parse_date(item.get("date")),
                "day": _clean_text(item.get("day")),
                "parity": _clean_text(item.get("parity")),
                "number": item.get("number"),
                "time_start": _parse_time(item.get("time_start")),
                "time_end": _parse_time(item.get("time_end")),
                "discipline": discipline,
                "lesson_type": _clean_text(item.get("lesson_type")),
                "room": _clean_text(item.get("room")),
                "teachers": _teachers(item.get("teachers")),
                "comment": _clean_text(item.get("comment")),
                "is_online": bool(item.get("is_online", False)),
                "is_exam": bool(item.get("is_exam", False)),
                "raw_json": item,
            }
        )
    return normalized


def normalize_exams(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in items:
        discipline = _clean_text(item.get("discipline"))
        if _is_placeholder_discipline(discipline):
            continue

        normalized.append(
            {
                "external_id": item.get("external_id"),
                "date": _parse_date(item.get("date")),
                "time_start": _parse_time(item.get("time_start")),
                "time_end": _parse_time(item.get("time_end")),
                "discipline": discipline,
                "event_type": _clean_text(item.get("event_type")),
                "room": _clean_text(item.get("room")),
                "teachers": _teachers(item.get("teachers")),
                "comment": _clean_text(item.get("comment")),
                "link": item.get("link"),
                "raw_json": item,
            }
        )
    return normalized


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _is_placeholder_discipline(value: str) -> bool:
    return value.lower() in _PLACEHOLDER_DISCIPLINES


def _parse_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _parse_time(value: Any) -> time | None:
    if value in (None, ""):
        return None
    if isinstance(value, time):
        return value
    text = str(value)
    if len(text) == 5:
        text = f"{text}:00"
    return time.fromisoformat(text)


def _teachers(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [_clean_text(value)] if _clean_text(value) else []
    return [_clean_text(item) for item in value if _clean_text(item)]
