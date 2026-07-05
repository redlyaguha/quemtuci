#!/usr/bin/env bash
set -euo pipefail

API="${API:-http://localhost:8000/api/v1}"
API="${API%/}"
HEALTH_URL="${HEALTH_URL:-${API%/api/v1}/health}"
DOCS_DIR="${DOCS_DIR:-test_docs}"

PDF_URLS=(
  "https://www.rfc-editor.org/rfc/rfc2616.pdf"
  "https://www.rfc-editor.org/rfc/rfc3986.pdf"
  "https://www.rfc-editor.org/rfc/rfc5246.pdf"
  "https://www.rfc-editor.org/rfc/rfc6749.pdf"
  "https://www.rfc-editor.org/rfc/rfc7519.pdf"
  "https://www.rfc-editor.org/rfc/rfc7540.pdf"
  "https://www.rfc-editor.org/rfc/rfc8259.pdf"
  "https://www.rfc-editor.org/rfc/rfc8446.pdf"
  "https://www.rfc-editor.org/rfc/rfc9110.pdf"
  "https://www.rfc-editor.org/rfc/rfc9112.pdf"
)

echo "Ожидание запуска бэкенда..."
for _ in {1..60}; do
  if curl -fsS "$HEALTH_URL" > /dev/null; then
    echo "Бэкенд запущен."
    break
  fi
  sleep 2
done

if ! curl -fsS "$HEALTH_URL" > /dev/null; then
  echo "Ошибка: бэкенд не ответил на $HEALTH_URL."
  exit 1
fi

echo "Получение JWT-токена администратора..."
TOKEN=$(curl -fsS -X POST "$API/auth/demo" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}' | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')

if [ -z "$TOKEN" ]; then
  echo "Ошибка: не удалось получить токен."
  exit 1
fi
echo "Токен получен."

echo "Подготовка учебных материалов..."
mkdir -p "$DOCS_DIR"

echo "Скачивание тестовых PDF..."
index=1
for url in "${PDF_URLS[@]}"; do
  file="$DOCS_DIR/lecture_${index}.pdf"
  echo "Скачивание: $file"
  curl -fL --retry 3 --retry-delay 2 -o "$file" "$url"
  index=$((index + 1))
done

echo "Загрузка документов в базу знаний..."
for file in "$DOCS_DIR"/*.pdf; do
  echo "Отправка: $file"
  curl -fsS -X POST "$API/documents/upload" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$file" > /dev/null
done

echo "Инициализация завершена. Система готова к демонстрации."
