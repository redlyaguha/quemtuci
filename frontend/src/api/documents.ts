import { api } from "./client";
import type { DocumentItem } from "../types";

/** Документы. Контракт backend — [BE-D1]..[BE-D4]. Экраны — [FE-03]. */
export const documentsApi = {
  list: () => api.get<DocumentItem[]>("/documents").then((r) => r.data),

  get: (id: string | number) =>
    api.get<DocumentItem>(`/documents/${id}`).then((r) => r.data),

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
