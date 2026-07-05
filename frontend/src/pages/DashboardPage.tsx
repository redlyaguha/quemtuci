import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Icon, queueTypeIcon } from "../components/Icon";
import { formatWhen } from "../format";
import { StatCard } from "../components/StatCard";
import { StatusChip } from "../components/StatusChip";
import { DocBadge } from "../components/DocBadge";
import { useAuth } from "../hooks/useAuth";
import { useApiData } from "../hooks/useApiData";
import { queuesApi, documentsApi } from "../api";
import { MOCK_QUEUES, MOCK_DOCUMENTS, SEARCH_HISTORY_SEED } from "../data/mock";
import { ROUTES } from "../routes";
import { colors, roleMeta } from "../theme";
import type { Queue, DocumentItem } from "../types";

/**
 * Дашборд под текущую роль — [FE-05].
 * Данные тянутся из API (очереди, документы) с фолбэком на демо-данные,
 * пока соответствующие backend-эндпоинты не реализованы.
 */
export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const fetchQueues = useCallback(() => queuesApi.list(), []);
  const fetchDocs = useCallback(() => documentsApi.list(), []);
  const { data: queues } = useApiData<Queue[]>(fetchQueues, MOCK_QUEUES);
  const { data: docs } = useApiData<DocumentItem[]>(fetchDocs, MOCK_DOCUMENTS);

  const [query, setQuery] = useState("");
  const runSearch = (q?: string) => {
    const value = (q ?? query).trim();
    if (!value) return;
    navigate(`${ROUTES.knowledge}?q=${encodeURIComponent(value)}`);
  };

  if (!user) return null;
  const role = user.role;
  const rm = roleMeta[role];

  return (
    <div style={{ animation: "fadeUp .35s both" }}>
      <header style={{ marginBottom: 18 }}>
        <div style={{ fontSize: 12, color: colors.textFaint, fontWeight: 500 }}>{rm.label} · Кампус</div>
        <h1 style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-.5px", margin: "2px 0 0" }}>
          Здравствуйте, {user.name.split(" ")[0]}
        </h1>
      </header>

      {role === "student" && (
        <StudentDashboard
          user={user}
          queues={queues}
          docs={docs}
          query={query}
          setQuery={setQuery}
          runSearch={runSearch}
          openQueue={(id) => navigate(ROUTES.queueDetail(id))}
          goKnowledge={() => navigate(ROUTES.knowledge)}
          goQueues={() => navigate(ROUTES.queues)}
        />
      )}

      {role === "teacher" && (
        <TeacherDashboard
          queues={queues}
          query={query}
          setQuery={setQuery}
          runSearch={runSearch}
          openQueue={(id) => navigate(ROUTES.queueDetail(id))}
          goQueues={() => navigate(ROUTES.queues)}
        />
      )}

      {role === "admin" && <AdminDashboard docs={docs} queues={queues} />}
    </div>
  );
}

/* ----------------------------- общие куски ----------------------------- */

const twoCol: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "minmax(0,1.5fr) minmax(0,1fr)",
  gap: 16,
};

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <h3 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 10px" }}>{children}</h3>;
}

function QuickSearch({
  query,
  setQuery,
  runSearch,
}: {
  query: string;
  setQuery: (v: string) => void;
  runSearch: (q?: string) => void;
}) {
  return (
    <div style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 16, padding: 16 }}>
      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && runSearch()}
          placeholder="Например: оформление лабораторных"
          style={{
            flex: 1,
            minWidth: 0,
            border: `1px solid ${colors.border}`,
            borderRadius: 11,
            padding: "11px 13px",
            fontSize: 14,
            background: colors.surfaceMuted,
          }}
        />
        <button
          onClick={() => runSearch()}
          style={{
            background: colors.primary,
            color: "#fff",
            border: "none",
            borderRadius: 11,
            padding: "0 16px",
            fontWeight: 600,
            fontSize: 14,
            cursor: "pointer",
          }}
        >
          Найти
        </button>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 12 }}>
        {SEARCH_HISTORY_SEED.map((h) => (
          <button
            key={h}
            onClick={() => runSearch(h)}
            style={{
              background: colors.surfaceMuted,
              border: `1px solid ${colors.borderMuted}`,
              borderRadius: 999,
              padding: "5px 11px",
              fontSize: 12.5,
              color: colors.textSoft,
              cursor: "pointer",
            }}
          >
            {h}
          </button>
        ))}
      </div>
    </div>
  );
}

