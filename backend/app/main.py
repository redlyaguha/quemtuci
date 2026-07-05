"""Точка входа FastAPI-приложения «Кампус»."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.api.v1 import auth, documents, search, queues, integrations, schedule
from app.services.elasticsearch_service import ensure_index
from app.services.seed import seed_practice_defense

_TAGS_METADATA = [
    {
        "name": "auth",
        "description": (
            "Авторизация и профиль. **Демо-режим** выдаёт JWT без пароля — "
            "укажите роль (`student` / `teacher` / `admin`) и получите токен. "
            "Все защищённые эндпоинты принимают `Authorization: Bearer <token>`."
        ),
    },
    {
        "name": "documents",
        "description": (
            "Учебные материалы (PDF / DOCX). Загрузка доступна только **admin**; "
            "просмотр и поиск — всем авторизованным пользователям. "
            "Файлы парсятся, разбиваются на чанки и индексируются в Elasticsearch."
        ),
    },
    {
        "name": "search",
        "description": (
            "Полнотекстовый поиск по базе знаний через Elasticsearch (русский анализатор). "
            "Результаты содержат подсветку совпадений (`<mark>…</mark>`). "
            "История запросов сохраняется автоматически и доступна через `/history`."
        ),
    },
    {
        "name": "queues",
        "description": (
            "Учебные очереди (лабораторные, консультации, защиты, пересдачи, практика). "
            "Преподаватель / admin создаёт очередь; студент записывается и выходит. "
            "Талон (`seq`) стабилен — не меняется при перестановках."
        ),
    },
    {
        "name": "health",
        "description": "Проверка живости сервиса для систем мониторинга.",
    },
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    await ensure_index()
    await seed_practice_defense()
    yield


app = FastAPI(
    title="Кампус API",
    description=(
        "## База знаний и система учебных очередей МТУСИ\n\n"
        "REST API для приложения «Кампус»: загрузка учебных материалов, "
        "полнотекстовый поиск, управление очередями на сдачу.\n\n"
        "### Аутентификация\n"
        "Все эндпоинты (кроме `/health` и `/auth/demo`) требуют JWT-токена. "
        "Получите его через `POST /api/v1/auth/demo`, затем передавайте в заголовке:\n"
        "```\nAuthorization: Bearer <token>\n```\n\n"
        "### Роли\n"
        "| Роль | Возможности |\n"
        "|------|-------------|\n"
        "| `student` | Поиск, просмотр документов, запись в очередь |\n"
        "| `teacher` | Всё выше + создание и управление своими очередями |\n"
        "| `admin` | Полный доступ, загрузка и удаление документов |"
    ),
    version="0.1.0",
    openapi_tags=_TAGS_METADATA,
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(documents.router, prefix=API_PREFIX)
app.include_router(search.router, prefix=API_PREFIX)
app.include_router(queues.router, prefix=API_PREFIX)
app.include_router(integrations.router, prefix=API_PREFIX)
app.include_router(schedule.router, prefix=API_PREFIX)


@app.get("/health", tags=["health"])
async def health() -> dict:
    """Проверка живости сервиса."""
    return {"status": "ok"}
