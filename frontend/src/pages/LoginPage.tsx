import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { AxiosError } from "axios";
import { Icon, type IconName } from "../components/Icon";
import { useAuth } from "../hooks/useAuth";
import { ROUTES } from "../routes";
import { colors, font } from "../theme";
import type { Role } from "../types";

/**
 * Вход в систему — [FE-02].
 * Два способа входа:
 *  - demo-кнопки по ролям (student/teacher/admin);
 *  - форма пользовательского MTUCI/TECH-токена.
 * Токен отправляется ТОЛЬКО на наш backend (см. предупреждение в форме).
 */

const DEMO_ROLES: { role: Role; title: string; sub: string; icon: IconName; color: string }[] = [
  { role: "student", title: "Войти как студент", sub: "Очереди, поиск, документы", icon: "grad", color: colors.student },
  { role: "teacher", title: "Войти как преподаватель", sub: "Создание очередей и dashboard", icon: "book", color: colors.teacher },
  { role: "admin", title: "Войти как администратор", sub: "Статистика и модерация базы", icon: "shield", color: colors.admin },
];

function errorText(err: unknown): string {
  if (err instanceof AxiosError) {
    const detail = (err.response?.data as { detail?: string } | undefined)?.detail;
    if (detail) return detail;
    if (err.response?.status === 401) return "Неверный или просроченный токен";
    if (!err.response) return "Сервер недоступен. Попробуйте позже";
  }
  return "Не удалось войти. Попробуйте ещё раз";
}

