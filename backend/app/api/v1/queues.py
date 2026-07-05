"""Учебные очереди: CRUD, запись/выход, управление.

BE-Q2: GET/POST /queues, GET /queues/{id}
BE-Q3: POST /queues/{id}/join, POST /queues/{id}/leave
BE-Q4: PATCH /queues/{id}/members/reorder, DELETE /queues/{id}/members/{mid}, PATCH /queues/{id}/close
"""
from __future__ import annotations

import uuid
from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, require_roles
from app.db.session import get_session
from app.models.queue import Queue, QueueMember, QueueStatus, QueueType
from app.models.user import User, UserRole
from app.schemas.auth import UserPublic
from app.schemas.queues import CompleteMemberRequest, QueueCreate, QueueMemberOut, QueueOut, ReorderRequest

router = APIRouter(prefix="/queues", tags=["queues"])

_401 = {"description": "Токен отсутствует или недействителен"}
_403 = {"description": "Недостаточно прав"}
_404 = {"description": "Очередь или участник не найдены"}


# ── хелперы ──────────────────────────────────────────────────────────────────

def _member_to_out(m: QueueMember, names: dict[uuid.UUID, str]) -> QueueMemberOut:
    return QueueMemberOut(
        id=m.id,
        userId=m.student_id,
        name=names.get(m.student_id, ""),
        seq=m.seq,
        position=m.position,
        passed=m.passed,
        grade=m.grade,
    )


async def _names_for(session: AsyncSession, user_ids: set[uuid.UUID | None]) -> dict[uuid.UUID, str]:
    """Карта id → полное имя для преподавателя и участников очереди."""
    ids = {i for i in user_ids if i is not None}
    if not ids:
        return {}
    rows = await session.execute(select(User.id, User.full_name).where(User.id.in_(ids)))
    return {row.id: row.full_name for row in rows}


async def _serialize_queue(session: AsyncSession, queue: Queue) -> QueueOut:
    """Собрать QueueOut, подтянув имена преподавателя и участников из users."""
    names = await _names_for(session, {queue.teacher_id, *(m.student_id for m in queue.members)})
    return QueueOut(
        id=queue.id,
        title=queue.title,
        discipline=queue.discipline,
        qtype=queue.type.value,
        teacher=names.get(queue.teacher_id, ""),
        room=queue.room,
        group=queue.group_name,
        when=f"{queue.date}T{queue.time_start}",
        max=queue.max_students,
        status=queue.status.value,
        comment=queue.comment,
        students=[_member_to_out(m, names) for m in sorted(queue.members, key=lambda m: m.position)],
    )


async def _get_queue_or_404(session: AsyncSession, queue_id: int) -> Queue:
    q = await session.get(Queue, queue_id)
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Очередь не найдена")
    return q


def _assert_owner(queue: Queue, user: UserPublic) -> None:
    """Только владелец-преподаватель или admin."""
    if user.role == UserRole.admin:
        return
    if user.role == UserRole.teacher and queue.teacher_id == user.id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на управление очередью")


# ── BE-Q2: CRUD ───────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=list[QueueOut],
    summary="Список очередей",
    response_description="Очереди, отсортированные по дате и времени начала",
    responses={401: _401},
)
async def list_queues(
    group: str | None = Query(None),
    teacher_id: uuid.UUID | None = Query(None),
    queue_status: str | None = Query(None, alias="status"),
    date: date_type | None = Query(None),
    session: AsyncSession = Depends(get_session),
    _: UserPublic = Depends(get_current_user),
) -> list[QueueOut]:
    """Список очередей с фильтрами. [BE-Q2]"""
    filters = []
    if group:
        filters.append(Queue.group_name == group)
    if teacher_id:
        filters.append(Queue.teacher_id == teacher_id)
    if queue_status:
        try:
            filters.append(Queue.status == QueueStatus(queue_status))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Неверный статус: {queue_status}")
    if date:
        filters.append(Queue.date == date)

    stmt = select(Queue).order_by(Queue.date, Queue.time_start)
    if filters:
        stmt = stmt.where(and_(*filters))
    result = await session.execute(stmt)
    queues = result.scalars().unique().all()
    return [await _serialize_queue(session, q) for q in queues]


