"""Точка входа FastAPI-приложения «Кампус».

Скелет: подключает роутеры API v1. Реализация эндпоинтов — в соответствующих issue.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import auth, documents, search, queues, integrations, schedule

app = FastAPI(
    title="Кампус API",
    description="База знаний университета и система учебных очередей.",
    version="0.1.0",
)

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
