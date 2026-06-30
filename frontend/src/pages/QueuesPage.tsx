import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Icon, queueTypeIcon } from "../components/Icon";
import { StatusChip } from "../components/StatusChip";
import { CreateQueueModal, type CreateQueuePrefill } from "../components/CreateQueueModal";
import { useAuth } from "../hooks/useAuth";
import { queuesApi, scheduleApi } from "../api";
import { localQueues } from "../data/localStore";
import { PRACTICE_DEFENSE_PREFILL } from "../data/constants";
import { ROUTES } from "../routes";
import { colors } from "../theme";
import type { Queue, QueueStatus } from "../types";

/**
 * Список очередей — [FE-06], [FE-P2].
 * Фильтры по статусу, карточки очередей, создание (для преподавателя),
 * быстрое создание очереди на защиту практики 06.07 ([FE-P2]).
 */

type Filter = "all" | QueueStatus;
const FILTERS: { key: Filter; label: string }[] = [
  { key: "all", label: "Все" },
  { key: "live", label: "Идут сейчас" },
  { key: "open", label: "Открытые" },
  { key: "closed", label: "Закрытые" },
];

export default function QueuesPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [queues, setQueues] = useState<Queue[]>(localQueues.list());
  const [filter, setFilter] = useState<Filter>("all");
  const [creating, setCreating] = useState(false);
  const [prefill, setPrefill] = useState<CreateQueuePrefill | undefined>(undefined);
  const [pdBusy, setPdBusy] = useState(false);

  const addAndOpen = (q: Queue) => {
    localQueues.add(q);
    setQueues((list) => [q, ...list]);
    navigate(ROUTES.queueDetail(q.id));
  };

  /** [FE-P2] Очередь на защиту практики: профильный эндпоинт, иначе форма с предзаполнением. */
  const createPracticeDefense = async () => {
    setPdBusy(true);
    try {
      const q = (await scheduleApi.createPracticeDefenseQueue()) as Queue;
      addAndOpen(q);
    } catch {
      // backend не готов — открываем форму с предзаполненными полями события 06.07.
      setPrefill(PRACTICE_DEFENSE_PREFILL);
      setCreating(true);
    } finally {
      setPdBusy(false);
    }
  };

  const closeModal = () => {
    setCreating(false);
    setPrefill(undefined);
  };

  useEffect(() => {
    let alive = true;
    queuesApi
      .list()
      .then((q) => alive && setQueues(q))
      .catch(() => {/* демо-данные */});
    return () => {
      alive = false;
    };
  }, []);

  const isTeacher = user?.role === "teacher";
  const filtered = filter === "all" ? queues : queues.filter((q) => q.status === filter);

  return (
    <div style={{ animation: "fadeUp .3s both" }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-.5px", margin: "0 0 16px" }}>Очереди</h1>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
          {FILTERS.map((f) => {
            const on = filter === f.key;
            return (
              <button
                key={f.key}
                onClick={() => setFilter(f.key)}
                style={{ background: on ? colors.primary : colors.surface, color: on ? "#fff" : colors.textSoft, border: `1px solid ${on ? colors.primary : colors.border}`, borderRadius: 999, padding: "8px 15px", fontSize: 13, fontWeight: 500, cursor: "pointer" }}
              >
                {f.label}
              </button>
            );
          })}
        </div>
        {isTeacher && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            <button
              onClick={createPracticeDefense}
              disabled={pdBusy}
              title="Очередь на защиту учебной практики 06.07"
              style={{ background: colors.surface, color: colors.primary, border: `1px solid ${colors.primary}`, borderRadius: 12, padding: "11px 18px", fontWeight: 600, fontSize: 14, cursor: pdBusy ? "default" : "pointer", opacity: pdBusy ? 0.6 : 1, display: "flex", alignItems: "center", gap: 7 }}
            >
              <Icon name="defense" size={16} />
              {pdBusy ? "Создаём…" : "Защита практики"}
            </button>
            <button
              onClick={() => setCreating(true)}
              style={{ background: colors.primary, color: "#fff", border: "none", borderRadius: 12, padding: "11px 18px", fontWeight: 600, fontSize: 14, cursor: "pointer", display: "flex", alignItems: "center", gap: 7 }}
            >
              <Icon name="plus" size={16} />
              Создать очередь
            </button>
          </div>
        )}
      </div>

      {filtered.length > 0 ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(280px,1fr))", gap: 13 }}>
          {filtered.map((q) => (
            <div
              key={q.id}
              onClick={() => navigate(ROUTES.queueDetail(q.id))}
              style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 16, padding: 17, cursor: "pointer", display: "flex", flexDirection: "column" }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8, marginBottom: 12 }}>
                <div style={{ width: 40, height: 40, borderRadius: 11, background: colors.primarySoft, color: colors.primary, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Icon name={queueTypeIcon(q.qtype)} size={20} />
                </div>
                <StatusChip status={q.status} />
              </div>
              <div style={{ fontWeight: 700, fontSize: 16, letterSpacing: "-.2px" }}>{q.title}</div>
              <div style={{ fontSize: 13, color: colors.textMuted, marginTop: 2 }}>
                {q.discipline} · {q.qtype}
              </div>
              <div style={{ borderTop: `1px solid ${colors.borderMuted}`, marginTop: 13, paddingTop: 12, display: "flex", flexDirection: "column", gap: 7, fontSize: 13, color: colors.textSoft }}>
                <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <Icon name="user" size={15} />
                  {q.teacher}
                </span>
                <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <Icon name="pin" size={15} />
                  {q.room} · {q.group}
                </span>
                <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <Icon name="cal" size={15} />
                  {q.when}
                </span>
              </div>
              <div style={{ marginTop: 13, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, fontWeight: 600 }}>
                  <Icon name="users" size={15} />
                  {q.students.length} / {q.max}
                </span>
                <span style={{ fontSize: 13, color: colors.primary, fontWeight: 600 }}>Открыть →</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ background: colors.surface, border: `1px dashed ${colors.border}`, borderRadius: 16, padding: 42, textAlign: "center", color: colors.textMuted }}>
          Нет очередей с выбранными фильтрами
        </div>
      )}

      {creating && (
        <CreateQueueModal
          teacherName={user?.name ?? "Преподаватель"}
          prefill={prefill}
          onClose={closeModal}
          onCreated={(q) => {
            closeModal();
            addAndOpen(q);
          }}
        />
      )}
    </div>
  );
}
