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
    api.post<Queue>("/queues", body).then((r) => r.data),

  join: (id: string | number) =>
    api.post<Queue>(`/queues/${id}/join`).then((r) => r.data),

  leave: (id: string | number) =>
    api.post<Queue>(`/queues/${id}/leave`).then((r) => r.data),

  reorder: (id: string | number, memberIds: (string | number)[]) =>
    api
      .patch<Queue>(`/queues/${id}/members/reorder`, { order: memberIds })
      .then((r) => r.data),

  removeMember: (id: string | number, memberId: string | number) =>
    api.delete(`/queues/${id}/members/${memberId}`).then((r) => r.data),

  close: (id: string | number) =>
    api.patch<Queue>(`/queues/${id}/close`).then((r) => r.data),
};
