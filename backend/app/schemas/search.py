"""Pydantic-схемы для search-эндпоинтов.

SearchHit совпадает с TypeScript-типом SearchResult на фронтенде.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SearchHit(BaseModel):
    chunk_id: str
    doc: str        # file_name
    type: str       # "PDF" | "DOCX"
    page: int
    rel: float      # нормализованная релевантность 0..1
    score: float    # сырой ES-score
    text: str       # фрагмент с тегами <mark>...</mark>


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchHit]


class SearchHistoryItem(BaseModel):
    id: int
    query: str
    created_at: datetime

    model_config = {"from_attributes": True}