function QueueRow({ q, onOpen, currentUserId }: { q: Queue; onOpen: () => void; currentUserId: string | number }) {
  const myPos = q.students.findIndex((s) => s.userId === currentUserId) + 1 || null;
  return (
    <div
      onClick={onOpen}
      style={{
        background: colors.surface,
        border: `1px solid ${colors.border}`,
        borderRadius: 16,
        padding: 16,
        cursor: "pointer",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 10 }}>
        <div style={{ display: "flex", gap: 11, alignItems: "center" }}>
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: 11,
              background: colors.primarySoft,
              color: colors.primary,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flex: "0 0 auto",
            }}
          >
            <Icon name={queueTypeIcon(q.qtype)} size={20} />
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 15 }}>{q.title}</div>
            <div style={{ fontSize: 12.5, color: colors.textMuted, marginTop: 1 }}>
              {q.teacher} · {q.discipline}
            </div>
          </div>
        </div>
        <StatusChip status={q.status} />
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 14, marginTop: 13, fontSize: 12.5, color: colors.textSoft }}>
        <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
          <Icon name="pin" size={15} />
          {q.room}
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
          <Icon name="cal" size={15} />
          {formatWhen(q.when)}
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
          <Icon name="users" size={15} />
          {q.students.length} чел.
        </span>
      </div>
      {myPos && (
        <div
          style={{
            marginTop: 12,
            padding: "9px 12px",
            background: colors.successSoft,
            borderRadius: 10,
            color: "#15803D",
            fontSize: 13,
            fontWeight: 600,
            display: "flex",
            alignItems: "center",
            gap: 7,
          }}
        >
          <Icon name="check" size={16} />
          Вы в очереди · позиция {myPos}
        </div>
      )}
    </div>
  );
}

/* ----------------------------- студент ----------------------------- */

