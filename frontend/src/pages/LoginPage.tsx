import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Icon, type IconName } from "../components/Icon";
import { useAuth } from "../hooks/useAuth";
import { ROUTES } from "../routes";
import { colors, font } from "../theme";
import type { Role } from "../types";

/**
 * Вход в систему. Каркас [FE-01] даёт рабочий demo-вход по ролям, чтобы
 * проверить роутинг и защищённые маршруты. Полная страница (форма
 * MTUCI/TECH-токена с предупреждением, оформление) — [FE-02].
 */

const DEMO_ROLES: { role: Role; title: string; sub: string; icon: IconName; color: string }[] = [
  { role: "student", title: "Войти как студент", sub: "Очереди, поиск, документы", icon: "grad", color: colors.student },
  { role: "teacher", title: "Войти как преподаватель", sub: "Создание очередей и dashboard", icon: "book", color: colors.teacher },
  { role: "admin", title: "Войти как администратор", sub: "Статистика и модерация базы", icon: "shield", color: colors.admin },
];

export default function LoginPage() {
  const { loginDemo } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [busy, setBusy] = useState<Role | null>(null);

  const from = (location.state as { from?: { pathname: string } } | null)?.from?.pathname ?? ROUTES.dashboard;

  const handleLogin = async (role: Role) => {
    setBusy(role);
    try {
      await loginDemo(role);
      navigate(from, { replace: true });
    } finally {
      setBusy(null);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: colors.bg,
        padding: "40px 28px",
        fontFamily: font.family,
        color: colors.text,
      }}
    >
      <div style={{ width: "100%", maxWidth: 400, animation: "fadeUp .4s ease both" }}>
        <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-.6px", margin: "0 0 6px" }}>
          Вход в систему
        </h2>
        <p style={{ color: colors.textMuted, fontSize: 15, margin: "0 0 28px" }}>
          Выберите роль, чтобы продолжить в демо-режиме
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {DEMO_ROLES.map((r) => (
            <button
              key={r.role}
              onClick={() => handleLogin(r.role)}
              disabled={busy !== null}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 14,
                textAlign: "left",
                width: "100%",
                background: colors.surface,
                border: `1px solid ${colors.border}`,
                borderRadius: 16,
                padding: 16,
                cursor: busy ? "default" : "pointer",
                opacity: busy && busy !== r.role ? 0.6 : 1,
              }}
            >
              <div
                style={{
                  width: 42,
                  height: 42,
                  borderRadius: 12,
                  background: r.color,
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flex: "0 0 auto",
                }}
              >
                <Icon name={r.icon} size={20} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 15 }}>{r.title}</div>
                <div style={{ color: colors.textMuted, fontSize: 13, marginTop: 1 }}>{r.sub}</div>
              </div>
              <div style={{ color: "#C2C5D2" }}>
                <Icon name="chev" size={18} />
              </div>
            </button>
          ))}
        </div>

        <div
          style={{
            marginTop: 22,
            padding: "12px 14px",
            background: "#F4F2FF",
            border: "1px solid #E6E2FF",
            borderRadius: 12,
            color: "#5B53B8",
            fontSize: 12.5,
            lineHeight: 1.5,
          }}
        >
          Это демо-режим. Вход по MTUCI/TECH-токену добавляется в [FE-02]; токен уходит только на
          backend.
        </div>
      </div>
    </div>
  );
}
