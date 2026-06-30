// Константы маршрутов — единый источник путей для навигации и роутера.
export const ROUTES = {
  login: "/login",
  dashboard: "/dashboard",
  knowledge: "/knowledge",
  upload: "/upload",
  queues: "/queues",
  queueDetail: (id: string | number = ":id") => `/queues/${id}`,
  profile: "/profile",
} as const;
