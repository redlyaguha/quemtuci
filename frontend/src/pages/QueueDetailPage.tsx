import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Icon, queueTypeIcon } from "../components/Icon";
import { StatusChip } from "../components/StatusChip";
import { Toast } from "../components/Toast";
import { useAuth } from "../hooks/useAuth";
import { queuesApi } from "../api";
import { localQueues } from "../data/localStore";
import { ROUTES } from "../routes";
import { colors } from "../theme";
import type { Queue, QueueMember } from "../types";

/**
 * Детали очереди — [FE-06].
 * Студент: запись/выход и своя позиция. Преподаватель: порядок студентов
 * (вверх/вниз), удаление, закрытие очереди.
 *
 * Мутации идут через API; пока backend ([BE-Q3]/[BE-Q4]) не готов, состояние
 * обновляется оптимистично локально, чтобы поток был проверяем.
 */
export default function QueueDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [queue, setQueue] = useState<Queue | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    if (id === undefined) return;
    let alive = true;
    const fallback = () => {
      const local = localQueues.get(id);
      if (!alive) return;
      if (local) setQueue(local);
      else setNotFound(true);
    };
    queuesApi
      .get(id)
      .then((q) => alive && setQueue(q))
      .catch(fallback);
    return () => {
      alive = false;
    };
  }, [id]);

  if (notFound) {
    return (
      <div style={{ maxWidth: 780 }}>
        <BackButton onClick={() => navigate(ROUTES.queues)} />
        <div style={{ background: colors.surface, border: `1px dashed ${colors.border}`, borderRadius: 16, padding: 42, textAlign: "center", color: colors.textMuted }}>
          Очередь не найдена
        </div>
      </div>
    );
  }
  if (!queue) {
    return <div style={{ color: colors.textMuted, padding: "20px 0" }}>Загрузка…</div>;
  }

  const myIndex = queue.students.findIndex((s) => s.me);
  const myPos = myIndex >= 0 ? myIndex + 1 : null;
  const isStudent = user?.role === "student";
  const isTeacher = user?.role === "teacher";
  const canManage = isTeacher && queue.status !== "closed";
  const canJoin = isStudent && myPos === null && queue.status !== "closed";

  /** Оптимистичное обновление + фоновый вызов API (ошибки backend игнорируем). */
  const mutate = (next: Queue, apiCall: () => Promise<unknown>, message?: string) => {
    setQueue(next);
    localQueues.update(next); // согласованность при возврате к списку в демо-режиме
    if (message) setToast(message);
    apiCall().catch(() => {/* backend не готов — локального обновления достаточно */});
  };

  const join = () => {
    const me: QueueMember = { id: `me-${Date.now()}`, name: user?.name ?? "Вы", me: true };
    mutate({ ...queue, students: [...queue.students, me] }, () => queuesApi.join(queue.id), "Вы записались в очередь");
  };

  const leave = () => {
    mutate({ ...queue, students: queue.students.filter((s) => !s.me) }, () => queuesApi.leave(queue.id), "Вы вышли из очереди");
  };

  const move = (index: number, dir: -1 | 1) => {
    const j = index + dir;
    if (j < 0 || j >= queue.students.length) return;
    const students = [...queue.students];
    [students[index], students[j]] = [students[j], students[index]];
    mutate({ ...queue, students }, () => queuesApi.reorder(queue.id, students.map((s) => s.id)));
  };

  const removeMember = (member: QueueMember) => {
    mutate({ ...queue, students: queue.students.filter((s) => s.id !== member.id) }, () => queuesApi.removeMember(queue.id, member.id));
  };

  const close = () => {
    mutate({ ...queue, status: "closed" }, () => queuesApi.close(queue.id), "Очередь закрыта");
  };

  return (
    <div style={{ animation: "fadeUp .3s both", maxWidth: 780 }}>
      <BackButton onClick={() => navigate(ROUTES.queues)} />

      {/* Шапка */}
      <div style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 18, padding: 22, marginBottom: 16 }}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 12, justifyContent: "space-between", alignItems: "flex-start" }}>
          <div style={{ display: "flex", gap: 14, alignItems: "center" }}>
            <div style={{ width: 52, height: 52, borderRadius: 14, background: colors.primarySoft, color: colors.primary, display: "flex", alignItems: "center", justifyContent: "center", flex: "0 0 auto" }}>
              <Icon name={queueTypeIcon(queue.qtype)} size={24} />
            </div>
            <div>
              <h2 style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-.5px", margin: 0 }}>{queue.title}</h2>
              <div style={{ fontSize: 13.5, color: colors.textMuted, marginTop: 3 }}>
                {queue.discipline} · {queue.qtype}
              </div>
            </div>
          </div>
          <StatusChip status={queue.status} />
        </div>

        <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 18 }}>
          <InfoCell label="Преподаватель" value={queue.teacher} />
          <InfoCell label="Аудитория" value={queue.room} />
          <InfoCell label="Группа" value={queue.group} />
          <InfoCell label="Дата и время" value={queue.when} />
        </div>

        {queue.comment && (
          <div style={{ marginTop: 12, fontSize: 13.5, color: colors.textSoft, background: "#FBF8FF", border: "1px solid #EEE7FB", borderRadius: 12, padding: "12px 14px", lineHeight: 1.5 }}>
            💬 {queue.comment}
          </div>
        )}

        {/* Действия студента */}
        {isStudent && myPos !== null && (
          <div style={{ marginTop: 16, display: "flex", flexWrap: "wrap", gap: 10, alignItems: "center", background: colors.successSoft, border: "1px solid #CDEFD9", borderRadius: 14, padding: "14px 16px" }}>
            <div style={{ width: 46, height: 46, borderRadius: "50%", background: colors.success, color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 18 }}>{myPos}</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600, fontSize: 14.5, color: "#15803D" }}>Вы в очереди</div>
              <div style={{ fontSize: 12.5, color: "#3E8B5C" }}>Ваша позиция: {myPos} из {queue.students.length}</div>
            </div>
            <button onClick={leave} style={{ background: "#fff", border: "1px solid #CDEFD9", color: colors.danger, borderRadius: 11, padding: "10px 16px", fontWeight: 600, fontSize: 13.5, cursor: "pointer" }}>
              Выйти из очереди
            </button>
          </div>
        )}
        {canJoin && (
          <button onClick={join} style={{ marginTop: 16, width: "100%", background: colors.primary, color: "#fff", border: "none", borderRadius: 13, padding: 14, fontWeight: 600, fontSize: 15, cursor: "pointer" }}>
            Встать в очередь
          </button>
        )}
      </div>

      {/* Список студентов */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 11 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, margin: 0 }}>Список студентов · {queue.students.length}</h3>
        {canManage && (
          <button onClick={close} style={{ background: colors.dangerSoft, color: colors.danger, border: "none", borderRadius: 10, padding: "8px 14px", fontSize: 13, fontWeight: 600, cursor: "pointer" }}>
            Закрыть очередь
          </button>
        )}
      </div>

      <div style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 16, overflow: "hidden" }}>
        {queue.students.length === 0 ? (
          <div style={{ padding: 34, textAlign: "center", color: colors.textFaint, fontSize: 13.5 }}>Пока никто не записался в очередь</div>
        ) : (
          queue.students.map((s, i) => (
            <div
              key={s.id}
              style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 15px", borderBottom: i < queue.students.length - 1 ? `1px solid ${colors.borderMuted}` : "none", background: s.me ? "#F7FBF8" : colors.surface }}
            >
              <div style={{ width: 30, height: 30, borderRadius: 9, background: s.me ? colors.success : colors.primarySoft, color: s.me ? "#fff" : colors.primary, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 13, flex: "0 0 auto" }}>{i + 1}</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 14, fontWeight: 500 }}>{s.name}</div>
                {s.me && <div style={{ fontSize: 11.5, color: colors.textFaint }}>это вы</div>}
              </div>
              {canManage && (
                <div style={{ display: "flex", gap: 4 }}>
                  <IconBtn name="arrowUp" title="Вверх" disabled={i === 0} onClick={() => move(i, -1)} />
                  <IconBtn name="arrowDown" title="Вниз" disabled={i === queue.students.length - 1} onClick={() => move(i, 1)} />
                  <IconBtn name="trash" title="Удалить" danger onClick={() => removeMember(s)} />
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </div>
  );
}

function BackButton({ onClick }: { onClick: () => void }) {
  return (
    <button onClick={onClick} style={{ background: "none", border: "none", color: colors.textMuted, fontSize: 13.5, cursor: "pointer", display: "flex", alignItems: "center", gap: 5, marginBottom: 14 }}>
      ← Назад к очередям
    </button>
  );
}

function InfoCell({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ flex: "1 1 130px", background: colors.surfaceMuted, border: `1px solid ${colors.borderMuted}`, borderRadius: 12, padding: "12px 14px" }}>
      <div style={{ fontSize: 11.5, color: colors.textFaint, marginBottom: 3 }}>{label}</div>
      <div style={{ fontSize: 14, fontWeight: 600 }}>{value}</div>
    </div>
  );
}

function IconBtn({ name, title, onClick, disabled, danger }: { name: "arrowUp" | "arrowDown" | "trash"; title: string; onClick: () => void; disabled?: boolean; danger?: boolean }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      style={{
        background: "none",
        border: `1px solid ${colors.border}`,
        color: disabled ? "#D5D7E2" : danger ? "#C7575C" : colors.textSoft,
        width: 32,
        height: 32,
        borderRadius: 9,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        cursor: disabled ? "default" : "pointer",
      }}
    >
      <Icon name={name} size={16} />
    </button>
  );
}
