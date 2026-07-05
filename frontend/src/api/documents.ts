import { api } from "./client";
import type { DocumentItem } from "../types";

/** Документы. Контракт backend — [BE-D1]..[BE-D4]. Экраны — [FE-03]. */
export const documentsApi = {
  /** Список документов. `mine` — только загруженные текущим пользователем. */
  list: (mine = false) =>
    api.get<DocumentItem[]>("/documents", { params: mine ? { mine: true } : undefined }).then((r) => r.data),

  get: (id: string | number) =>
    api.get<DocumentItem>(`/documents/${id}`).then((r) => r.data),

  /** Скачать оригинальный файл: сохраняет blob под именем документа. */
  download: async (id: string | number, name: string) => {
    const res = await api.get(`/documents/${id}/download`, { responseType: "blob" });
    const href = URL.createObjectURL(res.data as Blob);
    const a = document.createElement("a");
    a.href = href;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(href);
  },

  upload: (file: File, onUploadProgress?: (percent: number) => void) => {
    const form = new FormData();
    form.append("file", file);
    return api
      .post<DocumentItem>("/documents/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (e) => {
          if (onUploadProgress && e.total) {
            onUploadProgress(Math.round((e.loaded / e.total) * 100));
          }
        },
      })
      .then((r) => r.data);
  },

  remove: (id: string | number) =>
    api.delete(`/documents/${id}`).then(() => ({ ok: true })),
};
