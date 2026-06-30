import { statusMeta } from "../theme";

/** Чип статуса очереди/документа. Подписи и цвета — из theme.statusMeta. */
export function StatusChip({ status }: { status: string }) {
  const meta = statusMeta[status] ?? { label: "—", color: "#8A8D9C", bg: "#F1F2F8" };
  const pulsing = status === "live" || status === "indexing" || status === "uploading";

  return (
    <span
      style={{
        background: meta.bg,
        color: meta.color,
        fontSize: 11.5,
        fontWeight: 600,
        padding: "4px 11px",
        borderRadius: 999,
        whiteSpace: "nowrap",
        display: "inline-flex",
        alignItems: "center",
        gap: 5,
      }}
    >
      {pulsing && (
        <span
          style={{
            width: 6,
            height: 6,
            borderRadius: "50%",
            background: meta.color,
            animation: "pulseDot 1.4s infinite",
          }}
        />
      )}
      {meta.label}
    </span>
  );
}
