"""Поиск по базе знаний и история запросов.

BE-S3: GET /search?q= — полнотекстовый поиск через Elasticsearch.
BE-S4: GET /search/history, DELETE /search/history — история запросов.
BE-S5: Redis-кэш результатов ES (TTL 5 мин).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_session
from app.models.search_history import SearchHistory
from app.schemas.auth import UserPublic
from app.schemas.search import SearchHistoryItem, SearchHit, SearchResponse
from app.services import elasticsearch_service as es_svc
from app.services.cache import cache_get, cache_set

router = APIRouter(prefix="/search", tags=["search"])

_CACHE_TTL = 300  # 5 минут

_401 = {"description": "Токен отсутствует или недействителен"}


@router.get(
    "",
    response_model=SearchResponse,
    summary="Поиск по базе знаний",
    response_description="Список релевантных фрагментов с подсветкой совпадений",
    responses={
        400: {"description": "Пустой поисковый запрос"},
        401: _401,
    },
)
async def search(
    q: str = Query(..., min_length=1, description="Поисковый запрос (минимум 1 символ)"),
    size: int = Query(10, ge=1, le=50, description="Максимальное число результатов (1–50)"),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> SearchResponse:
    """Полнотекстовый поиск по загруженным учебным материалам.

    Использует Elasticsearch с русским морфологическим анализатором.
    Результаты содержат фрагменты текста с подсветкой совпадений (`<mark>…</mark>`).

    - Поле `rel` (0.0 – 1.0) — нормализованная релевантность относительно лучшего результата
    - Запросы кэшируются в Redis на 5 минут; история пишется при каждом запросе
    """
    if not q.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пустой запрос")

    query = q.strip()

    # BE-S4: сохраняем в историю (всегда, даже при попадании в кэш)
    session.add(SearchHistory(user_id=current_user.id, query=query))
    await session.commit()

    # BE-S5: проверяем кэш
    cache_key = f"search:{query}:{size}"
    cached = await cache_get(cache_key)
    if cached is not None:
        raw = cached
    else:
        raw = await es_svc.search_chunks(query, size=size)
        await cache_set(cache_key, raw, ttl=_CACHE_TTL)

    hits_raw = raw.get("hits", {})
    total = hits_raw.get("total", {}).get("value", 0)
    hits = hits_raw.get("hits", [])
    max_score: float = raw.get("hits", {}).get("max_score") or 1.0

    results: list[SearchHit] = []
    for h in hits:
        src = h["_source"]
        score: float = h.get("_score") or 0.0
        highlight_fragments = h.get("highlight", {}).get("text", [])
        text = highlight_fragments[0] if highlight_fragments else src.get("text", "")
        results.append(
            SearchHit(
                chunk_id=src["chunk_id"],
                doc=src["file_name"],
                type=src["file_type"],
                page=src["page_number"],
                score=score,
                rel=round(score / max_score, 4) if max_score else 0.0,
                text=text,
            )
        )

    return SearchResponse(query=query, total=total, results=results)


@router.get(
    "/history",
    response_model=list[SearchHistoryItem],
    summary="История поисковых запросов",
    response_description="Запросы пользователя, новые первыми",
    responses={401: _401},
)
async def search_history(
    limit: int = Query(20, ge=1, le=100, description="Максимальное число записей (1–100)"),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> list[SearchHistoryItem]:
    """История поисковых запросов текущего пользователя.

    Каждый вызов `GET /search` добавляет запись; дубликаты не фильтруются.
    """
    result = await session.execute(
        select(SearchHistory)
        .where(SearchHistory.user_id == current_user.id)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
    )
    return [SearchHistoryItem.model_validate(row) for row in result.scalars()]


@router.delete(
    "/history",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Очистить историю поиска",
    response_description="История удалена (нет тела ответа)",
    responses={401: _401},
)
async def clear_search_history(
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> None:
    """Удаляет всю историю поисковых запросов текущего пользователя."""
    await session.execute(
        delete(SearchHistory).where(SearchHistory.user_id == current_user.id)
    )
    await session.commit()
