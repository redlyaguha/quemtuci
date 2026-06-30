import { useEffect } from "react";
import { Icon } from "./Icon";

/** Тост-уведомление снизу по центру. Автоскрытие через `duration` мс. */
export function Toast({
  message,
  onClose,
  duration = 2600,
}: {
  message: string;
  onClose: () => void;
  duration?: number;
}) {
  useEffect(() => {
    const t = setTimeout(onClose, duration);
    return () => clearTimeout(t);
  }, [message, duration, onClose]);

  return (
    <div
      role="status"
      style={{
        position: "fixed",
        bottom: 24,
        left: "50%",
        transform: "translateX(-50%)",
        zIndex: 90,
        background: "#15161F",
        color: "#fff",
        padding: "13px 20px",
        borderRadius: 13,
        fontSize: 13.5,
        fontWeight: 500,
        boxShadow: "0 16px 40px -12px rgba(0,0,0,.4)",
        display: "flex",
        alignItems: "center",
        gap: 9,
        animation: "fadeUp .25s both",
      }}
    >
      <Icon name="check" size={16} />
      {message}
    </div>
  );
}
