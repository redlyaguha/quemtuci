import axios, { AxiosError } from "axios";

/**
 * HTTP-клиент с JWT-интерсептором — [FE-01].
 *
 * - В запрос подставляется `Authorization: Bearer <token>` из localStorage.
 * - На 401 токен сбрасывается и пользователь уводится на /login
 *   (через кастомное событие, чтобы не тянуть зависимость от роутера сюда).
 */

export const TOKEN_KEY = "access_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

/** Событие принудительного выхода — слушается в AuthProvider. */
export const AUTH_LOGOUT_EVENT = "campus:auth-logout";

export const api = axios.create({ baseURL: "/api/v1" });

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      clearToken();
      window.dispatchEvent(new CustomEvent(AUTH_LOGOUT_EVENT));
    }
    return Promise.reject(error);
  }
);
