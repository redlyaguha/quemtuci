import { api } from "./client";
import type { Queue, QueueCreate } from "../types";

export interface QueueFilters {
  group?: string;
  teacher?: string;
  status?: string;
  date?: string;
}

/** Учебные очереди. Контракт backend — [BE-Q1]..[BE-Q4]. Экраны — [FE-06]. */
export const queuesApi = {
  list: (filters?: QueueFilters) =>
    api.get<Queue[]>("/queues", { params: filters }).then((r) => r.data),

  get: (id: string | number) =>
    api.get<Queue>(`/queues/${id}`).then((r) => r.data),

  create: (body: QueueCreate) =>
    api.post<Queue>("/queues", toBackendQueueCreate(body)).then((r) => r.data),

  join: (id: string | number) =>
    api.post<Queue>(`/queues/${id}/join`).then((r) => r.data),

  leave: (id: string | number) =>
    api.post<Queue>(`/queues/${id}/leave`).then((r) => r.data),

  reorder: (id: string | number, memberIds: (string | number)[]) =>
    api
      .patch<Queue>(`/queues/${id}/members/reorder`, { order: memberIds })
      .then((r) => r.data),

  removeMember: (id: string | number, memberId: string | number) =>
    api.delete<Queue>(`/queues/${id}/members/${memberId}`).then((r) => r.data),

  /** Отметить участника сдавшим, опционально с оценкой. */
  completeMember: (id: string | number, memberId: string | number, grade: number | null) =>
    api
      .patch<Queue>(`/queues/${id}/members/${memberId}/complete`, { grade })
      .then((r) => r.data),

  close: (id: string | number) =>
    api.patch<Queue>(`/queues/${id}/close`).then((r) => r.data),
};

function toBackendQueueCreate(body: QueueCreate) {
  const { date, time_start } = parseWhen(body.when);
  return {
    title: body.title,
    discipline: body.discipline,
    qtype: body.qtype,
    group: body.group,
    room: body.room,
    date,
    time_start,
    max: body.max,
    comment: body.comment,
  };
}

function parseWhen(value: string): { date: string; time_start: string } {
  const match = value.match(/(\d{2})\.(\d{2})(?:\.(\d{4}))?\s*[·,]?\s*(\d{1,2}):(\d{2})/);
  if (!match) {
    const today = new Date().toISOString().slice(0, 10);
    return { date: today, time_start: "09:00:00" };
  }
  const [, dd, mm, yyyy, hh, min] = match;
  return {
    date: `${yyyy ?? new Date().getFullYear()}-${mm}-${dd}`,
    time_start: `${hh.padStart(2, "0")}:${min}:00`,
  };
}
