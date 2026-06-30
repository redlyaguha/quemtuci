import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Icon } from "../components/Icon";
import { DocBadge } from "../components/DocBadge";
import { Highlight } from "../components/Highlight";
import { Toast } from "../components/Toast";
import { searchApi } from "../api";
import { MOCK_CORPUS, SEARCH_HISTORY_SEED } from "../data/mock";
import { localDocs } from "../data/localDocs";
import { colors } from "../theme";
import type { SearchResult, DocumentType, DocumentItem } from "../types";

/**
 * База знаний — полнотекстовый поиск по документам [FE-04].
 * Поиск по кнопке и Enter, карточки результатов с подсветкой запроса,
 * пагинация по 10, пустое состояние. Запрос можно передать через ?q=.
 *
 * Пока backend `/search` ([BE-S3]) не готов — поиск идёт по локальному
 * корпусу демо-данных; при готовности API используется он.
 */

const PAGE_SIZE = 10;
type Filter = "all" | "PDF" | "DOCX";

const FILTERS: { key: Filter; label: string }[] = [
  { key: "all", label: "Все" },
  { key: "PDF", label: "PDF" },
  { key: "DOCX", label: "DOCX" },
];

function localSearch(query: string): SearchResult[] {
  const tokens = query.toLowerCase().split(/\s+/).filter(Boolean);
  if (!tokens.length) return [];
  return MOCK_CORPUS.filter((c) => {
    const hay = `${c.text} ${c.doc}`.toLowerCase();
    return tokens.some((t) => hay.includes(t));
  }).sort((a, b) => b.rel - a.rel);
}

function relMeta(rel: number) {
  const pct = Math.round(rel * 100);
  const color = pct >= 90 ? colors.success : pct >= 75 ? colors.warning : colors.textMuted;
  return { pct, color };
}

