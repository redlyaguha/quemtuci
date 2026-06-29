"""Интеграция с tech.mtuci.ru по пользовательскому токену. Скелет — [BE-M2].

ВАЖНО: токен не логировать, не возвращать на frontend, хранить только зашифрованным.
При MTUCI_MOCK=true использовать фикстуры, не обращаться к порталу.

Методы:
- authenticate_by_token(token)
- get_profile(session)
- get_timetable(session)
- get_timetable_week(session, week)
- get_exams(session)
- sync_user_data(user)
"""
# TODO [BE-M2]: реализовать MtuciTechService с мок-режимом и нормализацией.


class MtuciTechService:
    """Заглушка сервиса MTUCI/TECH. Реализация — [BE-M2]/[BE-M4]."""