function StudentDashboard({
  user,
  queues,
  docs,
  query,
  setQuery,
  runSearch,
  openQueue,
  goKnowledge,
  goQueues,
}: {
  user: { id: string | number; group?: string | null };
  queues: Queue[];
  docs: DocumentItem[];
  query: string;
  setQuery: (v: string) => void;
  runSearch: (q?: string) => void;
  openQueue: (id: string | number) => void;
  goKnowledge: () => void;
  goQueues: () => void;
}) {
  const myQueues = queues.filter((q) => !user.group || q.group === user.group);
  const activeCount = myQueues.filter((q) => q.status !== "closed").length;
  const liveCount = myQueues.filter((q) => q.status === "live").length;

  return (
    <>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "flex-start", marginBottom: 18 }}>
        <div
          style={{
            flex: "1 1 200px",
            minHeight: 120,
            background: "linear-gradient(145deg,#4F46E5,#7C4DFF)",
            color: "#fff",
            borderRadius: 18,
            padding: 18,
            display: "flex",
            flexDirection: "column",
            gap: 6,
          }}
        >
          <div style={{ fontSize: 13, opacity: 0.82, fontWeight: 500 }}>Моя группа</div>
          <div style={{ fontSize: 30, fontWeight: 800, letterSpacing: "-.6px" }}>{user.group ?? "—"}</div>
          <div style={{ fontSize: 13, opacity: 0.82, marginTop: "auto" }}>Программная инженерия · 2 курс</div>
        </div>
        <StatCard label="Активные очереди" value={activeCount} hint={liveCount ? `${liveCount} идёт сейчас` : undefined} hintColor={colors.success} />
        <StatCard label="Ближайшее занятие" value={<span style={{ fontSize: 20 }}>12:20 · А-402</span>} hint="Программная инженерия" />
      </div>

      <div style={twoCol}>
        <div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
            <SectionTitle>Активные очереди для вашей группы</SectionTitle>
            <button onClick={goQueues} style={linkBtn}>
              Все →
            </button>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {myQueues.length ? (
              myQueues.map((q) => <QueueRow key={q.id} q={q} currentUserId={user.id} onOpen={() => openQueue(q.id)} />)
            ) : (
              <EmptyHint>Для вашей группы пока нет очередей</EmptyHint>
            )}
          </div>
        </div>
        <div>
          <SectionTitle>Быстрый поиск по базе</SectionTitle>
          <div style={{ marginBottom: 16 }}>
            <QuickSearch query={query} setQuery={setQuery} runSearch={runSearch} />
          </div>
          <SectionTitle>Последние документы</SectionTitle>
          <div style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 16, overflow: "hidden" }}>
            {docs.slice(0, 4).map((d) => (
              <div
                key={d.id}
                onClick={goKnowledge}
                style={{ display: "flex", alignItems: "center", gap: 11, padding: "12px 14px", borderBottom: `1px solid ${colors.borderMuted}`, cursor: "pointer" }}
              >
                <DocBadge type={d.type} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13.5, fontWeight: 500, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{d.name}</div>
                  <div style={{ fontSize: 11.5, color: colors.textFaint }}>
                    {d.frags ? `${d.frags} фрагментов` : "не проиндексирован"}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

/* ----------------------------- преподаватель ----------------------------- */

const LESSONS = [
  { time: "12:20", room: "А-402", discipline: "Программная инженерия", group: "БПИ2403", kind: "Лабораторная" },
  { time: "14:00", room: "Б-215", discipline: "Базы данных", group: "БВТ2401", kind: "Лекция" },
];

function TeacherDashboard({
  queues,
  query,
  setQuery,
  runSearch,
  openQueue,
  goQueues,
}: {
  queues: Queue[];
  query: string;
  setQuery: (v: string) => void;
  runSearch: (q?: string) => void;
  openQueue: (id: string | number) => void;
  goQueues: () => void;
}) {
  const active = queues.filter((q) => q.status !== "closed");
  const studentsCount = active.reduce((acc, q) => acc + q.students.length, 0);

  return (
    <>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginBottom: 18 }}>
        <StatCard label="Мои активные очереди" value={active.length} />
        <StatCard label="Студентов записано" value={studentsCount} />
        <StatCard label="Пар сегодня" value={LESSONS.length} />
      </div>

      <div style={twoCol}>
        <div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
            <SectionTitle>Ближайшие пары</SectionTitle>
            <button onClick={goQueues} style={linkBtn}>
              + Создать вручную
            </button>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {LESSONS.map((l) => (
              <div
                key={l.time}
                style={{
                  background: colors.surface,
                  border: `1px solid ${colors.border}`,
                  borderRadius: 16,
                  padding: 16,
                  display: "flex",
                  flexWrap: "wrap",
                  gap: 12,
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <div style={{ display: "flex", gap: 13, alignItems: "center" }}>
                  <div style={{ textAlign: "center", background: colors.primarySoft, borderRadius: 12, padding: "9px 12px", minWidth: 62 }}>
                    <div style={{ fontSize: 17, fontWeight: 700, color: colors.primary }}>{l.time}</div>
                    <div style={{ fontSize: 11, color: "#7C7FE0" }}>{l.room}</div>
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 15 }}>{l.discipline}</div>
                    <div style={{ fontSize: 12.5, color: colors.textMuted, marginTop: 1 }}>
                      {l.group} · {l.kind}
                    </div>
                  </div>
                </div>
                <button onClick={goQueues} style={{ ...primaryBtn, display: "flex", alignItems: "center", gap: 6 }}>
                  <Icon name="plus" size={16} />
                  Создать очередь
                </button>
              </div>
            ))}
          </div>

          <SectionTitle>
            <span style={{ display: "block", marginTop: 22 }}>Мои активные очереди</span>
          </SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {active.slice(0, 3).map((q) => (
              <div
                key={q.id}
                onClick={() => openQueue(q.id)}
                style={{
                  background: colors.surface,
                  border: `1px solid ${colors.border}`,
                  borderRadius: 16,
                  padding: "15px 16px",
                  cursor: "pointer",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 10,
                }}
              >
                <div style={{ display: "flex", gap: 11, alignItems: "center" }}>
                  <div style={{ width: 40, height: 40, borderRadius: 11, background: colors.primarySoft, color: colors.primary, display: "flex", alignItems: "center", justifyContent: "center", flex: "0 0 auto" }}>
                    <Icon name={queueTypeIcon(q.qtype)} size={20} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 14.5 }}>{q.title}</div>
                    <div style={{ fontSize: 12, color: colors.textMuted }}>
                      {q.group} · {q.room} · {q.students.length} чел.
                    </div>
                  </div>
                </div>
                <StatusChip status={q.status} />
              </div>
            ))}
          </div>
        </div>

        <div>
          <SectionTitle>Быстрый поиск по базе</SectionTitle>
          <QuickSearch query={query} setQuery={setQuery} runSearch={runSearch} />
          <div style={{ background: "linear-gradient(150deg,#4F46E5,#7C4DFF)", color: "#fff", borderRadius: 16, padding: 18, marginTop: 16 }}>
            <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 4 }}>Нужна новая очередь?</div>
            <div style={{ fontSize: 13, opacity: 0.85, lineHeight: 1.5, marginBottom: 13 }}>
              Создайте очередь вручную, указав дисциплину, аудиторию и время.
            </div>
            <button onClick={goQueues} style={{ background: "#fff", color: colors.primary, border: "none", borderRadius: 11, padding: "10px 16px", fontWeight: 600, fontSize: 13.5, cursor: "pointer" }}>
              Создать вручную
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