export default function KnowledgeBasePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const [activeQuery, setActiveQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<Filter>("all");
  const [page, setPage] = useState(1);
  const [toast, setToast] = useState<string | null>(null);

  const openDoc = (d: DocumentItem) => {
    if (d.url) window.open(d.url, "_blank", "noopener");
    else setToast("Файл доступен после интеграции с хранилищем");
  };

  const runSearch = async (value: string) => {
    const q = value.trim();
    if (!q) return;
    setActiveQuery(q);
    setSearched(true);
    setPage(1);
    setLoading(true);
    try {
      const res = await searchApi.search(q);
      setResults(res.results);
    } catch {
      setResults(localSearch(q)); // backend не готов — локальный корпус
    } finally {
      setLoading(false);
    }
  };

  const submit = (value?: string) => {
    const q = (value ?? query).trim();
    if (!q) return;
    setQuery(q);
    setSearchParams(q ? { q } : {}, { replace: true });
    runSearch(q);
  };

  // Автозапуск поиска по ?q= (например, переход из дашборда).
  useEffect(() => {
    const q = searchParams.get("q");
    if (q && q !== activeQuery) {
      setQuery(q);
      runSearch(q);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const filtered = filter === "all" ? results : results.filter((r) => r.type === (filter as DocumentType));
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paged = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div style={{ animation: "fadeUp .3s both", maxWidth: 840 }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-.5px", margin: "0 0 14px" }}>
        База знаний
      </h1>

      {/* Поисковая строка */}
      <div style={{ display: "flex", gap: 8, marginBottom: 14 }}>
        <div
          style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            gap: 10,
            background: colors.surface,
            border: `1px solid ${colors.border}`,
            borderRadius: 14,
            padding: "0 14px",
          }}
        >
          <span style={{ color: colors.textFaint }}>
            <Icon name="search" size={17} />
          </span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit()}
            placeholder="Искать по содержанию документов…"
            style={{ flex: 1, border: "none", background: "none", padding: "14px 0", fontSize: 15 }}
          />
        </div>
        <button
          onClick={() => submit()}
          style={{ background: colors.primary, color: "#fff", border: "none", borderRadius: 14, padding: "0 24px", fontWeight: 600, fontSize: 15, cursor: "pointer" }}
        >
          Найти
        </button>
      </div>

      {/* Фильтры */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 7, alignItems: "center", marginBottom: 18 }}>
        <span style={{ fontSize: 12.5, color: colors.textFaint, marginRight: 2 }}>Фильтры:</span>
        {FILTERS.map((f) => {
          const on = filter === f.key;
          return (
            <button
              key={f.key}
              onClick={() => {
                setFilter(f.key);
                setPage(1);
              }}
              style={{
                background: on ? colors.primary : colors.surface,
                color: on ? "#fff" : colors.textSoft,
                border: `1px solid ${on ? colors.primary : colors.border}`,
                borderRadius: 999,
                padding: "8px 15px",
                fontSize: 13,
                fontWeight: 500,
                cursor: "pointer",
              }}
            >
              {f.label}
            </button>
          );
        })}
      </div>

      {/* История (до первого поиска) */}
      {!searched && (
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: colors.textSoft, marginBottom: 8 }}>История запросов</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
            {SEARCH_HISTORY_SEED.map((h) => (
              <button
                key={h}
                onClick={() => submit(h)}
                style={{ display: "flex", alignItems: "center", gap: 6, background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 999, padding: "7px 13px", fontSize: 13, color: colors.textSoft, cursor: "pointer" }}
              >
                <Icon name="clock" size={14} />
                {h}
              </button>
            ))}
          </div>

          {/* Документы базы знаний (включая загруженные) */}
          <div style={{ fontSize: 13, fontWeight: 600, color: colors.textSoft, margin: "20px 0 8px" }}>Документы базы знаний</div>
          <div style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 16, overflow: "hidden" }}>
            {localDocs.list().map((d, i, arr) => (
              <button
                key={d.id}
                onClick={() => openDoc(d)}
                style={{ display: "flex", alignItems: "center", gap: 11, padding: "12px 14px", borderBottom: i < arr.length - 1 ? `1px solid ${colors.borderMuted}` : "none", cursor: "pointer", background: "none", border: "none", width: "100%", textAlign: "left" }}
              >
                <DocBadge type={d.type} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13.5, fontWeight: 500, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{d.name}</div>
                  <div style={{ fontSize: 11.5, color: colors.textFaint }}>
                    {d.frags ? `${d.frags} фрагментов` : "не проиндексирован"}
                  </div>
                </div>
                <span style={{ fontSize: 12.5, color: colors.primary, fontWeight: 600, flex: "0 0 auto" }}>Открыть →</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Результаты */}
      {searched && !loading && filtered.length > 0 && (
        <div>
          <div style={{ fontSize: 13, color: colors.textMuted, marginBottom: 12 }}>
            Найдено {filtered.length} фрагментов по запросу «{activeQuery}»
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {paged.map((r, i) => {
              const rel = relMeta(r.rel);
              return (
                <div key={`${r.doc}-${r.page}-${i}`} style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 16, padding: 18 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, marginBottom: 9 }}>
                    <div style={{ display: "flex", gap: 10, alignItems: "center", minWidth: 0 }}>
                      <DocBadge type={r.type} />
                      <div style={{ minWidth: 0 }}>
                        <div style={{ fontWeight: 600, fontSize: 14.5, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{r.doc}</div>
                        <div style={{ fontSize: 12, color: colors.textFaint }}>Страница {r.page}</div>
                      </div>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 6, flex: "0 0 auto" }}>
                      <div style={{ width: 7, height: 7, borderRadius: "50%", background: rel.color }} />
                      <span style={{ fontSize: 12.5, fontWeight: 600, color: rel.color }}>{rel.pct}%</span>
                    </div>
                  </div>
                  <div style={{ fontSize: 14, lineHeight: 1.62, color: "#3A3C4A" }}>
                    <Highlight text={r.text} query={activeQuery} />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Пагинация */}
          {totalPages > 1 && (
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 6, marginTop: 22 }}>
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: 10,
                    border: `1px solid ${page === p ? colors.primary : colors.border}`,
                    background: page === p ? colors.primary : colors.surface,
                    color: page === p ? "#fff" : colors.textSoft,
                    fontWeight: 600,
                    fontSize: 13,
                    cursor: "pointer",
                  }}
                >
                  {p}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Пустое состояние */}
      {searched && !loading && filtered.length === 0 && (
        <div style={{ background: colors.surface, border: `1px dashed #D7DAE6`, borderRadius: 18, padding: "54px 30px", textAlign: "center", animation: "fadeUp .3s both" }}>
          <div style={{ width: 60, height: 60, borderRadius: 16, background: colors.surfaceMuted, display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px", color: "#B4B7C6" }}>
            <Icon name="search" size={26} />
          </div>
          <div style={{ fontSize: 17, fontWeight: 700 }}>По вашему запросу ничего не найдено</div>
          <div style={{ fontSize: 14, color: colors.textMuted, marginTop: 6, maxWidth: 360, marginLeft: "auto", marginRight: "auto", lineHeight: 1.55 }}>
            Попробуйте изменить формулировку, убрать лишние слова или использовать синонимы.
          </div>
        </div>
      )}

      {loading && <div style={{ color: colors.textMuted, fontSize: 14, padding: "20px 0" }}>Поиск…</div>}

      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </div>
  );
}
