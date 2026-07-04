"""Тесты MTUCI-интеграции [BE-M1..M4]."""
from __future__ import annotations

import uuid

import pytest

from app.models.integration import ExternalIntegration, IntegrationProvider, IntegrationStatus
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
