"""Тесты MTUCI-интеграции [BE-M1..M4]."""
from __future__ import annotations

import uuid

from app.models.integration import ExternalIntegration, IntegrationProvider, IntegrationStatus
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
