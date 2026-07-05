import { api } from "./client";
import type { SearchResponse } from "../types";

interface SearchHistoryItem {
  query: string;
}

/** Поиск по базе знаний. Контракт backend — [BE-S3], [BE-S4]. Экран — [FE-04]. */
export const searchApi = {
  search: (q: string) =>
    api.get<SearchResponse>("/search", { params: { q } }).then((r) => r.data),

  history: () =>
    api.get<Array<string | SearchHistoryItem>>("/search/history").then((r) =>
      r.data.map((item) => (typeof item === "string" ? item : item.query))
    ),

  clearHistory: () => api.delete("/search/history").then(() => ({ ok: true })),
};
