import { Navigate, useLocation } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "../hooks/useAuth";
import { ROUTES } from "../routes";
import { colors } from "../theme";

/**
 * Защищённая область: пока идёт гидратация сессии — спиннер;
 * аноним — редирект на /login (с запоминанием исходного пути).
 */
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { status } = useAuth();
  const location = useLocation();

  if (status === "loading") {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: colors.textMuted,
          fontFamily: "system-ui",
        }}
      >
        Загрузка…
      </div>
    );
  }

  if (status === "anonymous") {
    return <Navigate to={ROUTES.login} replace state={{ from: location }} />;
  }

  return <>{children}</>;
}
