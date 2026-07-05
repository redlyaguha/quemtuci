import { NavLink, useNavigate, useLocation, matchPath } from "react-router-dom";
import type { CSSProperties } from "react";
import { Icon, type IconName } from "./Icon";
import { useAuth } from "../hooks/useAuth";
import { useMediaQuery } from "../hooks/useMediaQuery";
import { useTelegram } from "../hooks/useTelegram";
import { ROUTES } from "../routes";
import { colors, font, radii, roleMeta } from "../theme";

/**
 * Каркас приложения: боковое меню (десктоп), мобильная шапка и нижняя
 * навигация (мобайл). Адаптив 320–1920px и Telegram Mini App — [FE-08].
 */

/** Заголовок страницы по текущему пути (для мобильной шапки). */
const PAGE_TITLES: { pattern: string; title: string }[] = [
  { pattern: ROUTES.dashboard, title: "Главная" },
  { pattern: ROUTES.knowledge, title: "База знаний" },
  { pattern: ROUTES.upload, title: "Загрузка документов" },
  { pattern: ROUTES.queueDetail(), title: "Очередь" },
  { pattern: ROUTES.queues, title: "Очереди" },
  { pattern: ROUTES.profile, title: "Профиль" },
];

function pageTitle(pathname: string): string {
  return PAGE_TITLES.find((p) => matchPath(p.pattern, pathname))?.title ?? "Кампус";
}

interface NavItem {
  to: string;
  label: string;
  shortLabel: string;
  icon: IconName;
}

const NAV: NavItem[] = [
  { to: ROUTES.dashboard, label: "Главная", shortLabel: "Главная", icon: "home" },
  { to: ROUTES.knowledge, label: "База знаний", shortLabel: "Поиск", icon: "book" },
  { to: ROUTES.upload, label: "Загрузка", shortLabel: "Загрузка", icon: "upload" },
  { to: ROUTES.queues, label: "Очереди", shortLabel: "Очереди", icon: "queues" },
  { to: ROUTES.profile, label: "Профиль", shortLabel: "Профиль", icon: "user" },
];

/** Нижняя навигация мобайла — сокращённый набор. */
const BOTTOM_NAV: NavItem[] = [
  NAV[0],
  { to: ROUTES.knowledge, label: "Поиск", shortLabel: "Поиск", icon: "search" },
  NAV[3],
  NAV[4],
];

