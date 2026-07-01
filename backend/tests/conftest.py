"""Глобальная конфигурация тестов.

Мокает ensure_index() чтобы lifespan не требовал запущенного Elasticsearch.
"""
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_es_lifespan():
    """Перехватывает ensure_index при старте приложения в каждом тесте."""
    with patch(
        "app.services.elasticsearch_service.ensure_index",
        new_callable=lambda: lambda: AsyncMock(),
    ):
        yield
