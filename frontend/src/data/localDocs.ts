import { MOCK_DOCUMENTS } from "./mock";
import type { DocumentItem } from "../types";

/**
 * Рантайн-стор документов для демо-режима — [FE-FIX].
 * Общий для страницы загрузки и базы знаний: загруженный документ виден на
 * обеих, открывается и удаляется в пределах сессии. Когда backend готов —
 * страницы используют ответы API, а стор остаётся фолбэком.
 */
let docs: DocumentItem[] = MOCK_DOCUMENTS.map((d) => ({ ...d }));

export const localDocs = {
  list: (): DocumentItem[] => docs,
  add: (d: DocumentItem): void => {
    docs = [d, ...docs];
  },
  remove: (id: string | number): void => {
    docs = docs.filter((d) => d.id !== id);
  },
};
