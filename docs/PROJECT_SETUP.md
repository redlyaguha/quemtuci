# Кампус — настройка проекта, роли и бэклог

Внутренний документ для команды. Репозиторий: `redlyaguha/quemtuci`.

## Команда и роли

| Участник | GitHub | Роль | Зона ответственности |
|---|---|---|---|
| Тимлид / Frontend | `@redlyaguha` | FE + Lead | Перенос UI-прототипа в React+TS+Vite, страницы, API-клиент, подсветка, адаптив, Telegram Mini App; контракт API и типы; интеграция; ревью PR в `dev` |
| Backend | `@LikhachevAlexey` | BE | FastAPI, модели, auth+JWT+RBAC, документы, парсинг, Elasticsearch, поиск, очереди, MTUCI-сервис, Redis |
| QA | `@Nikii-fnchek` | QA | pytest (≥50%), E2E Playwright, тестовые фикстуры, нагрузочные тесты, Precision@3, User Guide |
| DevOps | `@svyat0s1av` | DO | Dockerfile (back/front), docker-compose, .env.example, GitHub Actions, init.sh, Prometheus/Grafana, README |

## Ветвление и защита

- `prod` — дефолтная, релизная. В неё мёрджит только тимлид (или заморожена через Lock branch).
- `dev` — интеграционная. Прямой push запрещён; всё через PR с обязательным ревью code owner (`@redlyaguha`).
- Фиче-ветки: `feat/<area>-<short>`, например `feat/be-upload`, `feat/fe-search-page`.
- `.github/CODEOWNERS`: строка `*  @redlyaguha` — делает ревью тимлида обязательным на защищённых ветках.
- Коммиты по Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `chore:`.

## Приоритеты (тиеровка)

- **P0** — требования вуза (PDF): загрузка, парсинг, ES-поиск, подсветка, история, Docker, тесты, README. База оценки.
- **P1** — очереди + событие защиты практики 06.07.2026. Дифференциатор, UI уже готов в референсе.
- **P2 / стретч** — живая интеграция с tech.mtuci.ru. Архитектуру делаем, реальный скрейпинг — за фича-флагом + мок-фикстура, чтобы демо не зависело от портала.

---

## Бэклог issue

Формат: **[ID] Заголовок** — исполнитель · приоритет · лейблы · (требования) · зависимости.

### E0. Инициализация проекта

- **[S-01] Структура репозитория и ветки** — `@redlyaguha` · P0 · `setup`
  Создать `backend/`, `frontend/`, `docker-compose.yml`, `.env.example`, `.github/`, `README.md`, `init.sh` (заглушки). Ветки `prod`/`dev`, default = `prod`, CODEOWNERS, защита веток.
  *Приёмка:* структура соответствует шаблону из задания; защита `dev`/`prod` включена.
- **[S-02] Скелет docker-compose** — `@svyat0s1av` · P0 · `area:devops` · (DO-03)
  Сервисы: `app`, `front`, `postgres`, `elasticsearch`, `redis`. Healthchecks, общая сеть, volume для ES/PG.
  *Приёмка:* `docker compose up` поднимает все 5 сервисов, ES отвечает на `:9200`.
- **[S-03] .env.example + конфиг** — `@svyat0s1av` · P0 · `area:devops` · (DO-04)
  Все ключи из задания. Backend читает `core/config.py` (pydantic-settings). В prod-режиме падать без `TOKEN_ENCRYPTION_KEY`.
  *Приёмка:* `.env.example` в репо; приложение стартует с заполненным `.env`.
- **[S-04] CI: линт + тесты** — `@svyat0s1av` · P1 · `area:devops` · (DO-05)
  GitHub Actions: на push/PR в `dev` — ruff/flake8 + pytest (backend), eslint + tsc (frontend).
  *Приёмка:* проверки появляются в PR и обязательны для мёрджа в `dev`.

### E1. Авторизация и пользователи (критический путь)

- **[BE-A1] Модель User + миграции** — `@LikhachevAlexey` · P0 · `area:backend`
  Поля по ТЗ §12 (full_name, role, group_name, mtuci_* и т.д.). SQLAlchemy (async) + Alembic.
- **[BE-A2] Демо-вход** — `@LikhachevAlexey` · P0 · `area:backend`
  `POST /api/v1/auth/demo` для ролей student/teacher/admin (seed-пользователи). Выдаёт JWT.
- **[BE-A3] JWT + зависимость текущего пользователя** — `@LikhachevAlexey` · P0 · `area:backend` · (§15)
  `core/security.py`, `GET /api/v1/auth/me`, dependency `get_current_user`, проверка ролей (RBAC).
  *Приёмка:* защищённые роуты требуют JWT; студент не может создать очередь (403).

### E2. Документы

