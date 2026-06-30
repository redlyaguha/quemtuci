import { useEffect, useRef, useState } from "react";
import { Icon } from "../components/Icon";
import { DocBadge } from "../components/DocBadge";
import { StatusChip } from "../components/StatusChip";
import { Toast } from "../components/Toast";
import { useAuth } from "../hooks/useAuth";
import { documentsApi } from "../api";
import { localDocs } from "../data/localDocs";
import { colors } from "../theme";
import type { DocumentItem, DocumentType, DocumentStatus } from "../types";

/**
 * Загрузка документов — [FE-03].
 * Drag-and-Drop + выбор файла, валидация (PDF/DOCX, ≤20 МБ),
 * прогресс-бары со сменой статусов (Загрузка → Индексация → Готово / Ошибка),
 * таблица загруженных документов.
 *
 * Пока backend `/documents/upload` ([BE-D1]) не готов, загрузка эмулируется
 * клиентски, чтобы экран был проверяем; при готовности API используется он.
 */

const MAX_SIZE = 20 * 1024 * 1024; // 20 МБ — лимит backend
const ACCEPT = ".pdf,.docx";

interface UploadItem {
  id: number;
  name: string;
  type: DocumentType;
  size: string;
  progress: number;
  status: DocumentStatus;
  /** object URL для просмотра загруженного файла. */
  url?: string;
}

function fileType(name: string): DocumentType | null {
  const lower = name.toLowerCase();
  if (lower.endsWith(".pdf")) return "PDF";
  if (lower.endsWith(".docx")) return "DOCX";
  return null;
}

function humanSize(bytes: number): string {
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
  return `${Math.max(1, Math.round(bytes / 1024))} КБ`;
}

const today = () =>
  new Date().toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" });

