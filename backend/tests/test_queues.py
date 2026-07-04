"""Тесты очередей: CRUD, join/leave, reorder/remove/close [BE-Q2, Q3, Q4]."""
from __future__ import annotations

import uuid
from datetime import date, time
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_session
from app.main import app
from app.models.queue import Queue, QueueMember, QueueStatus, QueueType


# ── UUID-заглушки ────────────────────────────────────────────────────────────
TEACHER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
STUDENT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
ADMIN_ID   = uuid.UUID("00000000-0000-0000-0000-000000000003")


# ── хелперы токенов ──────────────────────────────────────────────────────────

def _token(role: str) -> str:
    with TestClient(app) as c:
        return c.post("/api/v1/auth/demo", json={"role": role}).json()["access_token"]


# ── фабрики объектов ─────────────────────────────────────────────────────────

def _make_member(member_id: int = 1, student_id: uuid.UUID = STUDENT_ID,
                 position: int = 1, seq: int = 1) -> QueueMember:
    m = QueueMember()
    m.id = member_id
    m.student_id = student_id
    m.queue_id = 1
    m.position = position
    m.seq = seq
    m.passed = False
    m.grade = None
    return m


def _make_queue(
    queue_id: int = 1,
    teacher_id: uuid.UUID = TEACHER_ID,
    status: QueueStatus = QueueStatus.open,
    members: list[QueueMember] | None = None,
    max_students: int = 30,
) -> Queue:
    q = Queue()
    q.id = queue_id
    q.title = "Тестовая очередь"
    q.discipline = "Программирование"
    q.group_name = "БПИ2403"
    q.teacher_id = teacher_id
    q.room = "А-310"
    q.date = date(2026, 7, 6)
    q.time_start = time(13, 0)
    q.time_end = time(14, 30)
    q.type = QueueType.practice
    q.status = status
    q.max_students = max_students
    q.comment = None
    q.members = members if members is not None else []
    return q


