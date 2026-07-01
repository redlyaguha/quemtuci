"""Документы: загрузка, список, получение, удаление.

BE-D1: POST /upload — валидация PDF/DOCX ≤20 МБ, UUID на документ.
BE-D2: извлечение текста (pdfplumber / python-docx).
BE-D3: чанкинг 1000 символов, перекрытие 100.
BE-D4: GET /, GET /{id}, DELETE /{id}.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, require_roles
from app.db.session import get_session
from app.models.document import Document, DocumentChunk, DocumentStatus, DocumentType
from app.models.user import UserRole
from app.schemas.auth import UserPublic
from app.schemas.documents import DocumentItem
from app.services.document_parser import ParserError, chunk_pages, extract_text

router = APIRouter(prefix="/documents", tags=["documents"])

_MAX_SIZE = 20 * 1024 * 1024  # 20 МБ
_ALLOWED_TYPES = {
    "application/pdf": DocumentType.pdf,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocumentType.docx,
}
_ALLOWED_EXTENSIONS = {".pdf": DocumentType.pdf, ".docx": DocumentType.docx}


def _detect_type(filename: str, content_type: str | None) -> DocumentType:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if content_type and content_type in _ALLOWED_TYPES:
        return _ALLOWED_TYPES[content_type]
    if ext in _ALLOWED_EXTENSIONS:
        return _ALLOWED_EXTENSIONS[ext]
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Поддерживаются только PDF и DOCX файлы",
    )


@router.post("/upload", response_model=DocumentItem, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_roles(UserRole.admin)),
) -> DocumentItem:
    """Загрузка PDF/DOCX (≤20 МБ). Только admin. [BE-D1, BE-D2, BE-D3]."""
    doc_type = _detect_type(file.filename or "", file.content_type)

    content = await file.read()
    if len(content) > _MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Размер файла превышает 20 МБ (получено {len(content) // (1024*1024)} МБ)",
        )
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Файл пустой")

    doc = Document(
        id=uuid.uuid4(),
        file_name=file.filename or "unnamed",
        file_type=doc_type,
        file_size=len(content),
        status=DocumentStatus.uploading,
        uploaded_by=current_user.id,
    )
    session.add(doc)
    await session.flush()  # получаем doc.id без коммита

    # --- BE-D2: извлечение текста ---
    try:
        pages = extract_text(content, doc_type.value)
        doc.status = DocumentStatus.indexing
        await session.flush()
    except ParserError as exc:
        doc.status = DocumentStatus.error
        doc.error_message = str(exc)
        await session.commit()
        return DocumentItem.from_doc(doc, chunk_count=0)

    # --- BE-D3: чанкинг ---
    text_chunks = chunk_pages(pages, doc.id)
    for tc in text_chunks:
        session.add(
            DocumentChunk(
                document_id=doc.id,
                chunk_id=tc.chunk_id,
                page_number=tc.page_number,
                text=tc.text,
            )
        )

    doc.status = DocumentStatus.done
    await session.commit()
    await session.refresh(doc)

    return DocumentItem.from_doc(doc, chunk_count=len(text_chunks))


@router.get("", response_model=list[DocumentItem])
async def list_documents(
    session: AsyncSession = Depends(get_session),
    _: UserPublic = Depends(get_current_user),
) -> list[DocumentItem]:
    """Список документов. [BE-D4]."""
    result = await session.execute(
        select(Document, func.count(DocumentChunk.id).label("cnt"))
        .outerjoin(DocumentChunk, DocumentChunk.document_id == Document.id)
        .group_by(Document.id)
        .order_by(Document.uploaded_at.desc())
    )
    return [DocumentItem.from_doc(row.Document, chunk_count=row.cnt) for row in result]


@router.get("/{document_id}", response_model=DocumentItem)
async def get_document(
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _: UserPublic = Depends(get_current_user),
) -> DocumentItem:
    """Документ по id. [BE-D4]."""
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Документ не найден")
    cnt_result = await session.execute(
        select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == document_id)
    )
    cnt = cnt_result.scalar_one()
    return DocumentItem.from_doc(doc, chunk_count=cnt)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _: UserPublic = Depends(require_roles(UserRole.admin)),
) -> None:
    """Удаление документа (только admin). [BE-D4]."""
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Документ не найден")
    await session.delete(doc)
    await session.commit()
