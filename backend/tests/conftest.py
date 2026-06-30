"""Глобальная конфигурация тестов.

Мокает ensure_index() чтобы lifespan не требовал запущенного Elasticsearch.
"""
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

FIXTURE_FILES = (
    "valid.pdf",
    "valid.docx",
    "empty.pdf",
    "empty.docx",
    "corrupted.pdf",
    "corrupted.docx",
    "fancy.pdf",
    "fancy.docx",
)


@pytest.fixture(autouse=True)
def mock_es_lifespan():
    """Перехватывает ensure_index при старте приложения в каждом тесте."""
    with patch(
        "app.services.elasticsearch_service.ensure_index",
        new_callable=lambda: lambda: AsyncMock(),
    ):
        yield


@pytest.fixture(scope="session")
def fixtures_dir():
    """Путь к папке с тестовыми файлами."""
    path = Path(__file__).parent / "fixtures" / "files"
    missing = [name for name in FIXTURE_FILES if not (path / name).exists()]
    if missing:
        pytest.fail(f"Не найдены тестовые фикстуры: {', '.join(missing)}")
    return path


@pytest.fixture
def sample_files(fixtures_dir):
    """Словарь с путями ко всем тестовым файлам."""
    return {
        "valid_pdf": fixtures_dir / "valid.pdf",
        "valid_docx": fixtures_dir / "valid.docx",
        "empty_pdf": fixtures_dir / "empty.pdf",
        "empty_docx": fixtures_dir / "empty.docx",
        "corrupted_pdf": fixtures_dir / "corrupted.pdf",
        "corrupted_docx": fixtures_dir / "corrupted.docx",
        "fancy_pdf": fixtures_dir / "fancy.pdf",
        "fancy_docx": fixtures_dir / "fancy.docx",
    }
