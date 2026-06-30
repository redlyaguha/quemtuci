import type { QueueType } from "../types";

/** Учебные группы (демо-набор; позже подтянутся из MTUCI/TECH). */
export const GROUPS = ["БПИ2403", "БВТ2401", "БСТ2302"] as const;

/** Типы очередей. */
export const QUEUE_TYPES: QueueType[] = ["Лабораторная", "Консультация", "Защита", "Пересдача"];
