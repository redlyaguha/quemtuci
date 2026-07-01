"""Парсинг и чанкинг документов. Реализация — [BE-D2], [BE-D3].

extract_text   — извлечение текста постранично из PDF (pdfplumber) / DOCX (python-docx).
chunk_pages    — разбивка в чанки по 1000 символов с перекрытием 100 (ТЗ BE-D3).
"""
from __future__ import annotations

import io
import uuid
from dataclasses import dataclass

import pdfplumber
from docx import Document as DocxDocument


class ParserError(Exception):
    """Файл не удалось прочитать или текст не извлечь."""


@dataclass
class TextChunk:
    chunk_id: str
    page_number: int
    text: str


def extract_text(content: bytes, file_type: str) -> list[tuple[int, str]]:
    """Возвращает список (номер_страницы, текст).

    file_type: 'PDF' или 'DOCX' (регистр не важен).
    Бросает ParserError при любой ошибке чтения.
    """
    try:
        if file_type.upper() == "PDF":
            return _extract_pdf(content)
        return _extract_docx(content)
    except ParserError:
        raise
    except Exception as exc:
        raise ParserError(str(exc)) from exc


def _extract_pdf(content: bytes) -> list[tuple[int, str]]:
    pages: list[tuple[int, str]] = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        if not pdf.pages:
            raise ParserError("PDF не содержит страниц")
        for i, page in enumerate(pdf.pages, start=1):
            pages.append((i, page.extract_text() or ""))
    return pages


def _extract_docx(content: bytes) -> list[tuple[int, str]]:
    doc = DocxDocument(io.BytesIO(content))
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    if not full_text:
        return [(1, "")]
    # DOCX не имеет страниц — аппроксимируем по ~2000 символов.
    page_size = 2000
    pages: list[tuple[int, str]] = []
    for i, start in enumerate(range(0, len(full_text), page_size), start=1):
        pages.append((i, full_text[start : start + page_size]))
    return pages


def chunk_pages(
    pages: list[tuple[int, str]],
    document_id: uuid.UUID,
    chunk_size: int = 1000,
    overlap: int = 100,
) -> list[TextChunk]:
    """Разбивает текст страниц на перекрывающиеся чанки (ТЗ BE-D3).

    chunk_id: "<document_uuid>_<index>"
    page_number: страница, на которой начинается чанк.
    """
    full_text = ""
    page_at: list[int] = []
    for page_num, text in pages:
        for _ in text:
            page_at.append(page_num)
        full_text += text

    if not full_text.strip():
        return []

    chunks: list[TextChunk] = []
    start = 0
    idx = 0
    while start < len(full_text):
        end = start + chunk_size
        text_slice = full_text[start:end]
        page_number = page_at[start] if start < len(page_at) else 1
        chunks.append(
            TextChunk(
                chunk_id=f"{document_id}_{idx}",
                page_number=page_number,
                text=text_slice,
            )
        )
        start += chunk_size - overlap
        idx += 1

    return chunks
