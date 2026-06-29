import axios from "axios";

/**
 * HTTP-клиент с JWT-интерсептором. Скелет — [FE-01].
 */
export const api = axios.create({ baseURL: "/api/v1" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
