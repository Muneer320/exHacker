"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { getDecisions, DecisionEntry } from "@/services/api";
import { Card, Pill, SeverityBadge, LoadingState, EmptyState } from "@/components/shared/ui";

const CATEGORY_MAP: Record<string, { icon: string; color: string }> = {
  opportunity_selected: { icon: "🎯", color: "var(--lime)" },
  direction_rejected: { icon: "❌", color: "var(--error)" },
  tech_chosen: { icon: "⚙️", color: "var(--blue)" },
  architecture_tradeoff: { icon: "🏗️", color: "var(--warning)" },
  research_finding: { icon: "🔬", color: "var(--sky)" },
  risk_accepted: { icon: "⚠️", color: "var(--error)" },
  feature_scoped: { icon: "📐", color: "var(--info)" },
  specialist_review: { icon: "🧠", color: "var(--blue-light)" },
  direction_generated: { icon: "💡", color: "var(--lime)" },
};

export default function TimelinePage() {
  const params = useParams();
  const projectId = params.id as string;
  const [entries, setEntries] = useState<DecisionEntry[]>([]);
  const [filter, setFilter] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { if (projectId) { setLoading(true); getDecisions(projectId, filter ?? undefined).then(r => { if (r.success) setEntries(r.data.entries); }).finally(() => setLoading(false)); } }, [projectId, filter]);

  const categories = [...new Set(entries.map(e => e.category))];

  return (
    <div>
      <div className="anim-fade-up" style={{ marginBottom: "20px" }}>
        <span className="sec-num">[ TIMELINE ]</span>
        <h2 className="d4" style={{ color: "var(--text-1)", marginBottom: "4px" }}>Decision Timeline</h2>
        <p className="body-sm">{entries.length} decisions · Append-only journal</p>
      </div>

      {/* Filter */}
      <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "20px" }}>
        <button onClick={() => setFilter(null)} className={`chip ${!filter ? "active" : ""}`}>All</button>
        {categories.map(c => (
          <button key={c} onClick={() => setFilter(c)} className={`chip ${filter === c ? "active" : ""}`}>
            {CATEGORY_MAP[c]?.icon || "📄"} {c.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      {/* Timeline */}
      <div style={{ position: "relative" }}>
        {/* Vertical line */}
        <div style={{ position: "absolute", left: "20px", top: "0", bottom: "0", width: "1px", background: "var(--border)" }} />

        <div style={{ display: "flex", flexDirection: "column", gap: "0" }}>
          {entries.length === 0 && (
            <div style={{ padding: "48px 20px", textAlign: "center", color: "var(--text-3)", fontSize: "13px" }}>
              No decisions recorded yet. Decisions appear automatically as specialists complete their work.
            </div>
          )}
          {entries.map((entry, i) => (
            <TimelineEntry key={entry.id} entry={entry} isLast={i === entries.length - 1} />
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Timeline Entry Component ─────────────────────────────────────────────────

function TimelineEntry({ entry, isLast }: { entry: DecisionEntry; isLast: boolean }) {
  const [expanded, setExpanded] = useState(false);
  const meta = CATEGORY_MAP[entry.category] || { icon: "📄", color: "var(--text-3)" };
  const statusColor = entry.status === "accepted" ? "var(--lime)" : entry.status === "rejected" ? "var(--error)" : entry.status === "superseded" ? "var(--warning)" : "var(--text-3)";

  return (
    <div style={{ display: "flex", gap: "16px", padding: "12px 0" }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: "40px", flexShrink: 0 }}>
        <div style={{ width: "28px", height: "28px", borderRadius: "50%", zIndex: 1, display: "flex", alignItems: "center", justifyContent: "center", background: `${meta.color}15`, border: `1px solid ${meta.color}30` }}>
          <span style={{ fontSize: "12px" }}>{meta.icon}</span>
        </div>
      </div>
      <div style={{ flex: 1, minWidth: 0, cursor: "pointer" }} onClick={() => setExpanded(!expanded)}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px", flexWrap: "wrap" }}>
          <span style={{ fontSize: "12px", fontFamily: "var(--font-mono)", color: "var(--text-3)" }}>#{entry.entry_number}</span>
          <Pill color={meta.color} bg={`${meta.color}12`}>{entry.category.replace(/_/g, " ")}</Pill>
          <Pill color={statusColor} bg="var(--surface-2)">{entry.status}</Pill>
          {entry.confidence !== null && <Pill color="var(--blue-light)" bg="var(--blue-dim)">{Math.round(entry.confidence * 100)}%</Pill>}
        </div>
        <h4 style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "2px" }}>{entry.title}</h4>
        <p style={{ fontSize: "12px", color: "var(--text-2)", lineHeight: 1.5 }}>{entry.description}</p>
        {expanded && (
          <div style={{ marginTop: "10px", padding: "12px", background: "var(--surface-0)", borderRadius: "var(--r-sm)" }}>
            {entry.rationale && <div style={{ marginBottom: "8px" }}><span className="label" style={{ marginBottom: "4px", display: "block" }}>Rationale</span><p style={{ fontSize: "11px", color: "var(--text-2)" }}>{entry.rationale}</p></div>}
            {entry.alternatives_considered?.filter((a: any) => a.title).map((alt: any, j: number) => (
              <div key={j} style={{ marginBottom: "6px", padding: "8px", background: "var(--surface-1)", borderRadius: "var(--r-sm)" }}>
                <p style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-1)", marginBottom: "2px" }}>{alt.title}</p>
                <div style={{ fontSize: "10px", color: "var(--text-3)" }}>
                  {alt.pros?.length > 0 && <p>Pros: {Array.isArray(alt.pros) ? alt.pros.join(", ") : alt.pros}</p>}
                  {alt.cons?.length > 0 && <p>Cons: {Array.isArray(alt.cons) ? alt.cons.join(", ") : alt.cons}</p>}
                </div>
              </div>
            ))}
            <div style={{ fontSize: "10px", color: "var(--text-3)", marginTop: "8px" }}>Specialist: {entry.originating_specialist} · {new Date(entry.created_at).toLocaleString()}</div>
          </div>
        )}
        {!isLast && <div style={{ height: "12px" }} />}
      </div>
    </div>
  );
}
