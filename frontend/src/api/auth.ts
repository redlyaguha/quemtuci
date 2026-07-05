import { api } from "./client";
import type { AuthResponse, Role, User } from "../types";

/**
 * Авторизация. Контракт backend — [BE-A2], [BE-A3], [BE-M3].
 * Реальное подключение к формам входа — [FE-02].
 */
export const authApi = {
  /** Демо-вход для роли student/teacher/admin. */
  demo: (role: Role) =>
    api.post<AuthResponse>("/auth/demo", { role }).then((r) => r.data),

  /** Вход по пользовательскому MTUCI/TECH-токену. */
  mtuciToken: (token: string) =>
    api.post<AuthResponse>("/auth/mtuci-token", { token }).then((r) => r.data),

  /** Текущий пользователь по JWT. */
  me: () => api.get<User>("/auth/me").then((r) => r.data),
};