- **[BE-D1] Загрузка и валидация** — `@LikhachevAlexey` · P0 · `area:backend` · (BE-01, BE-02, BE-03)
  `POST /api/v1/documents/upload`. PDF/DOCX, ≤20 МБ, иначе 400 с описанием. UUID на документ.
- **[BE-D2] Извлечение текста** — `@LikhachevAlexey` · P0 · `area:backend` · (BE-04)
  pdfplumber (PDF), python-docx (DOCX). Обработка ошибок парсинга → статус `error` + `error_message`.
- **[BE-D3] Чанкинг** — `@LikhachevAlexey` · P0 · `area:backend` · (BE-05)
  Чанки 1000 символов, перекрытие 100. Сохранять document_id, file_name, page_number, chunk_id, text.
- **[BE-D4] CRUD документов** — `@LikhachevAlexey` · P1 · `area:backend`
  `GET /documents`, `GET /documents/{id}`, `DELETE /documents/{id}` (admin).

### E3. Индексация и поиск

- **[BE-S1] Индекс ES с русским анализатором** — `@LikhachevAlexey` · P0 · `area:backend` · (BE-06)
  Индекс `documents`, встроенный `russian` analyzer, маппинг под полнотекст.
- **[BE-S2] Пайплайн индексации** — `@LikhachevAlexey` · P0 · `area:backend` · (BE-07)
  Каждый чанк → документ ES с метаданными и `uploaded_at`.
- **[BE-S3] Эндпоинт поиска** — `@LikhachevAlexey` · P0 · `area:backend` · (BE-08, BE-09)
  `GET /api/v1/search?q=` — multi_match по `text`. Ответ: chunk_id, file_name, page, text, score, highlights.
- **[BE-S4] История запросов** — `@LikhachevAlexey` · P1 · `area:backend`
  Сохранять запросы; `GET`/`DELETE /api/v1/search/history`.
- **[BE-S5] Redis-кеш** — `@LikhachevAlexey` · P2 · `area:backend` · (BE-10)
  TTL 5 мин, ключ учитывает query + user_id/role.

### E4. Очереди (P1)

- **[BE-Q1] Модели Queue/QueueMember** — `@LikhachevAlexey` · P1 · `area:backend` · (ТЗ §3, §12)
- **[BE-Q2] CRUD очередей** — `@LikhachevAlexey` · P1 · `area:backend`
  `GET /queues` (фильтры group/teacher/status/date), `POST /queues` (teacher/admin), `GET /queues/{id}`.
- **[BE-Q3] join / leave** — `@LikhachevAlexey` · P1 · `area:backend`
  Повторная запись → 400; закрытая очередь → 400; позиция в конец; при leave — пересчёт позиций.
- **[BE-Q4] reorder / remove / close** — `@LikhachevAlexey` · P1 · `area:backend`
  PATCH reorder, DELETE member, PATCH close — только владелец-преподаватель/админ.

### E5. MTUCI/TECH интеграция (P2, за фича-флагом + мок)

- **[BE-M1] Шифрование токена (Fernet) + модель ExternalIntegration** — `@LikhachevAlexey` · P2 · `area:backend` · (ТЗ §5, §6)
- **[BE-M2] MtuciTechService с мок-режимом** — `@LikhachevAlexey` · P2 · `area:backend`
  Методы authenticate_by_token / get_profile / get_timetable / get_exams / sync_user_data. При `MTUCI_MOCK=true` — фикстуры, без обращения к порталу.
- **[BE-M3] Эндпоинты входа и интеграции** — `@LikhachevAlexey` · P2 · `area:backend`
  `POST /auth/mtuci-token`, `GET/POST/DELETE /integrations/mtuci/*`. Токен на фронт не возвращать, не логировать.
- **[BE-M4] Нормализация расписания/сессии** — `@LikhachevAlexey` · P2 · `area:backend`
  Lesson/ExamEvent + фильтрация заглушек (`--`, пустая дисциплина). Пустой результат — не ошибка.

### E6. Защита практики 06.07.2026 (P1)

- **[BE-P1] Seed события защиты практики** — `@LikhachevAlexey` · P1 · `area:backend` · (ТЗ §8)
  PracticeDefenseEvent: 2026-07-06, 13:00–14:30, «Учебная практика (технологическая)», диф. зачёт, А-310, БПИ2403, Мосева М. С.
- **[FE-P2] Кнопка «Создать очередь на защиту практики»** — `@redlyaguha` · P1 · `area:frontend`
  Для преподавателя; создаёт очередь типа `practice_defense` с предзаполненными полями.

### E7. Frontend

- **[FE-01] Каркас Vite + Router + API-клиент** — `@redlyaguha` · P0 · `area:frontend`
  Структура `src/{api,components,pages,hooks,types,data}`. Axios/fetch-клиент с JWT-интерсептором.
