"""Поиск по базе знаний и история запросов.

BE-S3: GET /search?q= — полнотекстовый поиск через Elasticsearch.
BE-S4: GET /search/history, DELETE /search/history — история запросов.
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

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    size: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> SearchResponse:
    """Полнотекстовый поиск (multi_match по text) с подсветкой. [BE-S3]"""
    if not q.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пустой запрос")

    # Сохраняем запрос в историю (BE-S4)
    session.add(SearchHistory(user_id=current_user.id, query=q.strip()))
    await session.commit()

    raw = await es_svc.search_chunks(q.strip(), size=size)

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

    return SearchResponse(query=q.strip(), total=total, results=results)


@router.get("/history", response_model=list[SearchHistoryItem])
async def search_history(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> list[SearchHistoryItem]:
    """История поисковых запросов текущего пользователя. [BE-S4]"""
    result = await session.execute(
        select(SearchHistory)
        .where(SearchHistory.user_id == current_user.id)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
    )
    return [SearchHistoryItem.model_validate(row) for row in result.scalars()]


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_search_history(
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> None:
    """Очистка истории поисковых запросов. [BE-S4]"""
    await session.execute(
        delete(SearchHistory).where(SearchHistory.user_id == current_user.id)
    )
    await session.commit()
