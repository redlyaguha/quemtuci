"""Документы: загрузка, список, получение, удаление.

Скелет — реализация в issue [BE-D1]..[BE-D4].
"""
from fastapi import APIRouter

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document() -> dict:
    """Загрузка PDF/DOCX (<=20 МБ), иначе 400. TODO: [BE-D1]."""
    raise NotImplementedError


@router.get("")
async def list_documents() -> list:
    """Список документов. TODO: [BE-D4]."""
    raise NotImplementedError


@router.get("/{document_id}")
async def get_document(document_id: str) -> dict:
    """Документ по id. TODO: [BE-D4]."""
    raise NotImplementedError


@router.delete("/{document_id}")
async def delete_document(document_id: str) -> dict:
    """Удаление документа (admin). TODO: [BE-D4]."""
    raise NotImplementedError
