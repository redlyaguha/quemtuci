"""Дымовой тест: приложение поднимается, /health отвечает.

Базовый набор расширяется в issue [QA-01].
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