@router.post(
    "",
    response_model=QueueOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать очередь",
    response_description="Созданная очередь (без участников)",
    responses={401: _401, 403: {"description": "Требуется роль teacher или admin"}, 422: {"description": "Ошибка валидации тела запроса"}},
)
async def create_queue(
    body: QueueCreate,
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_roles(UserRole.teacher, UserRole.admin)),
) -> QueueOut:
    """Создать очередь (teacher/admin). [BE-Q2]"""
    queue = Queue(
        title=body.title,
        discipline=body.discipline,
        group_name=body.group,
        teacher_id=current_user.id,
        room=body.room,
        date=body.date,
        time_start=body.time_start,
        time_end=body.time_end,
        type=body.qtype,
        status=QueueStatus.open,
        max_students=body.max,
        comment=body.comment,
    )
    session.add(queue)
    await session.commit()
    await session.refresh(queue)
    return await _serialize_queue(session, queue)


@router.get(
    "/{queue_id}",
    response_model=QueueOut,
    summary="Очередь по ID",
    response_description="Очередь со списком участников",
    responses={401: _401, 404: _404},
)
async def get_queue(
    queue_id: int,
    session: AsyncSession = Depends(get_session),
    _: UserPublic = Depends(get_current_user),
) -> QueueOut:
    """Детали очереди. [BE-Q2]"""
    return await _serialize_queue(session, await _get_queue_or_404(session, queue_id))


# ── BE-Q3: join / leave ───────────────────────────────────────────────────────

@router.post(
    "/{queue_id}/join",
    response_model=QueueOut,
    summary="Встать в очередь",
    response_description="Очередь с обновлённым списком участников",
    responses={
        400: {"description": "Очередь закрыта / переполнена / вы уже записаны"},
        401: _401,
        403: {"description": "Только студент может записаться в очередь"},
        404: _404,
    },
)
async def join_queue(
    queue_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_roles(UserRole.student)),
) -> QueueOut:
    """Встать в конец очереди. [BE-Q3]"""
    queue = await _get_queue_or_404(session, queue_id)

    if queue.status == QueueStatus.closed:
        raise HTTPException(status_code=400, detail="Очередь закрыта")

    if any(m.student_id == current_user.id for m in queue.members):
        raise HTTPException(status_code=400, detail="Вы уже записаны в эту очередь")

    if len(queue.members) >= queue.max_students:
        raise HTTPException(status_code=400, detail="Очередь заполнена")

    next_pos = max((m.position for m in queue.members), default=0) + 1
    next_seq = max((m.seq for m in queue.members), default=0) + 1
    member = QueueMember(
        queue_id=queue_id,
        student_id=current_user.id,
        position=next_pos,
        seq=next_seq,
    )
    session.add(member)
    await session.commit()
    await session.refresh(queue)
    return await _serialize_queue(session, queue)


@router.post(
    "/{queue_id}/leave",
    response_model=QueueOut,
    summary="Выйти из очереди",
    response_description="Очередь с пересчитанными позициями",
    responses={
        400: {"description": "Очередь уже закрыта"},
        401: _401,
        403: {"description": "Только студент может выйти из очереди"},
        404: {"description": "Вы не записаны в эту очередь"},
    },
)
async def leave_queue(
    queue_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_roles(UserRole.student)),
) -> QueueOut:
    """Выйти из очереди, пересчитать позиции. [BE-Q3]"""
    queue = await _get_queue_or_404(session, queue_id)

    if queue.status == QueueStatus.closed:
        raise HTTPException(status_code=400, detail="Очередь закрыта")

    member = next((m for m in queue.members if m.student_id == current_user.id), None)
    if not member:
        raise HTTPException(status_code=404, detail="Вы не записаны в эту очередь")

    left_pos = member.position
    await session.delete(member)

    for m in queue.members:
        if m.id != member.id and m.position > left_pos:
            m.position -= 1

    await session.commit()
    await session.refresh(queue)
    return await _serialize_queue(session, queue)


