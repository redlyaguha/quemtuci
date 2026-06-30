/**
 * Дизайн-токены «Кампуса». Извлечены из HTML-прототипа (docs/prototype.html)
 * и собраны в одном месте, чтобы страницы [FE-02]..[FE-08] не дублировали цвета.
 */

export const colors = {
  // бренд
  primary: "#4F46E5",
  primaryHover: "#4338CA",
  primarySoft: "#EEF0FE",
  accent: "#7C4DFF",
  gradient: "linear-gradient(150deg,#4F46E5,#7C4DFF)",

  // роли
  student: "#4F46E5",
  teacher: "#0E9F6E",
  admin: "#7C3AED",

  // поверхности
  bg: "#EEF0F6",
  bgApp: "#F5F6FB",
  surface: "#FFFFFF",
  surfaceMuted: "#FAFBFE",
  border: "#E7E9F1",
  borderMuted: "#EEF0F6",

  // текст
  text: "#15161F",
  textSoft: "#5B5E6E",
  textMuted: "#8A8D9C",
  textFaint: "#9A9DAC",

  // статусы
  success: "#16A34A",
  successSoft: "#EAF8EF",
  warning: "#B45309",
  warningSoft: "#FEF4E2",
  danger: "#D7494E",
  dangerSoft: "#FDECEC",
  info: "#2C6BD6",
  infoSoft: "#E8F0FE",
  live: "#7C3AED",
  liveSoft: "#F1ECFE",

  highlight: "#FCE96A",
} as const;

export const radii = {
  sm: "9px",
  md: "11px",
  lg: "14px",
  xl: "16px",
  pill: "999px",
} as const;

export const font = {
  family: "'Onest', system-ui, sans-serif",
  mono: "'Spline Sans Mono', monospace",
} as const;

/** Карта статусов очередей/документов → подпись и цвета чипа. */
export const statusMeta: Record<
  string,
  { label: string; color: string; bg: string }
> = {
  done: { label: "Готово", color: colors.success, bg: colors.successSoft },
  indexing: { label: "Индексация…", color: colors.warning, bg: colors.warningSoft },
  uploading: { label: "Загрузка…", color: colors.info, bg: colors.infoSoft },
  error: { label: "Ошибка", color: colors.danger, bg: colors.dangerSoft },
  open: { label: "Открыта", color: colors.success, bg: colors.successSoft },
  live: { label: "Идёт сейчас", color: colors.live, bg: colors.liveSoft },
  closed: { label: "Закрыта", color: colors.textMuted, bg: "#F1F2F8" },
};

/** Подписи и цвета аватара по роли. */
export const roleMeta: Record<
  string,
  { label: string; color: string }
> = {
  student: { label: "Студент", color: colors.student },
  teacher: { label: "Преподаватель", color: colors.teacher },
  admin: { label: "Администратор", color: colors.admin },
};
