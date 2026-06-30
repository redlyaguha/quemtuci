"""Тесты поиска и истории запросов [BE-S1, BE-S2, BE-S3, BE-S4]."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_session
from app.main import app


# ---------- фикстуры ----------

def _token(role: str = "student") -> str:
    with TestClient(app) as c:
        return c.post("/api/v1/auth/demo", json={"role": role}).json()["access_token"]


def _mock_session_with_history():
    """AsyncMock-сессия, отдающая пустую историю по умолчанию."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()

    # scalars().all() → []
    scalars_mock = MagicMock()
    scalars_mock.__iter__ = MagicMock(return_value=iter([]))
    execute_result = MagicMock()
    execute_result.scalars = MagicMock(return_value=scalars_mock)
    session.execute = AsyncMock(return_value=execute_result)
    return session


ES_RESPONSE_OK = {
    "hits": {
        "total": {"value": 1},
        "max_score": 2.5,
        "hits": [{
            "_score": 2.5,
            "_source": {
                "chunk_id": "abc_0",
                "document_id": "abc",
                "file_name": "лекция.pdf",
                "file_type": "PDF",
                "page_number": 1,
                "text": "Алгоритм сортировки пузырьком",
            },
            "highlight": {"text": ["Алгоритм <mark>сортировки</mark> пузырьком"]},
        }],
    }
}

ES_RESPONSE_EMPTY = {
    "hits": {"total": {"value": 0}, "max_score": None, "hits": []}
}


# ---------- BE-S3: поиск ----------

def test_search_returns_results() -> None:
    session = _mock_session_with_history()

    async def _session_override():
        yield session

    app.dependency_overrides[get_session] = _session_override
    try:
        with (
            patch("app.services.elasticsearch_service.AsyncElasticsearch") as MockES,
        ):
            instance = AsyncMock()
            instance.search = AsyncMock(return_value=ES_RESPONSE_OK)
            instance.close = AsyncMock()
            MockES.return_value = instance

            with TestClient(app) as c:
                token = c.post("/api/v1/auth/demo", json={"role": "student"}).json()["access_token"]
                resp = c.get("/api/v1/search?q=сортировка",
                             headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["query"] == "сортировка"
        assert data["results"][0]["doc"] == "лекция.pdf"
        assert data["results"][0]["type"] == "PDF"
        assert data["results"][0]["rel"] == 1.0
        assert "<mark>" in data["results"][0]["text"]
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_search_empty_query_returns_422() -> None:
    with TestClient(app) as c:
        token = c.post("/api/v1/auth/demo", json={"role": "student"}).json()["access_token"]
        resp = c.get("/api/v1/search?q=",
                     headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422


def test_search_no_token_returns_401() -> None:
    with TestClient(app) as c:
        resp = c.get("/api/v1/search?q=тест")
    assert resp.status_code == 401


def test_search_empty_results() -> None:
    session = _mock_session_with_history()

    async def _session_override():
        yield session

    app.dependency_overrides[get_session] = _session_override
    try:
        with patch("app.services.elasticsearch_service.AsyncElasticsearch") as MockES:
            instance = AsyncMock()
            instance.search = AsyncMock(return_value=ES_RESPONSE_EMPTY)
            instance.close = AsyncMock()
            MockES.return_value = instance

            with TestClient(app) as c:
                token = c.post("/api/v1/auth/demo", json={"role": "student"}).json()["access_token"]
                resp = c.get("/api/v1/search?q=несуществующийзапрос",
                             headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 200
        assert resp.json()["total"] == 0
        assert resp.json()["results"] == []
    finally:
        app.dependency_overrides.pop(get_session, None)


# ---------- BE-S4: история ----------

def test_search_history_requires_auth() -> None:
    with TestClient(app) as c:
        resp = c.get("/api/v1/search/history")
    assert resp.status_code == 401


def test_clear_history_requires_auth() -> None:
    with TestClient(app) as c:
        resp = c.delete("/api/v1/search/history")
    assert resp.status_code == 401


def test_search_saves_to_history() -> None:
    """BE-S4: каждый поисковый запрос добавляется в историю (session.add вызван)."""
    session = _mock_session_with_history()
    saved: list = []
    original_add = session.add

    def _capture_add(obj):
        saved.append(obj)
        return original_add(obj)

    session.add = _capture_add

    async def _session_override():
        yield session

    app.dependency_overrides[get_session] = _session_override
    try:
        with patch("app.services.elasticsearch_service.AsyncElasticsearch") as MockES:
            instance = AsyncMock()
            instance.search = AsyncMock(return_value=ES_RESPONSE_EMPTY)
            instance.close = AsyncMock()
            MockES.return_value = instance

            with TestClient(app) as c:
                token = c.post("/api/v1/auth/demo", json={"role": "student"}).json()["access_token"]
                c.get("/api/v1/search?q=тест", headers={"Authorization": f"Bearer {token}"})

        from app.models.search_history import SearchHistory
        assert any(isinstance(obj, SearchHistory) for obj in saved)
    finally:
        app.dependency_overrides.pop(get_session, None)
