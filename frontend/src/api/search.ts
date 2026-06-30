import { api } from "./client";
import type { SearchResponse } from "../types";

/** Поиск по базе знаний. Контракт backend — [BE-S3], [BE-S4]. Экран — [FE-04]. */
export const searchApi = {
  search: (q: string) =>
    api.get<SearchResponse>("/search", { params: { q } }).then((r) => r.data),

  history: () => api.get<string[]>("/search/history").then((r) => r.data),

  clearHistory: () => api.delete("/search/history").then((r) => r.data),
};
