import type { ReactNode } from "react";
import { colors } from "../theme";

/** Карточка-метрика для дашбордов. */
export function StatCard({
  label,
  value,
  hint,
  hintColor,
}: {
  label: string;
  value: ReactNode;
  hint?: string;
  hintColor?: string;
}) {
  return (
    <div
      style={{
        flex: "1 1 150px",
        background: colors.surface,
        border: `1px solid ${colors.border}`,
        borderRadius: 18,
        padding: 18,
      }}
    >
      <div style={{ color: colors.textMuted, fontSize: 13 }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, marginTop: 4 }}>{value}</div>
      {hint && (
        <div style={{ fontSize: 12, color: hintColor ?? colors.textMuted, marginTop: 2 }}>{hint}</div>
      )}
    </div>
  );
}
