"""Модели Document и DocumentChunk (ТЗ §12). Скелет — [BE-D1]/[BE-D3].

Document: id, uuid, file_name, file_type, file_size, status, uploaded_by, uploaded_at, error_message.
DocumentChunk: id, document_id, chunk_id, page_number, text, elasticsearch_id.
"""
# TODO [BE-D1]/[BE-D3]: SQLAlchemy-модели Document, DocumentChunk.
