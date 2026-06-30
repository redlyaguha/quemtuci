import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  authApi,
  setToken as persistToken,
  clearToken,
  getToken,
  AUTH_LOGOUT_EVENT,
} from "../api";
import type { Role, User } from "../types";

type AuthStatus = "loading" | "authenticated" | "anonymous";

interface AuthContextValue {
  user: User | null;
  role: Role | null;
  status: AuthStatus;
  loginDemo: (role: Role) => Promise<void>;
  loginMtuci: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Демо-профили для оффлайн-режима каркаса [FE-01]: пока backend-эндпоинты
 * /auth/* не реализованы ([BE-A2]/[BE-A3]), demo-вход поднимает локальную
 * сессию, чтобы роутинг и защищённые маршруты были проверяемы.
 * [FE-02] заменит фолбэк реальными ответами API.
 */
const DEMO_USERS: Record<Role, User> = {
  student: { id: "demo-student", name: "Соколов Артём", role: "student", group: "БПИ2403", telegram_id: "artem_sokolov" },
  teacher: { id: "demo-teacher", name: "Иванов И. И.", role: "teacher", department: "Кафедра программной инженерии", telegram_id: "ivanov_teach" },
  admin: { id: "demo-admin", name: "Петрова А. С.", role: "admin", department: "Модератор базы знаний", telegram_id: "admin_petrova" },
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<AuthStatus>("loading");

  const applySession = useCallback((token: string, nextUser: User) => {
    persistToken(token);
    setUser(nextUser);
    setStatus("authenticated");
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
    setStatus("anonymous");
  }, []);

  // Гидратация сессии при загрузке: если есть токен — тянем профиль.
  useEffect(() => {
    const token = getToken();
    if (!token) {
      setStatus("anonymous");
      return;
    }
    authApi
      .me()
      .then((me) => {
        setUser(me);
        setStatus("authenticated");
      })
      .catch(() => logout());
  }, [logout]);

  // Принудительный выход по событию из axios-интерсептора (401).
  useEffect(() => {
    const handler = () => logout();
    window.addEventListener(AUTH_LOGOUT_EVENT, handler);
    return () => window.removeEventListener(AUTH_LOGOUT_EVENT, handler);
  }, [logout]);

  const loginDemo = useCallback(
    async (role: Role) => {
      try {
        const res = await authApi.demo(role);
        applySession(res.access_token, res.user);
      } catch {
        // Фолбэк каркаса — см. комментарий к DEMO_USERS.
        applySession(`demo.${role}.token`, DEMO_USERS[role]);
      }
    },
    [applySession]
  );

  const loginMtuci = useCallback(
    async (token: string) => {
      const res = await authApi.mtuciToken(token);
      applySession(res.access_token, res.user);
    },
    [applySession]
  );

  const value = useMemo<AuthContextValue>(
    () => ({ user, role: user?.role ?? null, status, loginDemo, loginMtuci, logout }),
    [user, status, loginDemo, loginMtuci, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth должен использоваться внутри <AuthProvider>");
  return ctx;
}
