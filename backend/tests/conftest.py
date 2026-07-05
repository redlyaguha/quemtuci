"""Глобальная конфигурация тестов.

Мокает lifespan-зависимости и внешние сервисы (ES, Redis, PostgreSQL)
чтобы тесты не требовали запущенной инфраструктуры.
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
def mock_lifespan_deps():
    """Перехватывает ensure_index, seed и Redis в каждом тесте."""
    with (
        patch("app.main.ensure_index", new_callable=AsyncMock),
        patch("app.main.seed_practice_defense", new_callable=AsyncMock),
        patch("app.services.cache.cache_get", new_callable=AsyncMock, return_value=None),
        patch("app.services.cache.cache_set", new_callable=AsyncMock),
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
