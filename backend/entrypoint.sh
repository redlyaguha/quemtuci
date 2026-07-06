#!/bin/sh
# Точка входа backend-контейнера: применяет миграции БД, затем запускает сервис.
set -e

echo "Применение миграций базы данных..."
attempt=1
max_attempts=10
until alembic upgrade head; do
  if [ "$attempt" -ge "$max_attempts" ]; then
    echo "Не удалось применить миграции после $attempt попыток." >&2
    exit 1
  fi
  echo "База ещё не готова (попытка $attempt из $max_attempts), повтор через 3 с..."
  attempt=$((attempt + 1))
  sleep 3
done

echo "Миграции применены. Запуск приложения..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
