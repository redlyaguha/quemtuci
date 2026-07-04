/**
 * Набор линейных иконок «Кампуса» — порт из HTML-прототипа.
 * Один общий SVG-каркас (currentColor, stroke), пути — в карте PATHS.
 */

const PATHS: Record<string, string> = {
  home: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.2-3.2"/>',
  upload: '<path d="M12 16V4"/><path d="m7 9 5-5 5 5"/><path d="M5 20h14"/>',
  queues:
    '<path d="M9 6h11"/><path d="M9 12h11"/><path d="M9 18h11"/><circle cx="4.5" cy="6" r="1.2"/><circle cx="4.5" cy="12" r="1.2"/><circle cx="4.5" cy="18" r="1.2"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 4-6.2 8-6.2S20 16 20 20"/>',
  file: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7.5v5l3 1.8"/>',
  plus: '<path d="M12 5v14"/><path d="M5 12h14"/>',
  check: '<path d="m5 12.5 4.5 4.5L19 6"/>',
  x: '<path d="M6 6l12 12"/><path d="M18 6 6 18"/>',
  chev: '<path d="m9 6 6 6-6 6"/>',
  logout:
    '<path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3"/><path d="M10 12h10"/><path d="m17 9 3 3-3 3"/>',
  bell: '<path d="M6 9a6 6 0 0 1 12 0c0 5 2 7 2 7H4s2-2 2-7"/><path d="M10 19.5a2 2 0 0 0 4 0"/>',
  alert:
    '<circle cx="12" cy="12" r="9"/><path d="M12 8v5"/><path d="M12 16.4v.2"/>',
  trash:
    '<path d="M4 7h16"/><path d="M9 7V5h6v2"/><path d="M6.5 7l1 13h9l1-13"/>',
  arrowUp: '<path d="M12 19V6"/><path d="m6.5 11 5.5-5.5L17.5 11"/>',
  arrowDown: '<path d="M12 5v13"/><path d="m6.5 13 5.5 5.5L17.5 13"/>',
  users:
    '<circle cx="9" cy="8" r="3.4"/><path d="M3 19c0-3 3-4.6 6-4.6S15 16 15 19"/><path d="M16 5.2a3 3 0 0 1 0 5.8"/><path d="M17.5 14.4c2 .5 3.5 1.8 3.5 4.6"/>',
  pin: '<path d="M12 21s7-5.5 7-11a7 7 0 0 0-14 0c0 5.5 7 11 7 11Z"/><circle cx="12" cy="10" r="2.4"/>',
  cal: '<rect x="3" y="5" width="18" height="16" rx="2.4"/><path d="M3 9.5h18"/><path d="M8 3v4"/><path d="M16 3v4"/>',
  book: '<path d="M5 4.5h11a2 2 0 0 1 2 2V20H7a2 2 0 0 0-2 2z"/><path d="M5 4.5V20"/>',
  grad: '<path d="m12 4 9 4-9 4-9-4 9-4Z"/><path d="M5 10v4.5c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V10"/>',
  shield: '<path d="M12 3 5 6v5c0 4.2 3 7.6 7 9 4-1.4 7-4.8 7-9V6z"/>',
  lab: '<path d="M9 3v6L4.5 18a2 2 0 0 0 1.8 3h11.4a2 2 0 0 0 1.8-3L15 9V3"/><path d="M8 3h8"/><path d="M7.5 14h9"/>',
  defense:
    '<path d="M12 3 5 6v5c0 4.2 3 7.6 7 9 4-1.4 7-4.8 7-9V6z"/><path d="m9.5 12 2 2 3.5-3.5"/>',
  chat: '<path d="M21 12a8 8 0 0 1-11.5 7.2L4 20l1-4.4A8 8 0 1 1 21 12Z"/>',
  retry: '<path d="M4 12a8 8 0 1 1 2.3 5.6"/><path d="M4 20v-4h4"/>',
  link: '<path d="M9.5 14.5 14.5 9.5"/><path d="M11 6.5l1.2-1.2a4 4 0 0 1 5.6 5.6L16.5 12"/><path d="M13 17.5l-1.2 1.2a4 4 0 0 1-5.6-5.6L7.5 12"/>',
};

export type IconName = keyof typeof PATHS;

interface IconProps {
  name: IconName;
  size?: number;
  strokeWidth?: number;
  className?: string;
}

export function Icon({ name, size = 20, strokeWidth = 1.8, className }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      dangerouslySetInnerHTML={{ __html: PATHS[name] ?? "" }}
    />
  );
}

/** Иконка по типу очереди. */
export function queueTypeIcon(qtype: string): IconName {
  const map: Record<string, IconName> = {
    Защита: "defense",
    practice_defense: "defense",
    Лабораторная: "lab",
    Консультация: "chat",
    Пересдача: "retry",
  };
  return map[qtype] ?? "queues";
}
