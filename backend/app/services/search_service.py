"""Поиск (multi_match по text) + кеш Redis. Скелет — [BE-S3]/[BE-S5].

Ответ: chunk_id, file_name, page, text, score, highlights. Кеш TTL 5 мин,
ключ учитывает query + user_id/role.
"""
# TODO [BE-S3]/[BE-S5]: search(query, user) с подсветкой и кешем.
