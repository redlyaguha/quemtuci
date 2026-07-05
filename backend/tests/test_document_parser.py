"""Тесты парсинга и чанкинга [BE-D2, BE-D3]."""
from __future__ import annotations

import io
import uuid

import pytest
from docx import Document as DocxDocument

from app.services.document_parser import ParserError, chunk_pages, extract_text


# ---------- фикстуры ----------

def _make_docx(text: str) -> bytes:
    doc = DocxDocument()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ---------- BE-D2: извлечение текста ----------

def test_extract_docx_returns_pages() -> None:
    content = _make_docx("Привет мир! " * 50)
    pages = extract_text(content, "DOCX")
    assert len(pages) >= 1
    full = "".join(t for _, t in pages)
    assert "Привет" in full


def test_extract_docx_empty_document() -> None:
    content = _make_docx("")
    pages = extract_text(content, "DOCX")
    assert pages == [(1, "")]


def test_extract_broken_bytes_raises_parser_error() -> None:
    with pytest.raises(ParserError):
        extract_text(b"not a real pdf or docx", "PDF")


def test_extract_broken_docx_raises_parser_error() -> None:
    with pytest.raises(ParserError):
        extract_text(b"\x00\x01\x02garbage", "DOCX")


# ---------- BE-D3: чанкинг ----------

def test_chunk_basic_split() -> None:
    doc_id = uuid.uuid4()
    pages = [(1, "A" * 2500)]
    chunks = chunk_pages(pages, doc_id, chunk_size=1000, overlap=100)
    # 2500 символов → чанки с шагом 900: 0, 900, 1800 → 3 чанка
    assert len(chunks) == 3


def test_chunk_ids_are_unique() -> None:
    doc_id = uuid.uuid4()
    pages = [(1, "X" * 5000)]
    chunks = chunk_pages(pages, doc_id)
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))


def test_chunk_id_format() -> None:
    doc_id = uuid.uuid4()
    pages = [(1, "hello world")]
    chunks = chunk_pages(pages, doc_id)
    assert chunks[0].chunk_id == f"{doc_id}_0"


def test_chunk_overlap() -> None:
    doc_id = uuid.uuid4()
    text = "0123456789" * 200  # 2000 символов
    pages = [(1, text)]
    chunks = chunk_pages(pages, doc_id, chunk_size=1000, overlap=100)
    # Второй чанк должен начинаться с символа 900 (1000 - 100)
    assert chunks[1].text == text[900:1900]


def test_chunk_empty_text_returns_empty() -> None:
    doc_id = uuid.uuid4()
    chunks = chunk_pages([(1, "   ")], doc_id)
    assert chunks == []


def test_chunk_page_number_propagated() -> None:
    doc_id = uuid.uuid4()
    pages = [(3, "X" * 500), (4, "Y" * 500)]
    chunks = chunk_pages(pages, doc_id, chunk_size=1000, overlap=0)
    assert chunks[0].page_number == 3
