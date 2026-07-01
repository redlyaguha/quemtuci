"""Тесты авторизации [BE-A2, BE-A3]."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.parametrize("role", ["student", "teacher", "admin"])
def test_demo_login_returns_token(role: str) -> None:
    """BE-A2: каждая роль получает JWT."""
    resp = client.post("/api/v1/auth/demo", json={"role": role})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == role


def test_demo_login_invalid_role() -> None:
    """BE-A2: неверная роль — 422."""
    resp = client.post("/api/v1/auth/demo", json={"role": "superuser"})
    assert resp.status_code == 422


def test_me_without_token() -> None:
    """BE-A3: /me без токена — 401."""
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_with_token() -> None:
    """BE-A3: /me с корректным JWT возвращает профиль."""
    login = client.post("/api/v1/auth/demo", json={"role": "student"})
    token = login.json()["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    user = resp.json()
    assert user["role"] == "student"
    assert user["name"] == "Вадим Рыбаченок"
    assert user["group"] == "БПИ2403"


def test_require_roles_rejects_wrong_role() -> None:
    """BE-A3: require_roles отклоняет пользователя с недопустимой ролью (403).

    Проверяем механизм через /me с токеном другой роли и тестовый маршрут.
    RBAC на /queues активируется в BE-Q2 — полный сценарий там.
    """
    from fastapi import Depends
    from fastapi.testclient import TestClient as TC

    from app.core.security import require_roles
    from app.models.user import UserRole
    from app.schemas.auth import UserPublic

    # Встроенный мини-маршрут, защищённый require_roles(admin)
    from fastapi import FastAPI

    mini = FastAPI()

    @mini.get("/admin-only")
    def _admin_only(_: UserPublic = Depends(require_roles(UserRole.admin))) -> dict:
        return {"ok": True}

    tc = TC(mini)

    login = client.post("/api/v1/auth/demo", json={"role": "student"})
    token = login.json()["access_token"]

    resp = tc.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
