import { colors, font } from "../theme";
import type { DocumentType } from "../types";

/** Бейдж типа документа (PDF/DOCX). */
export function DocBadge({ type }: { type: DocumentType }) {
  const pdf = type === "PDF";
  return (
    <span
      style={{
        background: pdf ? colors.dangerSoft : colors.infoSoft,
        color: pdf ? colors.danger : colors.info,
        fontSize: 10.5,
        fontWeight: 700,
        padding: "4px 8px",
        borderRadius: 7,
        flex: "0 0 auto",
        fontFamily: font.mono,
      }}
    >
      {type}
    </span>
  );
}
