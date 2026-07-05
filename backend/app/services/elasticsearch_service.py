"""Elasticsearch: индекс с русским анализатором, индексация чанков, поиск.

BE-S1: ensure_index() — создаёт индекс documents с russian analyzer.
BE-S2: index_chunks() — записывает чанки документа в ES.
BE-S3: search_chunks() — multi_match по text с подсветкой.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from elasticsearch import AsyncElasticsearch, NotFoundError

from app.core.config import settings

log = logging.getLogger(__name__)

INDEX = "documents"

_INDEX_BODY = {
    "settings": {
        "analysis": {"analyzer": {"default": {"type": "russian"}}},
    },
    "mappings": {
        "properties": {
            "chunk_id":    {"type": "keyword"},
            "document_id": {"type": "keyword"},
            "file_name":   {"type": "keyword"},
            "file_type":   {"type": "keyword"},
            "page_number": {"type": "integer"},
            "text":        {"type": "text", "analyzer": "russian"},
            "uploaded_at": {"type": "date"},
        }
    },
}


def _client() -> AsyncElasticsearch:
    return AsyncElasticsearch(settings.elasticsearch_url)


async def ensure_index() -> None:
    """Создаёт индекс documents, если не существует. Вызывается при старте."""
    es = _client()
    try:
        exists = await es.indices.exists(index=INDEX)
        if not exists:
            await es.indices.create(index=INDEX, body=_INDEX_BODY)
            log.info("ES: индекс '%s' создан", INDEX)
        else:
            log.debug("ES: индекс '%s' уже существует", INDEX)
    except Exception as exc:
        # Не роняем приложение если ES недоступен при старте
        log.warning("ES: не удалось инициализировать индекс: %s", exc)
    finally:
        await es.close()


async def index_chunks(
    document_id: uuid.UUID,
    file_name: str,
    file_type: str,
    chunks: list[dict],
) -> None:
    """Индексирует чанки документа в ES (BE-S2).

    chunks — список dict с ключами: chunk_id, page_number, text.
    """
    if not chunks:
        return
    es = _client()
    try:
        now = datetime.now(timezone.utc).isoformat()
        operations: list[dict] = []
        for c in chunks:
            operations.append({"index": {"_index": INDEX, "_id": c["chunk_id"]}})
            operations.append({
                "chunk_id":    c["chunk_id"],
                "document_id": str(document_id),
                "file_name":   file_name,
                "file_type":   file_type,
                "page_number": c["page_number"],
                "text":        c["text"],
                "uploaded_at": now,
            })
        resp = await es.bulk(operations=operations, refresh=True)
        if resp.get("errors"):
            log.warning("ES bulk errors для документа %s", document_id)
    except Exception as exc:
        log.warning("ES: ошибка индексации документа %s: %s", document_id, exc)
    finally:
        await es.close()


async def delete_document_chunks(document_id: uuid.UUID) -> None:
    """Удаляет все чанки документа из ES при DELETE /documents/{id}."""
    es = _client()
    try:
        await es.delete_by_query(
            index=INDEX,
            body={"query": {"term": {"document_id": str(document_id)}}},
        )
    except NotFoundError:
        pass
    except Exception as exc:
        log.warning("ES: ошибка удаления чанков документа %s: %s", document_id, exc)
    finally:
        await es.close()


async def search_chunks(query: str, size: int = 10) -> dict:
    """Полнотекстовый поиск multi_match по полю text с подсветкой (BE-S3)."""
    es = _client()
    try:
        return await es.search(
            index=INDEX,
            body={
                "size": size,
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["text"],
                        "type": "best_fields",
                    }
                },
                "highlight": {
                    "fields": {"text": {}},
                    "pre_tags": ["<mark>"],
                    "post_tags": ["</mark>"],
                    "fragment_size": 300,
                    "number_of_fragments": 1,
                },
            },
        )
    finally:
        await es.close()
