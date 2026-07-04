"""Тесты MTUCI-интеграции [BE-M1..M4]."""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_session
from app.main import app
from app.models.integration import ExternalIntegration, IntegrationProvider, IntegrationStatus
from app.models.user import User
from app.services.mtuci_tech_service import MtuciTechService
from app.services.token_crypto import decrypt_token, encrypt_token


def test_encrypt_token_does_not_store_plain_value() -> None:
    token = "mtuci-secret-token"

    encrypted = encrypt_token(token)

    assert encrypted != token
    assert token not in encrypted
    assert decrypt_token(encrypted) == token


def test_external_integration_model_fields() -> None:
    user_id = uuid.uuid4()
    integration = ExternalIntegration(
        user_id=user_id,
        provider=IntegrationProvider.mtuci,
        encrypted_token=encrypt_token("token"),
        status=IntegrationStatus.connected,
    )

    assert integration.user_id == user_id
    assert integration.provider == IntegrationProvider.mtuci
    assert integration.status == IntegrationStatus.connected
    assert decrypt_token(integration.encrypted_token) == "token"


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def first(self):
        return self.value


class _ExecuteResult:
    def __init__(self, value):
        self.value = value

    def scalars(self):
        return _ScalarResult(self.value)


class _FakeSession:
    def __init__(self, user=None, integration=None):
        self.user = user
        self.integration = integration
        self.added = []
        self.deleted = []
        self.commits = 0

    async def execute(self, stmt):
        text = str(stmt)
        if "external_integrations" in text:
            return _ExecuteResult(self.integration)
        if "users" in text:
            return _ExecuteResult(self.user)
        return _ExecuteResult(None)

    def add(self, obj):
        if isinstance(obj, User) and obj.id is None:
            obj.id = uuid.UUID("11111111-1111-1111-1111-111111111111")
            self.user = obj
        if isinstance(obj, ExternalIntegration):
            self.integration = obj
        self.added.append(obj)

    async def flush(self):
        if self.user is not None and self.user.id is None:
            self.user.id = uuid.UUID("11111111-1111-1111-1111-111111111111")

    async def commit(self):
        self.commits += 1

    async def delete(self, obj):
        self.deleted.append(obj)
        if obj is self.integration:
            self.integration = None


@pytest.mark.asyncio
async def test_mtuci_service_mock_authenticates_offline() -> None:
    service = MtuciTechService(mock=True)

    profile = await service.authenticate_by_token("mock-token")

    assert profile["mtuci_user_id"] == "mock-student-001"
    assert profile["role"] == "student"
    assert profile["group_name"] == "БПИ2403"


@pytest.mark.asyncio
async def test_mtuci_service_mock_returns_timetable_and_exams() -> None:
    service = MtuciTechService(mock=True)

    timetable = await service.get_timetable("mock-token")
    exams = await service.get_exams("mock-token")

    assert timetable[0]["discipline"] == "Алгоритмы и структуры данных"
    assert exams[0]["discipline"] == "Базы данных"


@pytest.mark.asyncio
async def test_mtuci_service_live_mode_is_explicitly_disabled() -> None:
    service = MtuciTechService(mock=False)

    try:
        await service.get_profile("real-token")
    except NotImplementedError as exc:
        assert "Live MTUCI/TECH API client" in str(exc)
    else:
        raise AssertionError("live mode should not perform implicit network calls")


def test_mtuci_token_login_creates_user_and_hides_token() -> None:
    session = _FakeSession()

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as client:
            resp = client.post("/api/v1/auth/mtuci-token", json={"token": "mock-token"})
    finally:
        app.dependency_overrides.pop(get_session, None)

    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "mock-token" not in resp.text
    assert data["user"]["role"] == "student"
    assert session.integration is not None
    assert decrypt_token(session.integration.encrypted_token) == "mock-token"


def test_mtuci_integration_status_sync_and_disconnect() -> None:
    integration = ExternalIntegration(
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        provider=IntegrationProvider.mtuci,
        encrypted_token=encrypt_token("mock-token"),
        status=IntegrationStatus.connected,
    )
    session = _FakeSession(integration=integration)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as client:
            token = client.post("/api/v1/auth/demo", json={"role": "student"}).json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            status_resp = client.get("/api/v1/integrations/mtuci/status", headers=headers)
            sync_resp = client.post("/api/v1/integrations/mtuci/sync", headers=headers)
            disconnect_resp = client.delete("/api/v1/integrations/mtuci/disconnect", headers=headers)
    finally:
        app.dependency_overrides.pop(get_session, None)

    assert status_resp.status_code == 200
    assert status_resp.json()["connected"] is True
    assert sync_resp.status_code == 200
    assert sync_resp.json()["timetable_count"] == 2
    assert session.integration is None
    assert disconnect_resp.json()["connected"] is False
