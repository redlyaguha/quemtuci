"""Учебные очереди: CRUD, запись/выход, управление.

Скелет — реализация в issue [BE-Q1]..[BE-Q4].
"""
from fastapi import APIRouter

router = APIRouter(prefix="/queues", tags=["queues"])


@router.get("")
async def list_queues() -> list:
    """Список очередей с фильтрами group/teacher/status/date. TODO: [BE-Q2]."""
    raise NotImplementedError


@router.post("")
async def create_queue() -> dict:
    """Создать очередь (teacher/admin). TODO: [BE-Q2]."""
    raise NotImplementedError


@router.get("/{queue_id}")
async def get_queue(queue_id: int) -> dict:
    """Детали очереди. TODO: [BE-Q2]."""
    raise NotImplementedError


@router.post("/{queue_id}/join")
async def join_queue(queue_id: int) -> dict:
    """Запись студента в конец очереди. TODO: [BE-Q3]."""
    raise NotImplementedError


@router.post("/{queue_id}/leave")
async def leave_queue(queue_id: int) -> dict:
    """Выход из очереди + пересчёт позиций. TODO: [BE-Q3]."""
    raise NotImplementedError


@router.patch("/{queue_id}/members/reorder")
async def reorder_members(queue_id: int) -> dict:
    """Изменение порядка студентов (владелец). TODO: [BE-Q4]."""
    raise NotImplementedError


@router.delete("/{queue_id}/members/{member_id}")
async def remove_member(queue_id: int, member_id: int) -> dict:
    """Удаление студента из очереди (владелец). TODO: [BE-Q4]."""
    raise NotImplementedError


@router.patch("/{queue_id}/close")
async def close_queue(queue_id: int) -> dict:
    """Закрытие очереди (владелец). TODO: [BE-Q4]."""
    raise NotImplementedError
