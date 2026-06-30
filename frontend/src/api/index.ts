// Барель API-слоя — единая точка импорта для страниц.
export { api, getToken, setToken, clearToken, AUTH_LOGOUT_EVENT } from "./client";
export { authApi } from "./auth";
export { documentsApi } from "./documents";
export { searchApi } from "./search";
export { queuesApi } from "./queues";
export type { QueueFilters } from "./queues";
export { integrationsApi, scheduleApi } from "./integrations";
