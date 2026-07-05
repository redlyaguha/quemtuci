/**
 * Форматирование даты/времени в "ДД.ММ.ГГГГ · ЧЧ:ММ".
 *
 * Backend отдаёт ISO-строки: время занятий без таймзоны ("2026-07-06T13:00:00")
 * и даты загрузки в UTC ("2026-07-05T17:56:20.818635+00:00"). Демо-данные — уже
 * готовые строки ("28.06 · 12:20").
 *
 * ISO разбираем через Date, чтобы UTC-время корректно переводилось в локальное
 * (иначе на экране «кривое» время). Готовые строки и чистые даты возвращаем как есть.
 */
const pad = (n: number) => String(n).padStart(2, "0");

export function formatWhen(when: string): string {
  if (!when) return "—";
  if (!when.includes("T")) return when; // уже готовая строка (демо-данные)

  const d = new Date(when);
  if (!Number.isNaN(d.getTime())) {
    const date = `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()}`;
    const time = `${pad(d.getHours())}:${pad(d.getMinutes())}`;
    return `${date} · ${time}`;
  }

  // Запасной разбор, если Date не справился.
  const [datePart, timePart = ""] = when.split("T");
  const [y, m, day] = datePart.split("-");
  const hm = timePart.slice(0, 5);
  if (!y || !m || !day) return when;
  return hm ? `${day}.${m}.${y} · ${hm}` : `${day}.${m}.${y}`;
}
