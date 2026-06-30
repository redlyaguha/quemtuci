import { MOCK_QUEUES } from "./mock";
import type { Queue } from "../types";

/**
 * Рантайм-стор очередей для демо-режима — [FE-06].
 * Пока backend-эндпоинты очередей не реализованы, страницы (список и детали)
 * работают с этим общим хранилищем, чтобы созданные/изменённые очереди были
 * согласованы при навигации в пределах сессии. Когда API готов — страницы
 * используют ответы API, а стор остаётся лишь фолбэком.
 */
let queues: Queue[] = MOCK_QUEUES.map((q) => ({
  ...q,
  // Стабильный номер-талон по исходному порядку записи.
  students: q.students.map((s, i) => ({ ...s, seq: s.seq ?? i + 1 })),
}));

export const localQueues = {
  list: (): Queue[] => queues,
  get: (id: string | number): Queue | undefined =>
    queues.find((q) => String(q.id) === String(id)),
  add: (q: Queue): void => {
    queues = [q, ...queues];
  },
  update: (q: Queue): void => {
    queues = queues.map((x) => (x.id === q.id ? q : x));
  },
};
