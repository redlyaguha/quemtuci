import { colors, font } from "../theme";

/**
 * Временная заглушка экрана для каркаса [FE-01].
 * Реальное наполнение приходит в соответствующей issue (`issue`).
 */
export function PagePlaceholder({ title, issue }: { title: string; issue: string }) {
  return (
    <div style={{ animation: "fadeUp .3s both" }}>
      <h1 style={{ fontSize: 21, fontWeight: 700, letterSpacing: "-.5px", margin: "0 0 6px" }}>
        {title}
      </h1>
      <p style={{ color: colors.textMuted, fontSize: 14, margin: 0 }}>
        Экран в разработке — {issue}.
      </p>
      <div
        style={{
          marginTop: 18,
          background: colors.surface,
          border: `1px dashed ${colors.border}`,
          borderRadius: 16,
          padding: "42px 24px",
          textAlign: "center",
          color: colors.textFaint,
          fontFamily: font.family,
        }}
      >
        Содержимое будет добавлено в рамках {issue}.
      </div>
    </div>
  );
}