function initials(name: string): string {
  return name
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0])
    .join("")
    .toUpperCase();
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const isDesktop = useMediaQuery("(min-width: 880px)");
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  useTelegram(); // инициализация Telegram Mini App, если открыто внутри Telegram

  const onLogout = () => {
    logout();
    navigate(ROUTES.login, { replace: true });
  };

  const rm = user ? roleMeta[user.role] : null;
  const title = pageTitle(location.pathname);

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        background: colors.bgApp,
        fontFamily: font.family,
        color: colors.text,
      }}
    >
      {isDesktop && (
        <aside
          style={{
            width: 248,
            flex: "0 0 248px",
            background: colors.surface,
            borderRight: `1px solid ${colors.border}`,
            height: "100vh",
            position: "sticky",
            top: 0,
            display: "flex",
            flexDirection: "column",
            padding: "18px 14px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 11, padding: "6px 8px 18px" }}>
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: 10,
                background: colors.gradient,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#fff",
              }}
            >
              <Icon name="book" size={20} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 16, letterSpacing: "-.3px" }}>Кампус</div>
              <div style={{ fontSize: 11, color: colors.textFaint }}>база знаний · очереди</div>
            </div>
          </div>

          <nav style={{ display: "flex", flexDirection: "column", gap: 3, marginTop: 6 }}>
            {NAV.map((n) => (
              <NavLink key={n.to} to={n.to} style={navLinkStyle}>
                <span style={{ display: "flex", width: 20, justifyContent: "center" }}>
                  <Icon name={n.icon} size={19} />
                </span>
                <span style={{ flex: 1, textAlign: "left" }}>{n.label}</span>
              </NavLink>
            ))}
          </nav>

          {user && (
            <div style={{ marginTop: "auto", borderTop: `1px solid ${colors.borderMuted}`, paddingTop: 12 }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: 8,
                  borderRadius: 12,
                  background: "#F7F8FC",
                }}
              >
                <div
                  style={{
                    width: 34,
                    height: 34,
                    borderRadius: "50%",
                    background: rm?.color ?? colors.primary,
                    color: "#fff",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: 600,
                    fontSize: 13,
                  }}
                >
                  {initials(user.name)}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: 13,
                      fontWeight: 600,
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {user.name}
                  </div>
                  <div style={{ fontSize: 11, color: colors.textFaint }}>{rm?.label}</div>
                </div>
                <button
                  onClick={onLogout}
                  title="Выйти"
                  style={{
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    color: colors.textMuted,
                    padding: 6,
                    borderRadius: 8,
                    display: "flex",
                  }}
                >
                  <Icon name="logout" size={18} />
                </button>
              </div>
            </div>
          )}
        </aside>
      )}

      <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column" }}>
        {!isDesktop && (
          <header
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "14px 16px",
              borderBottom: `1px solid ${colors.borderMuted}`,
              background: colors.surface,
              position: "sticky",
              top: 0,
              zIndex: 20,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
              <div style={{ width: 30, height: 30, borderRadius: 9, background: colors.gradient, display: "flex", alignItems: "center", justifyContent: "center", color: "#fff" }}>
                <Icon name="book" size={18} />
              </div>
              <div style={{ fontWeight: 700, fontSize: 15 }}>{title}</div>
            </div>
            {user && (
              <button
                onClick={() => navigate(ROUTES.profile)}
                title="Профиль"
                style={{ width: 34, height: 34, borderRadius: "50%", background: rm?.color ?? colors.primary, color: "#fff", border: "none", fontWeight: 600, fontSize: 12, cursor: "pointer" }}
              >
                {initials(user.name)}
              </button>
            )}
          </header>
        )}

        <main style={{ padding: isDesktop ? "26px 30px 60px" : "16px 14px 84px", flex: 1 }}>
          {/* Ограничение ширины контента на сверхшироких экранах (до 1920px) */}
          <div style={{ width: "100%", maxWidth: 1400, margin: "0 auto" }}>{children}</div>
        </main>

        {!isDesktop && (
          <nav
            style={{
              position: "fixed",
              left: 0,
              right: 0,
              bottom: 0,
              display: "flex",
              borderTop: `1px solid ${colors.borderMuted}`,
              background: colors.surface,
              padding: "7px 6px 9px",
            }}
          >
            {BOTTOM_NAV.map((n) => (
              <NavLink key={n.to + n.shortLabel} to={n.to} style={bottomLinkStyle}>
                <Icon name={n.icon} size={22} />
                <span style={{ fontSize: 10.5, fontWeight: 600 }}>{n.shortLabel}</span>
              </NavLink>
            ))}
          </nav>
        )}
      </div>
    </div>
  );
}

function navLinkStyle({ isActive }: { isActive: boolean }): CSSProperties {
  return {
    display: "flex",
    alignItems: "center",
    gap: 11,
    width: "100%",
    border: "none",
    cursor: "pointer",
    padding: "10px 11px",
    borderRadius: radii.md,
    fontSize: 14,
    fontWeight: isActive ? 600 : 500,
    background: isActive ? colors.primarySoft : "transparent",
    color: isActive ? colors.primary : colors.textSoft,
    textDecoration: "none",
  };
}

function bottomLinkStyle({ isActive }: { isActive: boolean }): CSSProperties {
  return {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 3,
    padding: "5px 0",
    textDecoration: "none",
    color: isActive ? colors.primary : colors.textFaint,
  };
}
