import { useState } from "react";
import { createPortal } from "react-dom";
import { Icon } from "./Icon";
import { queuesApi } from "../api";
import { GROUPS, QUEUE_TYPES } from "../data/constants";
import { colors, font } from "../theme";
import type { Queue, QueueCreate, QueueType } from "../types";

/**
 * Модалка создания очереди (преподаватель). Пытается создать через API,
 * при недоступности backend собирает очередь локально, чтобы поток работал.
 * `prefill` позволяет открыть форму с предзаполненными полями (используется
 * в FE-P2 для очереди защиты практики).
 */

export interface CreateQueuePrefill extends Partial<QueueCreate> {}

const lblStyle: React.CSSProperties = { display: "block", fontSize: 12.5, fontWeight: 600, color: colors.textSoft, marginBottom: 6 };
const inputStyle: React.CSSProperties = {
  width: "100%",
  border: `1px solid ${colors.border}`,
  borderRadius: 11,
  padding: "11px 13px",
  fontSize: 14,
  background: colors.surfaceMuted,
  color: colors.text,
};

export function CreateQueueModal({
  prefill,
  teacherName,
  onClose,
  onCreated,
}: {
  prefill?: CreateQueuePrefill;
  teacherName: string;
  onClose: () => void;
  onCreated: (queue: Queue) => void;
}) {
  const [title, setTitle] = useState(prefill?.title ?? "");
  const [discipline, setDiscipline] = useState(prefill?.discipline ?? "");
  const [group, setGroup] = useState(prefill?.group ?? GROUPS[0]);
  const [room, setRoom] = useState(prefill?.room ?? "");
  const [when, setWhen] = useState(prefill?.when ?? "");
  const [qtype, setQtype] = useState<QueueType>(prefill?.qtype ?? "Лабораторная");
  const [max, setMax] = useState(String(prefill?.max ?? 15));
  const [comment, setComment] = useState(prefill?.comment ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    if (!title.trim()) {
      setError("Укажите название очереди");
      return;
    }
    setError(null);
    setBusy(true);
    const body: QueueCreate = {
      title: title.trim(),
      discipline: discipline.trim() || "—",
      qtype,
      group,
      room: room.trim() || "—",
      when: when.trim() || "не указано",
      max: parseInt(max, 10) || 15,
      comment: comment.trim() || undefined,
    };
    try {
      const created = await queuesApi.create(body);
      onCreated(created);
    } catch {
      // backend не готов — создаём локально.
      onCreated({
        id: Date.now(),
        ...body,
        teacher: teacherName,
        status: "open",
        students: [],
      });
    } finally {
      setBusy(false);
    }
  };

  return createPortal(
    <div
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(20,22,40,.45)",
        backdropFilter: "blur(3px)",
        zIndex: 80,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
        animation: "fadeUp .2s both",
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{ background: colors.surface, borderRadius: 20, width: "100%", maxWidth: 520, maxHeight: "90vh", overflow: "auto", fontFamily: font.family }}
      >
        <div style={{ padding: "20px 22px", borderBottom: `1px solid ${colors.borderMuted}`, display: "flex", justifyContent: "space-between", alignItems: "center", position: "sticky", top: 0, background: colors.surface }}>
          <h3 style={{ fontSize: 18, fontWeight: 700, margin: 0 }}>Создание очереди</h3>
          <button onClick={onClose} style={{ background: colors.surfaceMuted, border: "none", width: 34, height: 34, borderRadius: 10, cursor: "pointer", color: colors.textSoft, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Icon name="x" size={18} />
          </button>
        </div>

        <div style={{ padding: 22, display: "flex", flexDirection: "column", gap: 14 }}>
          {error && (
            <div style={{ padding: "10px 13px", background: colors.dangerSoft, border: "1px solid #F4D6D8", borderRadius: 11, color: colors.danger, fontSize: 13 }}>{error}</div>
          )}
          <div>
            <label style={lblStyle}>Название очереди</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Например: Защита лабораторной №4" style={inputStyle} />
          </div>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <div style={{ flex: "1 1 180px" }}>
              <label style={lblStyle}>Дисциплина</label>
              <input value={discipline} onChange={(e) => setDiscipline(e.target.value)} placeholder="Программная инженерия" style={inputStyle} />
            </div>
            <div style={{ flex: "1 1 120px" }}>
              <label style={lblStyle}>Группа</label>
              <select value={group} onChange={(e) => setGroup(e.target.value)} style={inputStyle}>
                {GROUPS.map((g) => (
                  <option key={g} value={g}>
                    {g}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <div style={{ flex: "1 1 120px" }}>
              <label style={lblStyle}>Аудитория</label>
              <input value={room} onChange={(e) => setRoom(e.target.value)} placeholder="А-402" style={inputStyle} />
            </div>
            <div style={{ flex: "1 1 160px" }}>
              <label style={lblStyle}>Дата и время</label>
              <input value={when} onChange={(e) => setWhen(e.target.value)} placeholder="06.07 · 12:20" style={inputStyle} />
            </div>
          </div>
          <div>
            <label style={lblStyle}>Тип очереди</label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
              {QUEUE_TYPES.map((t) => {
                const on = qtype === t;
                return (
                  <button
                    key={t}
                    onClick={() => setQtype(t)}
                    style={{ background: on ? colors.primary : colors.surface, color: on ? "#fff" : colors.textSoft, border: `1px solid ${on ? colors.primary : colors.border}`, borderRadius: 10, padding: "9px 14px", fontSize: 13, fontWeight: 500, cursor: "pointer" }}
                  >
                    {t}
                  </button>
                );
              })}
            </div>
          </div>
          <div>
            <label style={lblStyle}>Максимум студентов</label>
            <input value={max} onChange={(e) => setMax(e.target.value)} inputMode="numeric" placeholder="15" style={inputStyle} />
          </div>
          <div>
            <label style={lblStyle}>Комментарий преподавателя</label>
            <textarea value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Необязательно" style={{ ...inputStyle, minHeight: 70, resize: "vertical" }} />
          </div>
        </div>

        <div style={{ padding: "16px 22px", borderTop: `1px solid ${colors.borderMuted}`, display: "flex", gap: 10, justifyContent: "flex-end", position: "sticky", bottom: 0, background: colors.surface }}>
          <button onClick={onClose} style={{ background: colors.surfaceMuted, border: "none", borderRadius: 11, padding: "11px 18px", fontWeight: 600, fontSize: 14, cursor: "pointer", color: colors.textSoft }}>
            Отмена
          </button>
          <button onClick={submit} disabled={busy} style={{ background: colors.primary, color: "#fff", border: "none", borderRadius: 11, padding: "11px 20px", fontWeight: 600, fontSize: 14, cursor: busy ? "default" : "pointer", opacity: busy ? 0.6 : 1 }}>
            {busy ? "Создаём…" : "Создать очередь"}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