def _mock_session(queue: Queue | None = None) -> AsyncMock:
    """Async-сессия, отдающая один объект Queue через session.get и execute."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.delete = AsyncMock()

    async def _get(model, pk):
        if model is Queue and queue is not None:
            return queue
        return None

    session.get = _get

    # Для list_queues: scalars().unique().all()
    scalars_mock = MagicMock()
    scalars_mock.unique = MagicMock(return_value=scalars_mock)
    scalars_mock.all = MagicMock(return_value=[queue] if queue else [])
    execute_result = MagicMock()
    execute_result.scalars = MagicMock(return_value=scalars_mock)
    session.execute = AsyncMock(return_value=execute_result)

    async def _refresh(obj):
        pass  # объект уже настроен заранее

    session.refresh = _refresh

    return session


# ── GET /queues ──────────────────────────────────────────────────────────────

def test_list_queues_requires_auth() -> None:
    with TestClient(app) as c:
        resp = c.get("/api/v1/queues")
    assert resp.status_code == 401


def test_list_queues_student_ok() -> None:
    queue = _make_queue()
    session = _mock_session(queue)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("student")
            resp = c.get("/api/v1/queues", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert data[0]["id"] == 1
    finally:
        app.dependency_overrides.pop(get_session, None)


# ── POST /queues ─────────────────────────────────────────────────────────────

def test_create_queue_student_forbidden() -> None:
    with TestClient(app) as c:
        token = _token("student")
        resp = c.post(
            "/api/v1/queues",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Сдача",
                "discipline": "МатАнализ",
                "qtype": "Лабораторная",
                "group": "БПИ2403",
                "room": "А-101",
                "date": "2026-07-06",
                "time_start": "10:00:00",
            },
        )
    assert resp.status_code == 403


def test_create_queue_teacher_ok() -> None:
    # _mock_session без очереди — refresh является no-op, объект уже заполнен endpoint-ом
    session = _mock_session()
    added: list = []
    original_add = session.add

    def _capture(obj):
        added.append(obj)
        if isinstance(obj, Queue):
            obj.id = 42
            obj.members = []
        return original_add(obj)

    session.add = _capture

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("teacher")
            resp = c.post(
                "/api/v1/queues",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "title": "Защита практики",
                    "discipline": "Учебная практика",
                    "qtype": "practice_defense",
                    "group": "БПИ2403",
                    "room": "А-310",
                    "date": "2026-07-06",
                    "time_start": "13:00:00",
                },
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["discipline"] == "Учебная практика"
        assert data["status"] == "open"
        assert any(isinstance(obj, Queue) for obj in added)
    finally:
        app.dependency_overrides.pop(get_session, None)


# ── POST /queues/{id}/join ────────────────────────────────────────────────────

def test_join_queue_teacher_forbidden() -> None:
    with TestClient(app) as c:
        token = _token("teacher")
        resp = c.post("/api/v1/queues/1/join", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_join_queue_closed_returns_400() -> None:
    queue = _make_queue(status=QueueStatus.closed)
    session = _mock_session(queue)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("student")
            resp = c.post("/api/v1/queues/1/join", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 400
        assert "закрыта" in resp.json()["detail"]
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_join_queue_already_in_returns_400() -> None:
    member = _make_member(student_id=STUDENT_ID)
    queue = _make_queue(members=[member])
    session = _mock_session(queue)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("student")
            resp = c.post("/api/v1/queues/1/join", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 400
        assert "уже записаны" in resp.json()["detail"]
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_join_queue_full_returns_400() -> None:
    members = [_make_member(member_id=i, student_id=uuid.uuid4(), position=i) for i in range(1, 3)]
    queue = _make_queue(members=members, max_students=2)
    session = _mock_session(queue)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("student")
            resp = c.post("/api/v1/queues/1/join", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 400
        assert "заполнена" in resp.json()["detail"]
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_join_queue_success() -> None:
    queue = _make_queue(members=[])
    session = _mock_session(queue)
    added: list = []
    original_add = session.add

    def _capture(obj):
        added.append(obj)
        if isinstance(obj, QueueMember):
            queue.members.append(obj)
        return original_add(obj)

    def _capture(obj):
        added.append(obj)
        if isinstance(obj, QueueMember):
            obj.id = 99       # DB-autoincrement
            obj.passed = False # DB-default
            queue.members.append(obj)
        return original_add(obj)

    session.add = _capture

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("student")
            resp = c.post("/api/v1/queues/1/join", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert any(isinstance(obj, QueueMember) for obj in added)
    finally:
        app.dependency_overrides.pop(get_session, None)


# ── POST /queues/{id}/leave ───────────────────────────────────────────────────

def test_leave_queue_not_in_returns_404() -> None:
    queue = _make_queue(members=[])
    session = _mock_session(queue)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("student")
            resp = c.post("/api/v1/queues/1/leave", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_leave_queue_recalculates_positions() -> None:
    m1 = _make_member(member_id=1, student_id=STUDENT_ID, position=1, seq=1)
    m2 = _make_member(member_id=2, student_id=uuid.uuid4(), position=2, seq=2)
    queue = _make_queue(members=[m1, m2])
    session = _mock_session(queue)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("student")
            resp = c.post("/api/v1/queues/1/leave", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 204
        # m2 должен сдвинуться с position=2 на position=1
        assert m2.position == 1
    finally:
        app.dependency_overrides.pop(get_session, None)


# ── PATCH /queues/{id}/members/reorder ───────────────────────────────────────

def test_reorder_non_owner_forbidden() -> None:
    queue = _make_queue(teacher_id=TEACHER_ID)
    session = _mock_session(queue)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            # student пытается переставить
            token = _token("student")
            resp = c.patch(
                "/api/v1/queues/1/members/reorder",
                headers={"Authorization": f"Bearer {token}"},
                json={"order": []},
            )
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_reorder_owner_ok() -> None:
    m1 = _make_member(member_id=1, position=1, seq=1)
    m2 = _make_member(member_id=2, student_id=uuid.uuid4(), position=2, seq=2)
    queue = _make_queue(members=[m1, m2])
    session = _mock_session(queue)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("teacher")
            resp = c.patch(
                "/api/v1/queues/1/members/reorder",
                headers={"Authorization": f"Bearer {token}"},
                json={"order": [2, 1]},
            )
        assert resp.status_code == 200
        # m2 теперь на позиции 1, m1 — на позиции 2
        assert m2.position == 1
        assert m1.position == 2
    finally:
        app.dependency_overrides.pop(get_session, None)


# ── DELETE /queues/{id}/members/{mid} ────────────────────────────────────────

def test_remove_member_non_owner_forbidden() -> None:
    queue = _make_queue(teacher_id=TEACHER_ID)
    session = _mock_session(queue)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("student")
            resp = c.delete("/api/v1/queues/1/members/1",
                            headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_remove_member_not_found() -> None:
    queue = _make_queue(members=[])
    session = _mock_session(queue)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("teacher")
            resp = c.delete("/api/v1/queues/1/members/999",
                            headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.pop(get_session, None)


# ── PATCH /queues/{id}/close ──────────────────────────────────────────────────

def test_close_queue_non_owner_forbidden() -> None:
    queue = _make_queue(teacher_id=TEACHER_ID)
    session = _mock_session(queue)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("student")
            resp = c.patch("/api/v1/queues/1/close",
                           headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_close_queue_already_closed_returns_400() -> None:
    queue = _make_queue(status=QueueStatus.closed)
    session = _mock_session(queue)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("teacher")
            resp = c.patch("/api/v1/queues/1/close",
                           headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 400
        assert "уже закрыта" in resp.json()["detail"]
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_close_queue_ok() -> None:
    queue = _make_queue(status=QueueStatus.open)
    session = _mock_session(queue)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("teacher")
            resp = c.patch("/api/v1/queues/1/close",
                           headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert queue.status == QueueStatus.closed
    finally:
        app.dependency_overrides.pop(get_session, None)


# ── seq стабильность ─────────────────────────────────────────────────────────

def test_seq_is_stable_after_reorder() -> None:
    """seq (талон) не меняется при перестановке позиций. [BE-Q3]"""
    m1 = _make_member(member_id=1, position=1, seq=1)
    m2 = _make_member(member_id=2, student_id=uuid.uuid4(), position=2, seq=2)
    queue = _make_queue(members=[m1, m2])
    session = _mock_session(queue)

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            token = _token("teacher")
            c.patch(
                "/api/v1/queues/1/members/reorder",
                headers={"Authorization": f"Bearer {token}"},
                json={"order": [2, 1]},
            )
        assert m1.seq == 1  # seq не изменился
        assert m2.seq == 2
    finally:
        app.dependency_overrides.pop(get_session, None)