# ── BE-Q4: reorder / remove / close ──────────────────────────────────────────

@router.patch(
    "/{queue_id}/members/reorder",
    response_model=QueueOut,
    summary="Изменить порядок участников",
    response_description="Очередь с обновлёнными позициями (seq не меняется)",
    responses={
        400: {"description": "order содержит не все id участников"},
        401: _401,
        403: _403,
        404: _404,
    },
)
async def reorder_members(
    queue_id: int,
    body: ReorderRequest,
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> QueueOut:
    """Переставить участников (только владелец/admin). [BE-Q4]"""
    queue = await _get_queue_or_404(session, queue_id)
    _assert_owner(queue, current_user)

    member_map = {m.id: m for m in queue.members}
    if set(body.order) != set(member_map.keys()):
        raise HTTPException(status_code=400, detail="order должен содержать ровно все id участников")

    for new_pos, mid in enumerate(body.order, start=1):
        member_map[mid].position = new_pos

    await session.commit()
    await session.refresh(queue)
    return await _serialize_queue(session, queue)


@router.patch("/{queue_id}/members/{member_id}/complete", response_model=QueueOut)
async def complete_member(
    queue_id: int,
    member_id: int,
    body: CompleteMemberRequest,
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> QueueOut:
    """Отметить студента сдавшим (только владелец/admin). [FE-INT]"""
    queue = await _get_queue_or_404(session, queue_id)
    _assert_owner(queue, current_user)

    member = next((m for m in queue.members if m.id == member_id), None)
    if not member:
        raise HTTPException(status_code=404, detail="Участник не найден")
    if member.passed:
        raise HTTPException(status_code=400, detail="Участник уже отмечен сдавшим")

    left_pos = member.position
    member.passed = True
    member.grade = body.grade
    member.position = 0

    active = [m for m in queue.members if not m.passed and m.position > left_pos]
    for m in active:
        m.position -= 1

    await session.commit()
    await session.refresh(queue)
    return await _serialize_queue(session, queue)


@router.delete(
    "/{queue_id}/members/{member_id}",
    response_model=QueueOut,
    summary="Удалить участника из очереди",
    response_description="Очередь с пересчитанными позициями",
    responses={401: _401, 403: _403, 404: _404},
)
async def remove_member(
    queue_id: int,
    member_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> QueueOut:
    """Удалить студента из очереди (только владелец/admin). [BE-Q4]"""
    queue = await _get_queue_or_404(session, queue_id)
    _assert_owner(queue, current_user)

    member = next((m for m in queue.members if m.id == member_id), None)
    if not member:
        raise HTTPException(status_code=404, detail="Участник не найден")

    left_pos = member.position
    await session.delete(member)
    for m in queue.members:
        if m.id != member_id and m.position > left_pos:
            m.position -= 1

    await session.commit()
    await session.refresh(queue)
    return await _serialize_queue(session, queue)


@router.patch(
    "/{queue_id}/close",
    response_model=QueueOut,
    summary="Закрыть очередь",
    response_description="Очередь со статусом closed",
    responses={
        400: {"description": "Очередь уже закрыта"},
        401: _401,
        403: _403,
        404: _404,
    },
)
async def close_queue(
    queue_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> QueueOut:
    """Закрыть очередь (только владелец/admin). [BE-Q4]"""
    queue = await _get_queue_or_404(session, queue_id)
    _assert_owner(queue, current_user)

    if queue.status == QueueStatus.closed:
        raise HTTPException(status_code=400, detail="Очередь уже закрыта")

    queue.status = QueueStatus.closed
    await session.commit()
    await session.refresh(queue)
    return await _serialize_queue(session, queue)
