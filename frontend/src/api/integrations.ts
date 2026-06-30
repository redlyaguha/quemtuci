import { api } from "./client";
import type { IntegrationStatus } from "../types";

/** Интеграция MTUCI/TECH. Контракт backend — [BE-M3]. Экран — [FE-07]. */
export const integrationsApi = {
  status: () =>
    api.get<IntegrationStatus>("/integrations/mtuci/status").then((r) => r.data),

  sync: () =>
    api.post<IntegrationStatus>("/integrations/mtuci/sync").then((r) => r.data),

  disconnect: () =>
    api.delete("/integrations/mtuci/disconnect").then((r) => r.data),
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