- **[FE-02] LoginPage** — `@redlyaguha` · P0 · `area:frontend`
  Демо-кнопки + форма MTUCI/TECH-токена с предупреждением «токен уходит только на backend».
- **[FE-03] UploadDocumentsPage** — `@redlyaguha` · P0 · `area:frontend` · (FE-01, FE-02, FE-03)
  Drag-and-Drop, прогресс-бары (Загрузка/Индексация/Готово/Ошибка), таблица документов.
- **[FE-04] KnowledgeBasePage** — `@redlyaguha` · P0 · `area:frontend` · (FE-04…FE-08)
  Поиск по кнопке и Enter, карточки результатов, подсветка жёлтым, пагинация по 10, пустое состояние.
- **[FE-05] DashboardPage (3 роли)** — `@redlyaguha` · P1 · `area:frontend`
  Перенести три дашборда из референса, подключить к API.
- **[FE-06] QueuesPage + QueueDetailPage** — `@redlyaguha` · P1 · `area:frontend`
  Список с фильтрами, карточка очереди, позиция студента, управление для преподавателя.
- **[FE-07] ProfilePage + статус интеграции** — `@redlyaguha` · P2 · `area:frontend`
  ФИО/роль/группа, статус MTUCI, кнопки «Синхронизировать» / «Отключить».
- **[FE-08] Адаптив + Telegram Mini App** — `@redlyaguha` · P1 · `area:frontend` · (FE-09)
  320–1920px, нижняя навигация (Главная/Поиск/Очереди/Профиль).

### E8. DevOps

- **[DO-01] Dockerfile backend** — `@svyat0s1av` · P0 · `area:devops` · (DO-01)
- **[DO-02] Dockerfile frontend + Nginx** — `@svyat0s1av` · P0 · `area:devops` · (DO-02)
- **[DO-03] init.sh (10 тестовых PDF)** — `@svyat0s1av` · P1 · `area:devops` · (DO-07)
  Скачивает 10 PDF и грузит через API.
- **[DO-04] Prometheus + Grafana** — `@svyat0s1av` · P2 · `area:devops` · (DO-06)
  Метрики на /search, среднее время ответа; базовый дашборд.

### E9. QA

- **[QA-01] Юнит-тесты backend (≥50%)** — `@Nikii-fnchek` · P0 · `area:qa` · (QA-01)
  Парсинг, валидация, чанкинг. Отчёт о покрытии в CI.
- **[QA-02] Тестовые фикстуры** — `@Nikii-fnchek` · P0 · `area:qa` · (QA-03)
  Корректные PDF/DOCX, пустые, битые, нестандартные шрифты → `tests/fixtures`.
- **[QA-03] E2E Playwright** — `@Nikii-fnchek` · P1 · `area:qa` · (QA-02)
  Сценарий: загрузка → индексация → поиск → результаты.
- **[QA-04] Нагрузочные тесты (50 пользователей)** — `@Nikii-fnchek` · P2 · `area:qa` · (QA-04)
- **[QA-05] Precision@3** — `@Nikii-fnchek` · P2 · `area:qa` · (QA-05)
  10 эталонных запросов, таблица результатов.
- **[QA-06] User Guide (PDF/MD)** — `@Nikii-fnchek` · P1 · `docs` · (QA-06)

### E10. Документация

- **[DOC-01] README** — `@svyat0s1av` (+ вклад BE/FE) · P0 · `docs`
  Все 11 пунктов из ТЗ §17: описание, стек, архитектура, запуск через compose, отдельный запуск back/front, как работает MTUCI-токен, почему не используем логин/пароль ЛК, API, тестовые пользователи, скриншоты.
- **[DOC-02] Swagger/OpenAPI вычитка** — `@LikhachevAlexey` · P1 · `docs`
  Описания, примеры, корректные HTTP-статусы (200/400/404/500).

---

## Календарная привязка (из PDF)

- **Неделя 1 (дни 1–6):** S-01…S-03, BE-A1…A3, BE-D1…D3, BE-S1, FE-01…FE-03, DO-01…DO-02, QA-01…QA-02. День 5 — интеграция №1. День 6 — дневник/отчёт.
- **Неделя 2 (дни 7–12):** BE-S3…S5, очереди, FE-04…FE-08, DO-03…DO-04, QA-03…QA-06, MTUCI-стретч. День 9 — интеграция №2. День 11 — дневник. День 12 — предзащита.

## Definition of Done для PR в `dev`

1. Линт и тесты зелёные. 2. Ревью тимлида получено. 3. Контракт API совпадает с типами на фронте. 4. Нет секретов/токенов в коде и логах. 5. Публичные функции задокументированы.
