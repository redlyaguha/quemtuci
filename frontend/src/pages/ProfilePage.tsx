import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Icon } from "../components/Icon";
import { Toast } from "../components/Toast";
import { useAuth } from "../hooks/useAuth";
import { integrationsApi } from "../api";
import { ROUTES } from "../routes";
import { colors, font, roleMeta } from "../theme";
import type { IntegrationStatus } from "../types";

/**
 * Профиль пользователя и статус интеграции MTUCI/TECH — [FE-07].
 * ФИО/роль/группа, статус интеграции, кнопки «Синхронизировать» и «Отключить»
 * (дёргают integrationsApi). Настройки уведомлений — локально.
 */

function initials(name: string): string {
  return name.split(/\s+/).slice(0, 2).map((p) => p[0]).join("").toUpperCase();
}

const NOTIF_DEFS = [
  { key: "queue", label: "Изменения в моих очередях" },
  { key: "search", label: "Новые документы по подпискам" },
  { key: "schedule", label: "Напоминания о парах" },
] as const;

const NOTIF_STORAGE_KEY = "campus:notif-prefs";
const NOTIF_DEFAULTS: Record<string, boolean> = { queue: true, search: false, schedule: true };

function loadNotif(): Record<string, boolean> {
  try {
    const raw = localStorage.getItem(NOTIF_STORAGE_KEY);
    if (raw) return { ...NOTIF_DEFAULTS, ...JSON.parse(raw) };
  } catch {
    /* повреждённое значение — берём значения по умолчанию */
  }
  return NOTIF_DEFAULTS;
}

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [integration, setIntegration] = useState<IntegrationStatus>({ connected: false });
  const [intBusy, setIntBusy] = useState<"sync" | "disconnect" | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [notif, setNotif] = useState<Record<string, boolean>>(loadNotif);

  // Сохраняем настройки уведомлений (до появления backend-эндпоинта) в localStorage.
  useEffect(() => {
    localStorage.setItem(NOTIF_STORAGE_KEY, JSON.stringify(notif));
  }, [notif]);

  useEffect(() => {
    let alive = true;
    integrationsApi
      .status()
      .then((s) => alive && setIntegration(s))
      .catch(() => {/* нет данных — считаем не подключено */});
    return () => {
      alive = false;
    };
  }, []);

  if (!user) return null;
  const rm = roleMeta[user.role];
  const affiliation = user.group ? `Группа ${user.group}` : user.department ?? "—";
  const affiliationLabel = user.group ? "Группа" : "Подразделение";

  const sync = async () => {
    setIntBusy("sync");
    try {
      const s = await integrationsApi.sync();
      setIntegration(s);
      setToast("Профиль и расписание синхронизированы");
    } catch {
      setToast("Сервис интеграции недоступен");
    } finally {
      setIntBusy(null);
    }
  };

  const disconnect = async () => {
    setIntBusy("disconnect");
    try {
      await integrationsApi.disconnect();
      setIntegration({ connected: false });
      setToast("Интеграция отключена");
    } catch {
      setToast("Не удалось отключить интеграцию");
    } finally {
      setIntBusy(null);
    }
  };

  const onLogout = () => {
    logout();
    navigate(ROUTES.login, { replace: true });
  };

  return (
    <div style={{ animation: "fadeUp .3s both", maxWidth: 720 }}>
      {/* Шапка профиля */}
      <div style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 18, padding: 22, display: "flex", flexWrap: "wrap", gap: 16, alignItems: "center", marginBottom: 16 }}>
        <div style={{ width: 66, height: 66, borderRadius: "50%", background: rm.color, color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 24 }}>
          {initials(user.name)}
        </div>
        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: 21, fontWeight: 700, margin: 0 }}>{user.name}</h2>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 7, alignItems: "center" }}>
            <span style={{ background: colors.primarySoft, color: colors.primary, fontSize: 12, fontWeight: 600, padding: "3px 11px", borderRadius: 999 }}>{rm.label}</span>
            <span style={{ fontSize: 13, color: colors.textMuted }}>{affiliation}</span>
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 14 }}>
        {/* Личные данные */}
        <div style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 16, padding: 18 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, margin: "0 0 14px" }}>Личные данные</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 13 }}>
            <Field label="ФИО" value={user.name} />
            <Field label={affiliationLabel} value={affiliation} />
            <Field label="Telegram ID" value={user.telegram_id ? `@${user.telegram_id}` : "—"} mono />
          </div>
        </div>

        {/* Уведомления */}
        <div style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 16, padding: 18 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, margin: "0 0 14px" }}>Уведомления</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {NOTIF_DEFS.map((n) => {
              const on = notif[n.key];
              return (
                <button
                  key={n.key}
                  onClick={() => setNotif((s) => ({ ...s, [n.key]: !s[n.key] }))}
                  style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, padding: "9px 0", cursor: "pointer", background: "none", border: "none", textAlign: "left", width: "100%" }}
                >
                  <span style={{ fontSize: 13.5 }}>{n.label}</span>
                  <span style={{ width: 40, height: 23, borderRadius: 999, background: on ? colors.primary : "#D5D7E2", position: "relative", transition: ".15s", flex: "0 0 auto" }}>
                    <span style={{ width: 17, height: 17, borderRadius: "50%", background: "#fff", position: "absolute", top: 3, left: on ? 20 : 3, transition: ".15s", boxShadow: "0 1px 2px rgba(0,0,0,.2)" }} />
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Интеграция MTUCI/TECH */}
      <div style={{ background: "linear-gradient(135deg,#F7F6FF,#FFFFFF)", border: "1px solid #E6E2FF", borderRadius: 18, padding: 20, marginTop: 14 }}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 12, justifyContent: "space-between", alignItems: "flex-start" }}>
          <div style={{ display: "flex", gap: 13, alignItems: "center" }}>
            <div style={{ width: 46, height: 46, borderRadius: 13, background: "#fff", border: "1px solid #E6E2FF", display: "flex", alignItems: "center", justifyContent: "center", color: colors.primary }}>
              <Icon name="link" size={22} />
            </div>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 9, flexWrap: "wrap" }}>
                <h3 style={{ fontSize: 16, fontWeight: 700, margin: 0 }}>Интеграция с МТУСИ / TECH</h3>
                <StatusBadge connected={integration.connected} />
              </div>
              <div style={{ fontSize: 13, color: "#7A7D8C", marginTop: 4 }}>
                {integration.connected
                  ? integration.last_sync
                    ? `Последняя синхронизация: ${integration.last_sync}`
                    : "Расписание и группы подтягиваются автоматически"
                  : "Привяжите расписание, чтобы автоматически подтягивать пары и группы"}
              </div>
            </div>
          </div>

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button
              onClick={sync}
              disabled={intBusy !== null}
              style={{ background: colors.primary, color: "#fff", border: "none", borderRadius: 12, padding: "11px 18px", fontWeight: 600, fontSize: 13.5, cursor: intBusy ? "default" : "pointer", opacity: intBusy === "disconnect" ? 0.6 : 1, whiteSpace: "nowrap" }}
            >
              {intBusy === "sync" ? "Синхронизируем…" : "Синхронизировать"}
            </button>
            {integration.connected && (
              <button
                onClick={disconnect}
                disabled={intBusy !== null}
                style={{ background: "#fff", color: colors.danger, border: `1px solid #F4D6D8`, borderRadius: 12, padding: "11px 18px", fontWeight: 600, fontSize: 13.5, cursor: intBusy ? "default" : "pointer", opacity: intBusy === "sync" ? 0.6 : 1, whiteSpace: "nowrap" }}
              >
                {intBusy === "disconnect" ? "Отключаем…" : "Отключить"}
              </button>
            )}
          </div>
        </div>
        <div style={{ marginTop: 14, background: "#FFF8E8", border: "1px solid #F6E6BC", borderRadius: 12, padding: "12px 14px", fontSize: 12.5, color: "#8A6D2A", lineHeight: 1.55 }}>
          ⚠️ Токен МТУСИ/TECH хранится только на backend в зашифрованном виде. Реальная интеграция подключается через пользовательский токен.
        </div>
      </div>

      <button
        onClick={onLogout}
        style={{ marginTop: 16, background: colors.surface, border: `1px solid ${colors.border}`, color: colors.danger, borderRadius: 12, padding: "12px 18px", fontWeight: 600, fontSize: 14, cursor: "pointer", display: "flex", alignItems: "center", gap: 8 }}
      >
        <Icon name="logout" size={18} />
        Выйти из аккаунта
      </button>

      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </div>
  );
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <div style={{ fontSize: 12, color: colors.textFaint, marginBottom: 3 }}>{label}</div>
      <div style={{ fontSize: 14, fontWeight: 500, fontFamily: mono ? font.mono : undefined }}>{value}</div>
    </div>
  );
}

function StatusBadge({ connected }: { connected: boolean }) {
  return (
    <span style={{ background: connected ? colors.successSoft : "#F1F2F8", color: connected ? colors.success : colors.textMuted, fontSize: 11.5, fontWeight: 600, padding: "2px 9px", borderRadius: 999, display: "flex", alignItems: "center", gap: 5 }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: connected ? colors.success : "#B4B7C6" }} />
      {connected ? "Подключено" : "Не подключено"}
    </span>
  );
}