export default function LoginPage() {
  const { loginDemo, loginMtuci } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [busy, setBusy] = useState<Role | "mtuci" | null>(null);
  const [token, setToken] = useState("");
  const [showToken, setShowToken] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const from =
    (location.state as { from?: { pathname: string } } | null)?.from?.pathname ?? ROUTES.dashboard;

  const handleDemo = async (role: Role) => {
    setError(null);
    setBusy(role);
    try {
      await loginDemo(role);
      navigate(from, { replace: true });
    } catch (err) {
      setError(errorText(err));
    } finally {
      setBusy(null);
    }
  };

  const handleMtuci = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token.trim() || busy) return;
    setError(null);
    setBusy("mtuci");
    try {
      await loginMtuci(token.trim());
      navigate(from, { replace: true });
    } catch (err) {
      setError(errorText(err));
    } finally {
      setBusy(null);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexWrap: "wrap",
        background: colors.bg,
        fontFamily: font.family,
        color: colors.text,
      }}
    >
      {/* Брендовая панель */}
      <div
        style={{
          flex: "1 1 420px",
          minHeight: "100vh",
          background: "linear-gradient(150deg,#4F46E5 0%,#6D5DF6 55%,#7C4DFF 100%)",
          color: "#fff",
          padding: "56px 52px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div style={{ position: "absolute", width: 420, height: 420, borderRadius: "50%", background: "rgba(255,255,255,.08)", top: -140, right: -120 }} />
        <div style={{ position: "absolute", width: 260, height: 260, borderRadius: "50%", background: "rgba(255,255,255,.06)", bottom: -90, left: -60 }} />

        <div style={{ display: "flex", alignItems: "center", gap: 12, position: "relative" }}>
          <div
            style={{
              width: 42,
              height: 42,
              borderRadius: 12,
              background: "rgba(255,255,255,.16)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Icon name="book" size={20} />
          </div>
          <div style={{ fontWeight: 700, fontSize: 20, letterSpacing: "-.4px" }}>Кампус</div>
        </div>

        <div style={{ position: "relative", maxWidth: 440 }}>
          <div style={{ fontSize: 13, fontWeight: 600, letterSpacing: "1.5px", textTransform: "uppercase", opacity: 0.7, marginBottom: 18 }}>
            Учебная практика
          </div>
          <h1 style={{ fontSize: 42, lineHeight: 1.08, fontWeight: 800, letterSpacing: "-1.2px", margin: "0 0 18px" }}>
            Университетская база знаний и учебные очереди
          </h1>
          <p style={{ fontSize: 16, lineHeight: 1.6, opacity: 0.86, margin: 0 }}>
            Интеллектуальный поиск по внутренним документам университета и удобная запись в учебные
            очереди — в одном сервисе. Работает как сайт и как Telegram Mini App.
          </p>
        </div>

        <div style={{ position: "relative", display: "flex", gap: 26, fontSize: 13, opacity: 0.78 }}>
          <div><div style={{ fontSize: 22, fontWeight: 700 }}>4</div>документа</div>
          <div><div style={{ fontSize: 22, fontWeight: 700 }}>286</div>фрагментов</div>
          <div><div style={{ fontSize: 22, fontWeight: 700 }}>3</div>активные очереди</div>
        </div>
      </div>

      {/* Форма входа */}
      <div
        style={{
          flex: "1 1 420px",
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "40px 28px",
        }}
      >
        <div style={{ width: "100%", maxWidth: 400, animation: "fadeUp .4s ease both" }}>
          <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-.6px", margin: "0 0 6px" }}>
            Вход в систему
          </h2>
          <p style={{ color: colors.textMuted, fontSize: 15, margin: "0 0 24px" }}>
            Выберите роль для демо-режима или войдите по токену МТУСИ/TECH
          </p>

          {error && (
            <div
              role="alert"
              style={{
                marginBottom: 16,
                padding: "11px 14px",
                background: colors.dangerSoft,
                border: `1px solid #F4D6D8`,
                borderRadius: 12,
                color: colors.danger,
                fontSize: 13,
                lineHeight: 1.5,
              }}
            >
              {error}
            </div>
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {DEMO_ROLES.map((r) => (
              <button
                key={r.role}
                onClick={() => handleDemo(r.role)}
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

          {/* Разделитель */}
          <div style={{ display: "flex", alignItems: "center", gap: 12, margin: "22px 0 18px" }}>
            <div style={{ flex: 1, height: 1, background: colors.border }} />
            <span style={{ fontSize: 12.5, color: colors.textFaint }}>или по токену</span>
            <div style={{ flex: 1, height: 1, background: colors.border }} />
          </div>

          {/* Форма MTUCI/TECH-токена */}
          <form onSubmit={handleMtuci}>
            <label htmlFor="mtuci-token" style={{ display: "block", fontSize: 12.5, fontWeight: 600, color: colors.textSoft, marginBottom: 6 }}>
              MTUCI / TECH-токен
            </label>
            <div style={{ position: "relative", display: "flex" }}>
              <input
                id="mtuci-token"
                type={showToken ? "text" : "password"}
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="Вставьте токен tech.mtuci.ru"
                autoComplete="off"
                style={{
                  flex: 1,
                  minWidth: 0,
                  border: `1px solid ${colors.border}`,
                  borderRadius: 12,
                  padding: "12px 44px 12px 13px",
                  fontSize: 14,
                  background: colors.surfaceMuted,
                  color: colors.text,
                  fontFamily: font.mono,
                }}
              />
              <button
                type="button"
                onClick={() => setShowToken((v) => !v)}
                title={showToken ? "Скрыть" : "Показать"}
                style={{
                  position: "absolute",
                  right: 6,
                  top: "50%",
                  transform: "translateY(-50%)",
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: colors.textMuted,
                  padding: 6,
                  fontSize: 12,
                  display: "flex",
                  alignItems: "center",
                }}
              >
                {showToken ? "Скрыть" : "Показать"}
              </button>
            </div>

            <button
              type="submit"
              disabled={!token.trim() || busy !== null}
              style={{
                marginTop: 12,
                width: "100%",
                background: colors.primary,
                color: "#fff",
                border: "none",
                borderRadius: 12,
                padding: 13,
                fontWeight: 600,
                fontSize: 15,
                cursor: !token.trim() || busy ? "default" : "pointer",
                opacity: !token.trim() || busy ? 0.6 : 1,
              }}
            >
              {busy === "mtuci" ? "Входим…" : "Войти по токену"}
            </button>
          </form>

          <div
            style={{
              marginTop: 16,
              padding: "12px 14px",
              background: "#FFF8E8",
              border: "1px solid #F6E6BC",
              borderRadius: 12,
              color: "#8A6D2A",
              fontSize: 12.5,
              lineHeight: 1.55,
              display: "flex",
              gap: 9,
            }}
          >
            <span aria-hidden style={{ flex: "0 0 auto" }}>🔒</span>
            <span>
              Токен отправляется <b>только на наш backend</b> и хранится в зашифрованном виде. На
              сторонние сервисы он не передаётся, во фронтенде не сохраняется.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