/* ----------------------------- администратор ----------------------------- */

function AdminDashboard({ docs, queues }: { docs: DocumentItem[]; queues: Queue[] }) {
  const totalFrags = docs.reduce((acc, d) => acc + (d.frags ?? 0), 0);
  const errors = docs.filter((d) => d.status === "error");
  const activeQueues = queues.filter((q) => q.status !== "closed").length;

  const chart = [62, 88, 74, 95, 120, 80, 134];
  const days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];
  const maxV = Math.max(...chart);

  return (
    <>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginBottom: 18 }}>
        <StatCard label="Документов в базе" value={docs.length} hint={`${totalFrags} фрагментов`} hintColor={colors.success} />
        <StatCard label="Поисковых запросов" value="1 248" hint="за 30 дней" />
        <StatCard label="Активные очереди" value={activeQueues} />
        <StatCard label="Ошибки индексации" value={<span style={{ color: errors.length ? colors.danger : undefined }}>{errors.length}</span>} />
      </div>

      <div style={twoCol}>
        <div>
          <SectionTitle>Последние загруженные файлы</SectionTitle>
          <div style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 16, overflow: "hidden" }}>
            {docs.map((d) => (
              <div key={d.id} style={{ display: "flex", alignItems: "center", gap: 12, padding: "13px 15px", borderBottom: `1px solid ${colors.borderMuted}` }}>
                <DocBadge type={d.type} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13.5, fontWeight: 500, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{d.name}</div>
                  <div style={{ fontSize: 11.5, color: colors.textFaint }}>
                    {d.date ? formatWhen(d.date) : "—"} · {d.size}
                  </div>
                </div>
                <StatusChip status={d.status} />
              </div>
            ))}
          </div>
        </div>

        <div>
          {errors.length > 0 && (
            <>
              <SectionTitle>Ошибки индексации</SectionTitle>
              <div style={{ background: colors.surface, border: "1px solid #F4D6D8", borderRadius: 16, padding: 16 }}>
                {errors.map((d) => (
                  <div key={d.id} style={{ display: "flex", gap: 11, alignItems: "flex-start" }}>
                    <div style={{ width: 34, height: 34, borderRadius: 10, background: colors.dangerSoft, color: colors.danger, display: "flex", alignItems: "center", justifyContent: "center", flex: "0 0 auto" }}>
                      <Icon name="alert" size={18} />
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 14 }}>{d.name}</div>
                      <div style={{ fontSize: 12.5, color: colors.textMuted, marginTop: 3, lineHeight: 1.5 }}>
                        Не удалось извлечь текст из части документа. Проиндексирован частично.
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          <SectionTitle>
            <span style={{ display: "block", marginTop: errors.length ? 20 : 0 }}>Запросы за неделю</span>
          </SectionTitle>
          <div style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 16, padding: "18px 16px" }}>
            <div style={{ display: "flex", alignItems: "flex-end", gap: 8, height: 110 }}>
              {chart.map((val, i) => (
                <div key={days[i]} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 6, justifyContent: "flex-end", height: "100%" }}>
                  <div
                    style={{
                      width: "100%",
                      height: Math.round((val / maxV) * 88),
                      borderRadius: "6px 6px 3px 3px",
                      background: i === chart.length - 1 ? "linear-gradient(#7C4DFF,#4F46E5)" : "#E2E0FB",
                    }}
                  />
                  <div style={{ fontSize: 11, color: colors.textFaint }}>{days[i]}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

/* ----------------------------- мелочи ----------------------------- */

const linkBtn: React.CSSProperties = {
  background: "none",
  border: "none",
  color: colors.primary,
  fontWeight: 600,
  fontSize: 13,
  cursor: "pointer",
};

const primaryBtn: React.CSSProperties = {
  background: colors.primary,
  color: "#fff",
  border: "none",
  borderRadius: 11,
  padding: "10px 16px",
  fontWeight: 600,
  fontSize: 13.5,
  cursor: "pointer",
};

function EmptyHint({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ background: colors.surface, border: `1px dashed ${colors.border}`, borderRadius: 16, padding: 28, textAlign: "center", color: colors.textFaint, fontSize: 13.5 }}>
      {children}
    </div>
  );
}
