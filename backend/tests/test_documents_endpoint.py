"""Тесты эндпоинта загрузки документов [BE-D1] — валидация без реальной БД."""
from __future__ import annotations

import io
from unittest.mock import AsyncMock, MagicMock

import pytest
from docx import Document as DocxDocument
from fastapi.testclient import TestClient

from app.db.session import get_session
from app.main import app


def _make_docx_bytes(text: str = "Тестовый документ.") -> bytes:
    doc = DocxDocument()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.fixture()
def client_mock_db():
    """TestClient с замоканной AsyncSession."""
    session = AsyncMock()
    # flush и commit — no-op; get вернёт None (документ/пользователь-uploader не найден).
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.get = AsyncMock(return_value=None)
    # add ничего не делает
    session.add = MagicMock()

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.pop(get_session, None)


def _admin_token(client: TestClient) -> str:
    resp = client.post("/api/v1/auth/demo", json={"role": "admin"})
    return resp.json()["access_token"]


# ---------- BE-D1: валидация типа и размера ----------

def test_upload_wrong_type_returns_400(client_mock_db: TestClient) -> None:
    token = _admin_token(client_mock_db)
    resp = client_mock_db.post(
        "/api/v1/documents/upload",
        files={"file": ("report.txt", b"some text", "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert "PDF" in resp.json()["detail"] or "DOCX" in resp.json()["detail"]


def test_upload_empty_file_returns_400(client_mock_db: TestClient) -> None:
    token = _admin_token(client_mock_db)
    resp = client_mock_db.post(
        "/api/v1/documents/upload",
        files={"file": ("doc.pdf", b"", "application/pdf")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


def test_upload_requires_auth() -> None:
    with TestClient(app) as c:
        resp = c.post(
            "/api/v1/documents/upload",
            files={"file": ("doc.pdf", b"%PDF-1.4", "application/pdf")},
        )
    assert resp.status_code == 401


def test_upload_allowed_for_any_authenticated_role(client_mock_db: TestClient) -> None:
    """Загрузка доступна всем авторизованным ролям (не только admin)."""
    login = client_mock_db.post("/api/v1/auth/demo", json={"role": "student"})
    token = login.json()["access_token"]
    docx_bytes = _make_docx_bytes("Студенческий документ.")
    resp = client_mock_db.post(
        "/api/v1/documents/upload",
        files={"file": ("student.docx", docx_bytes,
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201


def test_upload_valid_docx_accepted(client_mock_db: TestClient) -> None:
    """BE-D1: валидный DOCX принимается (201). Парсинг + сохранение замоканы."""
    token = _admin_token(client_mock_db)
    docx_bytes = _make_docx_bytes("Привет! Это тестовый документ для загрузки.")
    resp = client_mock_db.post(
        "/api/v1/documents/upload",
        files={"file": ("test.docx", docx_bytes,
                         "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "test.docx"
    assert body["type"] == "DOCX"
    assert body["status"] in ("done", "error", "indexing")
