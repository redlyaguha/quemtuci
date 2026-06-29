"""Модели Lesson и ExamEvent (ТЗ §7, §12). Скелет — [BE-M4].

Lesson: id, user_id, group_name, source, external_id, date, day, parity, number,
time_start, time_end, discipline, lesson_type, room, teachers, comment, is_online,
is_exam, raw_json, created_at.
ExamEvent: id, user_id, group_name, source, date, time_start, time_end, discipline,
event_type, room, teachers, comment, link, raw_json.
"""
# TODO [BE-M4]: SQLAlchemy-модели Lesson, ExamEvent (+ PracticeDefenseEvent seed, [BE-P1]).
