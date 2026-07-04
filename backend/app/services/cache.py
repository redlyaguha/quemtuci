"""Redis-кэш для результатов поиска [BE-S5].

Все операции fault-tolerant: при недоступности Redis приложение работает без кэша.
TTL по умолчанию 5 минут (300 сек).
"""
from __future__ import annotations

import json
import logging
from typing import Any

from redis.asyncio import Redis

from app.core.config import settings

log = logging.getLogger(__name__)

_client: Redis | None = None


def _get_client() -> Redis:
    global _client
    if _client is None:
        _client = Redis.from_url(settings.redis_url, decode_responses=True)
    return _client


async def cache_get(key: str) -> Any | None:
    """Вернуть десериализованное значение из кэша или None."""
    try:
        raw = await _get_client().get(key)
        return json.loads(raw) if raw is not None else None
    except Exception:
        log.debug("Redis cache_get miss/error: %s", key)
        return None


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    """Сохранить JSON-сериализуемое значение в кэш с TTL."""
    try:
        await _get_client().set(key, json.dumps(value), ex=ttl)
    except Exception:
        log.debug("Redis cache_set error: %s", key)
