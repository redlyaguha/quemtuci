import type { QueueCreate, QueueType } from "../types";

/** Учебные группы (демо-набор; позже подтянутся из MTUCI/TECH). */
export const GROUPS = ["БПИ2403", "БВТ2401", "БСТ2302"] as const;

/** Типы очередей. */
export const QUEUE_TYPES: QueueType[] = ["Лабораторная", "Консультация", "Защита", "Пересдача"];

/**
 * Предзаполнение очереди на защиту учебной практики 06.07.2026 — [FE-P2].
 * Поля соответствуют событию защиты практики (ТЗ §8).
 */
export const PRACTICE_DEFENSE_PREFILL: QueueCreate = {
  title: "Защита учебной практики",
  discipline: "Учебная практика",
  qtype: "Защита",
  group: GROUPS[0],
  room: "А-301",
  when: "06.07 · 10:00",
  max: 20,
  comment:
    "Защита отчётов по учебной практике. Подходите по позиции с готовым отчётом и презентацией.",
};
