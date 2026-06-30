// Типы домена. Должны соответствовать контракту backend API (см. /docs).
// Базовый набор — [FE-01]. Расширяется по мере реализации страниц [FE-02]..[FE-08].

export type Role = "student" | "teacher" | "admin";

/** Текущий пользователь (ответ GET /auth/me, /auth/demo). */
export interface User {
  id: number | string;
  name: string;
  role: Role;
  /** Группа студента / кафедра преподавателя — affiliation. */
  group?: string | null;
  department?: string | null;
  telegram_id?: string | null;
}

/** Ответ авторизации: наш JWT + профиль. */
export interface AuthResponse {
  access_token: string;
  token_type?: string;
  user: User;
}

// ---------- Документы ----------

export type DocumentType = "PDF" | "DOCX";
export type DocumentStatus = "uploading" | "indexing" | "done" | "error";

export interface DocumentItem {
  id: number | string;
  name: string;
  type: DocumentType;
  date?: string;
  size?: string;
  /** Кол-во проиндексированных фрагментов (чанков). */
  frags?: number;
  status: DocumentStatus;
  /** Ссылка для просмотра файла (object URL для загруженных в этой сессии). */
  url?: string;
}

// ---------- Поиск ----------

export interface SearchResult {
  doc: string;
  type: DocumentType;
  page: number;
  /** Релевантность 0..1. */
  rel: number;
  /** Фрагмент текста (бекенд возвращает с тегами подсветки). */
  text: string;
}

export interface SearchResponse {
  query: string;
  total: number;
  results: SearchResult[];
}

// ---------- Очереди ----------

export type QueueType = "Лабораторная" | "Консультация" | "Защита" | "Пересдача";
export type QueueStatus = "open" | "live" | "closed";

export interface QueueMember {
  id: number | string;
  name: string;
  /**
   * Идентификатор пользователя, занявшего место. «Это я» вычисляется
   * сравнением с текущим пользователем, а не хранимым флагом — иначе позиция
   * ошибочно показывается другим ролям. На бэкенде проставляется по JWT.
   */
  userId?: number | string;
}

export interface Queue {
  id: number | string;
  title: string;
  discipline: string;
  qtype: QueueType;
  teacher: string;
  room: string;
  group: string;
  when: string;
  max: number;
  status: QueueStatus;
  comment?: string;
  students: QueueMember[];
}

/** Тело запроса на создание очереди (POST /queues). */
export interface QueueCreate {
  title: string;
  discipline: string;
  qtype: QueueType;
  group: string;
  room: string;
  when: string;
  max: number;
  comment?: string;
}

// ---------- Интеграция MTUCI/TECH ----------

export interface IntegrationStatus {
  connected: boolean;
  /** ISO-дата последней синхронизации. */
  last_sync?: string | null;
}
