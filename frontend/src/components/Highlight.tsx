import { Fragment } from "react";
import { colors } from "../theme";

/**
 * Подсветка вхождений запроса в тексте жёлтым маркером.
 * Токены короче 3 символов игнорируются (как в прототипе) — чтобы не
 * подсвечивать предлоги и союзы.
 */
export function Highlight({ text, query }: { text: string; query: string }) {
  const q = query.trim().toLowerCase();
  const tokens = q.split(/\s+/).filter((t) => t.length > 2);
  if (!tokens.length) return <>{text}</>;

  const escaped = tokens.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const re = new RegExp(`(${escaped.join("|")})`, "gi");
  const set = new Set(tokens);
  const parts = text.split(re);

  return (
    <>
      {parts.map((p, i) =>
        set.has(p.toLowerCase()) ? (
          <mark key={i} style={{ background: colors.highlight, color: "inherit", borderRadius: 3, padding: "0 1px" }}>
            {p}
          </mark>
        ) : (
          <Fragment key={i}>{p}</Fragment>
        )
      )}
    </>
  );
}
