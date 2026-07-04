import { api } from "./client";
import type { IntegrationStatus } from "../types";

interface IntegrationApiStatus extends IntegrationStatus {
  status?: string;
  last_sync_at?: string | null;
}

/** Интеграция MTUCI/TECH. Контракт backend — [BE-M3]. Экран — [FE-07]. */
export const integrationsApi = {
  status: () =>
    api.get<IntegrationApiStatus>("/integrations/mtuci/status").then((r) => ({
      connected: r.data.connected,
      last_sync: r.data.last_sync ?? r.data.last_sync_at ?? null,
    })),

  sync: () =>
    api.post<IntegrationApiStatus>("/integrations/mtuci/sync").then((r) => ({
      connected: r.data.connected ?? r.data.status === "connected",
      last_sync: r.data.last_sync ?? r.data.last_sync_at ?? null,
    })),

  disconnect: () =>
    api.delete("/integrations/mtuci/disconnect").then(() => ({ ok: true })),
};

/** Расписание и события (защита практики). Контракт — [BE-M4], [BE-P1], [FE-P2]. */
export const scheduleApi = {
  my: () => api.get("/schedule/my").then((r) => r.data),

  events: () => api.get("/schedule/events").then((r) => r.data),

  createPracticeDefenseQueue: () =>
    api
      .post("/schedule/practice-defense/create-queue")
      .then((r) => r.data),
};
