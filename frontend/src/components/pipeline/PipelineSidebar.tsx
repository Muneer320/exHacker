"use client";

import { usePipeline } from "./PipelineContext";
import { PIPELINE_STAGES, type StageStatus } from "./types";
import ReadinessScore from "./ReadinessScore";

// ─── Status helpers ───────────────────────────────────────────────────────────

const STATUS_CONFIG: Record<StageStatus, { icon: string; color: string; label: string }> = {
  queued:       { icon: "○", color: "var(--text-3)", label: "Queued" },
  waiting:      { icon: "○", color: "var(--text-3)", label: "Waiting" },
  running:      { icon: "▶", color: "var(--blue)", label: "Running" },
  streaming:    { icon: "◉", color: "var(--blue-light)", label: "Streaming" },
  completed:    { icon: "✓", color: "var(--lime)", label: "Done" },
  failed:       { icon: "✕", color: "var(--error)", label: "Failed" },
  cached:       { icon: "⚡", color: "var(--sky)", label: "Cached" },
  using_fallback: { icon: "△", color: "var(--warning)", label: "Fallback" },
  skipped:      { icon: "—", color: "var(--text-3)", label: "Skipped" },
};

// ─── PipelineSidebar ──────────────────────────────────────────────────────────

export default function PipelineSidebar() {
  const { state, dispatch } = usePipeline();

  return (
    <aside style={{
      width: "280px", minWidth: "280px", height: "100%",
      background: "var(--surface-0)", borderRight: "1px solid var(--border)",
      display: "flex", flexDirection: "column", overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{ padding: "20px 20px 12px", borderBottom: "1px solid var(--border)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
          <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: state.projectStatus === "draft" ? "var(--warning)" : "var(--lime)", animation: state.projectStatus === "draft" ? "pulse 2s infinite" : "none" }} />
          <span style={{ fontSize: "11px", color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 500 }}>
            {state.projectStatus === "draft" ? "In Progress" : "Complete"}
          </span>
        </div>
        <h2 style={{ fontFamily: "var(--font-display)", fontSize: "15px", fontWeight: 700, color: "var(--text-1)", letterSpacing: "-0.01em" }}>
          {state.projectName}
        </h2>
      </div>

      {/* Pipeline stages */}
      <div style={{ flex: 1, overflow: "auto", padding: "8px 0" }}>
        {PIPELINE_STAGES.map((def, idx) => {
          const s = state.stages[def.id];
          if (!s) return null;
          const isActive = state.activeStageId === def.id;
          const config = STATUS_CONFIG[s.status];
          const isDone = s.status === "completed" || s.status === "cached";

          return (
            <div key={def.id}>
              <div
                onClick={() => dispatch({ type: "TOGGLE_EXPAND", stageId: def.id })}
                style={{
                  display: "flex", alignItems: "center", gap: "10px",
                  padding: "10px 16px 10px 20px", cursor: "pointer",
                  background: isActive ? "var(--blue-dim)" : "transparent",
                  borderLeft: isActive ? "2px solid var(--blue)" : "2px solid transparent",
                  transition: "all 0.15s",
                }}
                onMouseEnter={e => { if (!isActive) (e.currentTarget).style.background = "var(--surface-1)"; }}
                onMouseLeave={e => { if (!isActive) (e.currentTarget).style.background = "transparent"; }}
                role="button" tabIndex={0}
                aria-expanded={s.expanded}
                aria-label={`${def.name}: ${config.label}`}
                onKeyDown={e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); dispatch({ type: "TOGGLE_EXPAND", stageId: def.id }); } }}
              >
                {/* Status indicator */}
                <div style={{
                  width: "24px", height: "24px", borderRadius: "50%",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "10px", fontWeight: 700,
                  background: isDone ? "rgba(194,255,77,0.12)" : isActive ? "rgba(61,124,246,0.15)" : "var(--surface-2)",
                  color: config.color, flexShrink: 0,
                  transition: "all 0.3s",
                }}>
                  {s.status === "running" || s.status === "streaming" ? (
                    <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: config.color, animation: "pulse 1s infinite" }} />
                  ) : (
                    config.icon
                  )}
                </div>

                {/* Name + meta */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <span style={{ fontSize: "12px", fontWeight: 600, color: isActive ? "var(--text-1)" : isDone ? "var(--text-2)" : "var(--text-2)", letterSpacing: "-0.01em" }}>
                      {def.shortName}
                    </span>
                    {/* Confidence badge */}
                    {s.confidence !== null && s.status === "completed" && (
                      <span style={{ fontSize: "9px", padding: "1px 5px", borderRadius: "99px", background: s.confidence >= 0.8 ? "rgba(194,255,77,0.12)" : "rgba(245,158,11,0.12)", color: s.confidence >= 0.8 ? "var(--lime)" : "var(--warning)", fontWeight: 600 }}>
                        {Math.round(s.confidence * 100)}%
                      </span>
                    )}
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px", marginTop: "2px" }}>
                    <span style={{ fontSize: "10px", color: config.color, fontWeight: 500 }}>{config.label}</span>
                    {s.runtime !== null && isDone && (
                      <>
                        <span style={{ fontSize: "8px", color: "var(--text-3)" }}>·</span>
                        <span style={{ fontSize: "10px", color: "var(--text-3)" }}>{s.runtime}s</span>
                      </>
                    )}
                  </div>
                </div>

                {/* Expand indicator */}
                <span style={{ fontSize: "8px", color: "var(--text-3)", transform: s.expanded ? "rotate(90deg)" : "none", transition: "transform 0.15s" }}>▸</span>
              </div>

              {/* Expandable details */}
              {s.expanded && (
                <div style={{ padding: "0 16px 10px 52px" }}>
                  {/* Description */}
                  <p style={{ fontSize: "11px", color: "var(--text-3)", lineHeight: 1.5, marginBottom: "8px" }}>
                    {def.description}
                  </p>

                  {/* Model attribution */}
                  {s.modelUsed && (
                    <div style={{ fontSize: "10px", color: "var(--text-3)", marginBottom: "6px" }}>
                      <span style={{ fontWeight: 500 }}>Model:</span> {s.modelUsed}
                    </div>
                  )}

                  {/* Cache/fallback badges */}
                  {s.isCached && <span className="badge badge-sky" style={{ fontSize: "9px", padding: "1px 6px", marginBottom: "6px" }}>⚡ Cached</span>}
                  {s.isFallback && <span className="badge" style={{ fontSize: "9px", padding: "1px 6px", marginBottom: "6px", borderColor: "rgba(245,158,11,0.2)", color: "var(--warning)", background: "rgba(245,158,11,0.08)" }}>△ Fallback</span>}

                  {/* Key findings */}
                  {s.keyFindings.length > 0 && (
                    <div style={{ marginBottom: "8px" }}>
                      <span style={{ fontSize: "9px", color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 600 }}>Findings</span>
                      <ul style={{ listStyle: "none", padding: 0, margin: "4px 0" }}>
                        {s.keyFindings.map((f, i) => (
                          <li key={i} style={{ fontSize: "11px", color: "var(--text-2)", lineHeight: 1.5, paddingLeft: "8px", borderLeft: "1px solid var(--blue)", marginBottom: "3px" }}>{f}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Summary */}
                  {s.summary && (
                    <p style={{ fontSize: "11px", color: "var(--text-2)", lineHeight: 1.5, marginBottom: "6px" }}>{s.summary}</p>
                  )}

                  {/* Error */}
                  {s.error && (
                    <div style={{ padding: "8px 10px", background: "rgba(239,68,68,0.06)", border: "1px solid rgba(239,68,68,0.15)", borderRadius: "4px", fontSize: "11px", color: "#fca5a5", marginBottom: "6px" }}>
                      {s.error}
                    </div>
                  )}

                  {/* Streaming log */}
                  {s.log.length > 0 && (
                    <div style={{ background: "var(--surface-0)", borderRadius: "4px", padding: "8px 10px", fontSize: "10px", fontFamily: "var(--font-mono)", lineHeight: 1.8 }}>
                      {s.log.map(l => (
                        <div key={l.id} style={{ color: l.type === "error" ? "var(--error)" : l.type === "complete" ? "var(--lime)" : l.type === "ai" ? "var(--blue-light)" : l.type === "search" ? "var(--sky)" : "var(--text-3)" }}>
                          {l.text}
                        </div>
                      ))}
                      {(s.status === "running" || s.status === "streaming") && (
                        <span style={{ color: "var(--blue)", animation: "pulse 1s infinite" }}>_</span>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Connector line between stages */}
              {idx < PIPELINE_STAGES.length - 1 && (
                <div style={{ marginLeft: "32px", width: "1px", height: "8px", background: "var(--border)" }} />
              )}
            </div>
          );
        })}
      </div>

      {/* Readiness score */}
      <ReadinessScore />

      {/* Bottom actions */}
      <div style={{ borderTop: "1px solid var(--border)", padding: "12px 16px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--text-3)" }}>⌘K</span>
          <span style={{ fontSize: "9px", color: "var(--text-3)" }}>v{/* version would go here */}</span>
        </div>
      </div>
    </aside>
  );
}
