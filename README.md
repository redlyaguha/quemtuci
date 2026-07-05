# Кампус

Интеллектуальная база знаний университета и система учебных очередей для студентов,
преподавателей и администратора.

Проект объединяет загрузку учебных PDF/DOCX, полнотекстовый поиск по материалам,
очереди на сдачу работ и безопасную интеграцию с MTUCI/TECH по пользовательскому токену.

## Содержание

1. [Описание](#описание)
2. [Стек технологий](#стек-технологий)
3. [Архитектура](#архитектура)
4. [Запуск через Docker Compose](#запуск-через-docker-compose)
5. [Запуск backend отдельно](#запуск-backend-отдельно)
6. [Запуск frontend отдельно](#запуск-frontend-отдельно)
7. [Как работает MTUCI/TECH-токен](#как-работает-mtucitech-токен)
8. [Почему не используем логин/пароль ЛК МТУСИ](#почему-не-используем-логинпароль-лк-мтуси)
9. [API](#api)
10. [Тестовые пользователи](#тестовые-пользователи)
11. [Скриншоты и страницы](#скриншоты-и-страницы)

## Описание

В приложении есть три роли:

| Роль | Возможности |
|---|---|
| Студент | Поиск по базе знаний, просмотр документов, просмотр очередей, запись и выход из очереди |
| Преподаватель | Возможности студента, создание очередей, управление участниками, закрытие очередей |
| Администратор | Полный доступ, загрузка и удаление документов, подготовка базы знаний |

Основной сценарий: администратор загружает учебные материалы, backend извлекает текст,
разбивает его на чанки, сохраняет метаданные в PostgreSQL и индексирует текст в
Elasticsearch. Пользователь ищет материалы через frontend, а повторяющиеся запросы
кешируются в Redis.

## Стек технологий

| Слой | Технологии |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy async, Alembic, Pydantic Settings |
| Frontend | React 18, TypeScript, Vite, React Router, Axios |
| База данных | PostgreSQL 16 |
| Поиск | Elasticsearch 8 с русским анализатором |
| Кеш | Redis 7 |
| Мониторинг | Prometheus, Grafana, `/metrics` FastAPI |
| Контейнеризация | Docker, Docker Compose |
| Тесты | pytest, Playwright |

## Архитектура

```text
browser / Telegram Mini App
        |
        v
frontend (React + Nginx)
        |
        v
backend (FastAPI)
   |        |          |
   v        v          v
PostgreSQL Redis  Elasticsearch
   |
   v
MTUCI/TECH integration data

Prometheus -> backend /metrics
Grafana    -> Prometheus datasource
```

Сервисы Docker Compose:

| Сервис | Порт | Назначение |
|---|---:|---|
| backend | 8000 | REST API, Swagger, метрики |
| frontend | 5173 | React-приложение через Nginx |
| postgres | 5432 | Основная БД |
| elasticsearch | 9200 | Индекс документов |
| redis | 6379 | Кеш поиска |
| prometheus | 9090 | Сбор метрик |
| grafana | 3000 | Dashboard мониторинга |

## Запуск через Docker Compose

1. Создайте локальный `.env`:

```bash
cp .env.example .env
```

2. Для локального запуска значения из `.env.example` уже настроены на Docker Compose.
Для production обязательно замените `JWT_SECRET_KEY`, `POSTGRES_PASSWORD`,
`GF_SECURITY_ADMIN_PASSWORD` и задайте `TOKEN_ENCRYPTION_KEY`.

Сгенерировать ключ Fernet:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

3. Поднимите стек:

```bash
docker compose up --build
```

4. Проверьте сервисы:

```bash
curl http://localhost:8000/health
curl http://localhost:9200
```

Адреса:

- Frontend: `http://localhost:5173`
- Swagger: `http://localhost:8000/docs`
- Backend health: `http://localhost:8000/health`
- Метрики: `http://localhost:8000/metrics`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

Grafana использует логин `admin`; пароль берётся из `GF_SECURITY_ADMIN_PASSWORD`
(`admin` в локальном `.env.example`). Datasource Prometheus и dashboard `Campus API`
провиженятся автоматически.

Для загрузки 10 тестовых PDF:

```bash
bash init.sh
```

Если backend работает не на `http://localhost:8000`, передайте URL API:

```bash
API=http://localhost:8000/api/v1 bash init.sh
```

## Запуск backend отдельно

Backend требует PostgreSQL, Elasticsearch и Redis. Их можно поднять через Compose,
а backend запустить локально:

```bash
docker compose up postgres elasticsearch redis
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Для Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Если backend запускается вне Docker, используйте URL с `localhost`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/campus
ELASTICSEARCH_URL=http://localhost:9200
REDIS_URL=redis://localhost:6379/0
```

Проверки backend:

```bash
python -m pytest backend/tests
```

## Запуск frontend отдельно

```bash
cd frontend
npm install
npm run dev
```

Vite запускается на `http://localhost:5173` и проксирует `/api` на
`http://localhost:8000`.

Проверки frontend:

```bash
npm run typecheck
npm run build
```

## Как работает MTUCI/TECH-токен

1. Пользователь вводит MTUCI/TECH-токен на странице входа.
2. Frontend отправляет токен только на backend.
3. Backend проверяет токен через MTUCI/TECH или мок-сервис при `MTUCI_MOCK=true`.
4. Backend создаёт или обновляет локального пользователя.
5. Токен MTUCI/TECH шифруется Fernet и хранится в PostgreSQL только в зашифрованном виде.
6. Frontend получает только локальный JWT приложения.

MTUCI/TECH-токен нужен для пользовательской интеграции с расписанием и профилем.
Он не является паролем от личного кабинета.

## Почему не используем логин/пароль ЛК МТУСИ

Приложение не запрашивает и не хранит логин или пароль от личного кабинета МТУСИ.
Это снижает риск компрометации учётных данных и не требует доверять приложению пароль
от внешней системы. Для интеграции используется отдельный пользовательский токен,
который хранится зашифрованным и не возвращается на frontend.

## API

Полная интерактивная документация доступна в Swagger:

```text
http://localhost:8000/docs
```

Основные группы endpoint:

| Группа | Endpoint | Назначение |
|---|---|---|
| Auth | `POST /api/v1/auth/demo` | Демо-вход по роли |
| Auth | `GET /api/v1/auth/me` | Профиль текущего пользователя |
| Documents | `POST /api/v1/documents/upload` | Загрузка PDF/DOCX, только admin |
| Documents | `GET /api/v1/documents` | Список документов |
| Search | `GET /api/v1/search?q=` | Полнотекстовый поиск |
| Search | `GET /api/v1/search/history` | История запросов |
| Queues | `GET /api/v1/queues` | Список очередей |
| Queues | `POST /api/v1/queues` | Создание очереди teacher/admin |
| Integrations | `/api/v1/integrations/mtuci/*` | Управление MTUCI/TECH-интеграцией |
| Schedule | `/api/v1/schedule/*` | Расписание и события |

Защищённые endpoint принимают заголовок:

```http
Authorization: Bearer <jwt>
```

Пример демо-входа:

```bash
curl -X POST http://localhost:8000/api/v1/auth/demo \
  -H "Content-Type: application/json" \
  -d "{\"role\":\"student\"}"
```

## Тестовые пользователи

Демо-пользователи создаются без пароля через `POST /api/v1/auth/demo`.

| Роль | JSON role | ФИО | Группа / кафедра |
|---|---|---|---|
| Студент | `student` | Вадим Рыбаченок | БПИ2403 |
| Преподаватель | `teacher` | Мосева Марина Сергеевна | Кафедра |
| Администратор | `admin` | Администратор | - |

## Скриншоты и страницы

В репозитории есть интерактивный HTML-прототип: `docs/prototype.html`.

Основные экраны приложения:

| Страница | Маршрут | Что проверять |
|---|---|---|
| Вход | `/login` | Демо-роли, форма MTUCI/TECH-токена |
| Дашборд | `/dashboard` | Разные состояния для student/teacher/admin |
| База знаний | `/knowledge` | Поиск, подсветка, пустые состояния |
| Загрузка документов | `/upload` | PDF/DOCX upload, статусы обработки |
| Очереди | `/queues` | Фильтры, карточки очередей, запись |
| Детали очереди | `/queues/:id` | Позиции, управление участниками |
| Профиль | `/profile` | Роль, группа/кафедра, MTUCI/TECH-интеграция |

Frontend адаптирован под ширину 320-1920px и может работать как Telegram Mini App:
при наличии Telegram WebApp SDK используются данные окружения Telegram, иначе включается
обычный browser fallback.

## Проверки перед сдачей

```bash
git diff --check
docker compose config
python -m pytest backend/tests
cd frontend && npm run typecheck && npm run build
```

Для полной проверки контейнеров:

```bash
docker compose build backend frontend
docker compose up
```
