import { createPortal } from "react-dom";
import type { ReactNode } from "react";
import { colors, font } from "../theme";

/**
 * Подтверждающий диалог (через портал в body). Используется для защиты от
 * мисклика — закрытие очереди, отметка «сдал» и т.п. `children` — доп. контент
 * (например, выбор оценки) между текстом и кнопками.
 */
export function ConfirmDialog({
  title,
  message,
  confirmLabel = "Подтвердить",
  cancelLabel = "Отмена",
  danger = false,
  confirmDisabled = false,
  onConfirm,
  onCancel,
  children,
}: {
  title: string;
  message?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean;
  confirmDisabled?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  children?: ReactNode;
}) {
  return createPortal(
    <div
      onClick={onCancel}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(20,22,40,.45)",
        backdropFilter: "blur(3px)",
        zIndex: 85,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
        animation: "fadeUp .2s both",
        fontFamily: font.family,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{ background: colors.surface, borderRadius: 18, width: "100%", maxWidth: 420, padding: 22, boxShadow: "0 30px 70px -20px rgba(20,22,40,.5)" }}
      >
        <h3 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 8px", color: colors.text }}>{title}</h3>
        {message && <p style={{ fontSize: 14, color: colors.textSoft, margin: 0, lineHeight: 1.5 }}>{message}</p>}
        {children}
        <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 20 }}>
          <button
            onClick={onCancel}
            style={{ background: colors.surfaceMuted, border: "none", borderRadius: 11, padding: "10px 18px", fontWeight: 600, fontSize: 14, cursor: "pointer", color: colors.textSoft }}
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            disabled={confirmDisabled}
            style={{
              background: danger ? colors.danger : colors.primary,
              color: "#fff",
              border: "none",
              borderRadius: 11,
              padding: "10px 18px",
              fontWeight: 600,
              fontSize: 14,
              cursor: confirmDisabled ? "default" : "pointer",
              opacity: confirmDisabled ? 0.6 : 1,
            }}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
