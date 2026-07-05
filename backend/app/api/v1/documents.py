"""Документы: загрузка, список, получение, удаление.

BE-D1: POST /upload — валидация PDF/DOCX ≤20 МБ, UUID на документ.
BE-D2: извлечение текста (pdfplumber / python-docx).
BE-D3: чанкинг 1000 символов, перекрытие 100.
BE-D4: GET /, GET /{id}, DELETE /{id}.
"""
from __future__ import annotations

import uuid
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, Response, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, require_roles
from app.db.session import get_session
from app.models.document import Document, DocumentChunk, DocumentStatus, DocumentType
from app.models.user import User, UserRole
from app.schemas.auth import UserPublic
from app.schemas.documents import DocumentItem
from app.services import elasticsearch_service as es_svc
from app.services.document_parser import ParserError, chunk_pages, extract_text

_MIME_BY_TYPE = {
    DocumentType.pdf: "application/pdf",
    DocumentType.docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

router = APIRouter(prefix="/documents", tags=["documents"])

_MAX_SIZE = 20 * 1024 * 1024  # 20 МБ
_ALLOWED_TYPES = {
    "application/pdf": DocumentType.pdf,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocumentType.docx,
}
_ALLOWED_EXTENSIONS = {".pdf": DocumentType.pdf, ".docx": DocumentType.docx}

_401 = {"description": "Токен отсутствует или недействителен"}
_403 = {"description": "Требуется роль admin"}
_404 = {"description": "Документ не найден"}


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


@router.post(
    "/upload",
    response_model=DocumentItem,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить документ",
    response_description="Метаданные загруженного документа и количество чанков",
    responses={
        400: {"description": "Неверный формат файла, превышен лимит 20 МБ или файл пустой"},
        401: _401,
    },
)
async def upload_document(
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> DocumentItem:
    """Загрузка PDF или DOCX файла в базу знаний. Доступна всем авторизованным.

    Пайплайн обработки:
    1. Валидация типа файла (Content-Type / расширение) и размера (≤ 20 МБ)
    2. Извлечение текста постранично (pdfplumber для PDF, python-docx для DOCX)
    3. Разбивка на чанки по 1000 символов с перекрытием 100
    4. Сохранение чанков в PostgreSQL
    5. Индексация в Elasticsearch (русский анализатор)

    Статус документа меняется: `uploading` → `indexing` → `done` (или `error`).
    """
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
        content=content,
    )
    session.add(doc)
    await session.flush()

    uploader = await session.get(User, current_user.id)

    try:
        pages = extract_text(content, doc_type.value)
        doc.status = DocumentStatus.indexing
        await session.flush()
    except ParserError as exc:
        doc.status = DocumentStatus.error
        doc.error_message = str(exc)
        await session.commit()
        return DocumentItem.from_doc(doc, chunk_count=0, uploader=uploader)

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

    await es_svc.index_chunks(
        document_id=doc.id,
        file_name=doc.file_name,
        file_type=doc.file_type.value,
        chunks=[{"chunk_id": tc.chunk_id, "page_number": tc.page_number, "text": tc.text}
                for tc in text_chunks],
    )

    return DocumentItem.from_doc(doc, chunk_count=len(text_chunks), uploader=uploader)


@router.get(
    "",
    response_model=list[DocumentItem],
    summary="Список документов",
    response_description="Документы, отсортированные по дате загрузки (новые первыми)",
    responses={401: _401},
)
async def list_documents(
    mine: bool = Query(False, description="Только документы, загруженные текущим пользователем"),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(get_current_user),
) -> list[DocumentItem]:
    """Список документов базы знаний с информацией о загрузившем.

    Доступен всем авторизованным. При `mine=true` — только свои загрузки.
    """
    stmt = (
        select(Document, func.count(DocumentChunk.id).label("cnt"), User)
        .outerjoin(DocumentChunk, DocumentChunk.document_id == Document.id)
        .outerjoin(User, User.id == Document.uploaded_by)
        .group_by(Document.id, User.id)
        .order_by(Document.uploaded_at.desc())
    )
    if mine:
        stmt = stmt.where(Document.uploaded_by == current_user.id)
    result = await session.execute(stmt)
    return [DocumentItem.from_doc(row.Document, chunk_count=row.cnt, uploader=row.User) for row in result]


@router.get(
    "/{document_id}",
    response_model=DocumentItem,
    summary="Документ по ID",
    response_description="Метаданные документа и количество чанков",
    responses={401: _401, 404: _404},
)
async def get_document(
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _: UserPublic = Depends(get_current_user),
) -> DocumentItem:
    """Получить метаданные конкретного документа по UUID."""
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Документ не найден")
    cnt_result = await session.execute(
        select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == document_id)
    )
    cnt = cnt_result.scalar_one()
    uploader = await session.get(User, doc.uploaded_by) if doc.uploaded_by else None
    return DocumentItem.from_doc(doc, chunk_count=cnt, uploader=uploader)


@router.get(
    "/{document_id}/download",
    summary="Скачать документ",
    response_description="Оригинальный файл (PDF/DOCX)",
    responses={
        401: _401,
        404: {"description": "Документ не найден или файл не сохранён"},
    },
)
async def download_document(
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _: UserPublic = Depends(get_current_user),
) -> Response:
    """Скачать оригинальный файл документа. Доступно всем авторизованным."""
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Документ не найден")
    if doc.content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл недоступен для скачивания (загружен до включения хранения)",
        )
    filename = quote(doc.file_name)
    return Response(
        content=doc.content,
        media_type=_MIME_BY_TYPE.get(doc.file_type, "application/octet-stream"),
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    response_class=Response,
    summary="Удалить документ",
    response_description="Документ удалён (нет тела ответа)",
    responses={401: _401, 403: _403, 404: _404},
)
async def delete_document(
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _: UserPublic = Depends(require_roles(UserRole.admin, UserRole.teacher)),
) -> None:
    """Удалить документ, его чанки и записи в Elasticsearch. Для **admin** и **teacher**."""
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Документ не найден")
    await session.delete(doc)
    await session.commit()
    await es_svc.delete_document_chunks(document_id)
