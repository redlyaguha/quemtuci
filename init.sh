set -euo pipefail

API_URL="http://localhost:8000/api/v1"
DOCS_DIR="test_docs"

echo "Ожидание запуска бэкенда..."
while ! curl -s "http://localhost:8000/health" > /dev/null; do
  sleep 2
done
echo "Бэкенд запущен."

echo "Получение JWT-токена администратора..."
TOKEN=$(curl -s -X POST "$API_URL/auth/demo" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}' | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')

if [ -z "$TOKEN" ]; then
  echo "Ошибка: не удалось получить токен."
  exit 1
fi
echo "Токен получен."

echo "Подготовка учебных материалов..."
mkdir -p "$DOCS_DIR"

# Скачивание тестового PDF-файла
curl -s -L -o "$DOCS_DIR/lecture_1.pdf" "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
curl -s -L -o "$DOCS_DIR/lecture_2.pdf" "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

echo "Загрузка документов в базу знаний..."
for file in "$DOCS_DIR"/*.pdf; do
  echo "Отправка: $file"
  curl -s -X POST "$API_URL/documents/upload" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$file" > /dev/null
done

echo "Инициализация завершена. Система готова к демонстрации."