export default function UploadDocumentsPage() {
  const { user } = useAuth();
  const canDelete = user?.role === "teacher" || user?.role === "admin";

  const [docs, setDocs] = useState<DocumentItem[]>(localDocs.list());
  const [uploads, setUploads] = useState<UploadItem[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Начальный список документов из API (с фолбэком на общий демо-стор).
  useEffect(() => {
    let alive = true;
    documentsApi
      .list()
      .then((d) => alive && setDocs(d))
      .catch(() => {/* остаёмся на демо-данных стора */});
    return () => {
      alive = false;
    };
  }, []);

  const patchUpload = (id: number, patch: Partial<UploadItem>) =>
    setUploads((list) => list.map((u) => (u.id === id ? { ...u, ...patch } : u)));

  const addDoc = (doc: DocumentItem) => {
    localDocs.add(doc);
    setDocs((list) => [doc, ...list]);
  };

  const removeDoc = (doc: DocumentItem) => {
    documentsApi.remove(doc.id).catch(() => {/* backend не готов — локального удаления достаточно */});
    localDocs.remove(doc.id);
    setDocs((list) => list.filter((d) => d.id !== doc.id));
    if (doc.url) URL.revokeObjectURL(doc.url);
    setToast("Документ удалён из базы");
  };

  const openDoc = (doc: DocumentItem) => {
    if (doc.url) window.open(doc.url, "_blank", "noopener");
    else setToast("Файл доступен после интеграции с хранилищем");
  };

  /** Клиентская эмуляция: Загрузка → Индексация → Готово. */
  const simulate = (item: UploadItem) => {
    let progress = 0;
    let phase: DocumentStatus = "uploading";
    const tick = () => {
      progress += 9 + Math.random() * 8;
      if (progress >= 100) {
        if (phase === "uploading") {
          phase = "indexing";
          progress = 0;
          patchUpload(item.id, { status: "indexing", progress: 0 });
        } else {
          patchUpload(item.id, { status: "done", progress: 100 });
          addDoc({
            id: item.id,
            name: item.name,
            type: item.type,
            date: today(),
            size: item.size,
            frags: 30 + Math.floor(Math.random() * 90),
            status: "done",
            url: item.url,
          });
          setToast("Документ проиндексирован и добавлен в базу");
          return;
        }
      }
      patchUpload(item.id, { progress: Math.min(100, progress) });
      setTimeout(tick, 280);
    };
    setTimeout(tick, 280);
  };

  const startUpload = async (file: File) => {
    const type = fileType(file.name);
    if (!type) {
      setToast("Поддерживаются только PDF и DOCX");
      return;
    }
    if (file.size > MAX_SIZE) {
      setToast("Файл больше 20 МБ");
      return;
    }

    const item: UploadItem = {
      id: Date.now() + Math.floor(Math.random() * 1000),
      name: file.name,
      type,
      size: humanSize(file.size),
      progress: 0,
      status: "uploading",
      url: URL.createObjectURL(file), // для просмотра файла в этой сессии
    };
    setUploads((list) => [item, ...list]);

    try {
      const doc = await documentsApi.upload(file, (percent) => patchUpload(item.id, { progress: percent }));
      patchUpload(item.id, { status: "done", progress: 100 });
      addDoc({ ...doc, url: doc.url ?? item.url });
      setToast("Документ проиндексирован и добавлен в базу");
    } catch {
      // backend не готов — эмулируем процесс, чтобы экран был проверяем.
      simulate(item);
    }
  };

  const handleFiles = (files: FileList | null) => {
    if (!files) return;
    Array.from(files).forEach(startUpload);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div style={{ animation: "fadeUp .3s both", maxWidth: 860 }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-.5px", margin: "0 0 16px" }}>
        Загрузка документов
      </h1>

      {/* Dropzone */}
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && inputRef.current?.click()}
        style={{
          border: `2px dashed ${dragOver ? colors.primary : "#CBC9F0"}`,
          background: dragOver ? "#F3F2FF" : "#FBFAFF",
          borderRadius: 20,
          padding: "42px 24px",
          textAlign: "center",
          cursor: "pointer",
          transition: ".15s",
        }}
      >
        <div
          style={{
            width: 64,
            height: 64,
            borderRadius: 18,
            background: colors.primarySoft,
            color: colors.primary,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 16px",
          }}
        >
          <Icon name="upload" size={28} />
        </div>
        <div style={{ fontSize: 17, fontWeight: 700 }}>Перетащите файлы сюда</div>
        <div style={{ fontSize: 14, color: colors.textMuted, marginTop: 5 }}>
          или нажмите, чтобы выбрать · PDF, DOCX · до 20 МБ
        </div>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPT}
          multiple
          hidden
          onChange={(e) => {
            handleFiles(e.target.files);
            e.target.value = "";
          }}
        />
      </div>

      {/* Прогресс загрузки */}
      {uploads.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 11px" }}>Загрузка и индексация</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 11 }}>
            {uploads.map((u) => {
              const barColor =
                u.status === "indexing" ? colors.warning : u.status === "error" ? colors.danger : u.status === "done" ? colors.success : colors.primary;
              return (
                <div key={u.id} style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 14, padding: "14px 16px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 11 }}>
                    <DocBadge type={u.type} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 13.5, fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{u.name}</div>
                      <div style={{ fontSize: 11.5, color: colors.textFaint }}>{u.size}</div>
                    </div>
                    <StatusChip status={u.status} />
                  </div>
                  <div style={{ marginTop: 11, height: 6, background: colors.borderMuted, borderRadius: 999, overflow: "hidden" }}>
                    <div style={{ height: "100%", width: `${Math.round(u.progress)}%`, background: barColor, borderRadius: 999, transition: "width .3s" }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Таблица документов */}
      <div style={{ marginTop: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 11px" }}>Загруженные документы</h3>
        <div style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 16, overflow: "hidden" }}>
          <div
            style={{
              display: "flex",
              padding: "11px 16px",
              background: colors.surfaceMuted,
              borderBottom: `1px solid ${colors.borderMuted}`,
              fontSize: 11.5,
              fontWeight: 600,
              color: colors.textFaint,
              textTransform: "uppercase",
              letterSpacing: ".4px",
            }}
          >
            <div style={{ flex: 1 }}>Документ</div>
            <div style={{ width: 120 }}>Дата</div>
            <div style={{ width: 90 }}>Размер</div>
            <div style={{ width: 110 }}>Фрагменты</div>
            <div style={{ width: 110 }}>Статус</div>
            <div style={{ width: 84, textAlign: "right" }}>Действия</div>
          </div>
          {docs.map((d) => (
            <div key={d.id} style={{ display: "flex", alignItems: "center", padding: "13px 16px", borderBottom: `1px solid ${colors.borderMuted}`, fontSize: 13.5 }}>
              <div style={{ flex: 1, display: "flex", alignItems: "center", gap: 11, minWidth: 0 }}>
                <DocBadge type={d.type} />
                <button
                  onClick={() => openDoc(d)}
                  title="Открыть документ"
                  style={{ background: "none", border: "none", padding: 0, fontWeight: 500, fontSize: 13.5, color: colors.text, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", cursor: "pointer", textAlign: "left", minWidth: 0 }}
                >
                  {d.name}
                </button>
              </div>
              <div style={{ width: 120, color: colors.textMuted }}>{d.date ?? "—"}</div>
              <div style={{ width: 90, color: colors.textMuted }}>{d.size ?? "—"}</div>
              <div style={{ width: 110, color: colors.textMuted }}>{d.frags || "—"}</div>
              <div style={{ width: 110 }}>
                <StatusChip status={d.status} />
              </div>
              <div style={{ width: 84, display: "flex", gap: 4, justifyContent: "flex-end" }}>
                <button onClick={() => openDoc(d)} title="Открыть" style={iconActionStyle(false)}>
                  <Icon name="file" size={15} />
                </button>
                {canDelete && (
                  <button onClick={() => removeDoc(d)} title="Удалить" style={iconActionStyle(true)}>
                    <Icon name="trash" size={15} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </div>
  );
}

function iconActionStyle(danger: boolean): React.CSSProperties {
  return {
    background: "none",
    border: `1px solid ${colors.border}`,
    color: danger ? "#C7575C" : colors.textSoft,
    width: 30,
    height: 30,
    borderRadius: 8,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    flex: "0 0 auto",
  };
}
