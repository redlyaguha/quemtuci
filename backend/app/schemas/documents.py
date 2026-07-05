"""Pydantic-схемы для documents-эндпоинтов.

DocumentItem совпадает с TypeScript-типом DocumentItem на фронтенде.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, computed_field


class DocumentItem(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    status: str
    date: str | None = None
    size: str | None = None
    frags: int | None = None
    error_message: str | None = None
    uploaderName: str | None = None
    uploaderRole: str | None = None
    uploaderGroup: str | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_doc(cls, doc: object, chunk_count: int = 0, uploader: object | None = None) -> "DocumentItem":
        from app.models.document import Document
        from app.models.user import User, UserRole

        d: Document = doc  # type: ignore[assignment]
        u: User | None = uploader  # type: ignore[assignment]
        return cls(
            id=d.id,
            name=d.file_name,
            type=d.file_type.value,
            status=d.status.value,
            date=d.uploaded_at.isoformat() if d.uploaded_at else None,
            size=_human_size(d.file_size),
            frags=chunk_count,
            error_message=d.error_message,
            uploaderName=u.full_name if u else None,
            uploaderRole=u.role.value if u else None,
            uploaderGroup=u.group_name if (u and u.role == UserRole.student) else None,
        )


def _human_size(size_bytes: int) -> str:
    for unit in ("Б", "КБ", "МБ", "ГБ"):
        if size_bytes < 1024:
            return f"{size_bytes:.0f} {unit}"
        size_bytes /= 1024  # type: ignore[assignment]
    return f"{size_bytes:.1f} ГБ"
