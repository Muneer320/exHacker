"use client";

import { useState, useEffect, useRef, type ReactNode } from "react";

// ─── Status badges ────────────────────────────────────────────────────────────

function StepBadge({ status }: { status: "pending" | "running" | "done" | "error" }) {
  const cfg = {
    pending: { icon: "○", color: "var(--text-3)", label: "Not started" },
    running: { icon: "◉", color: "var(--blue)", label: "In progress" },
    done: { icon: "✓", color: "var(--lime)", label: "Complete" },
    error: { icon: "✕", color: "var(--error)", label: "Error" },
  }[status];
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: "5px", fontSize: "10px", fontWeight: 600, color: cfg.color, letterSpacing: "0.03em" }}>
      <span style={{ animation: status === "running" ? "pulse 1s infinite" : "none" }}>{cfg.icon}</span>
      {cfg.label}
    </span>
  );
}

// ─── Streaming log line ───────────────────────────────────────────────────────

interface LogLine {
  text: string;
  type: "info" | "search" | "ai" | "synthesis" | "done" | "error";
}

const LOG_COLORS: Record<string, string> = {
  info: "var(--text-3)",
  search: "var(--sky)",
  ai: "var(--blue-light)",
  synthesis: "var(--text-2)",
  done: "var(--lime)",
  error: "var(--error)",
};

function GenLog({ lines }: { lines: LogLine[] }) {
  const endRef = useRef<HTMLDivElement>(null);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [lines.length]);

  if (lines.length === 0) return null;

  return (
    <div style={{ marginTop: "12px", padding: "10px 12px", background: "var(--surface-0)", borderRadius: "var(--r-sm)", fontFamily: "var(--font-mono)", fontSize: "11px", lineHeight: 1.8 }}>
      {lines.map((l, i) => (
        <div key={i} style={{ color: LOG_COLORS[l.type] }}>{l.text}</div>
      ))}
      <div ref={endRef} />
      <span style={{ animation: "pulse 1s infinite", color: "var(--blue)" }}>_</span>
    </div>
  );
}

// ─── GuidedSection ────────────────────────────────────────────────────────────

interface GuidedSectionProps {
  /** What this specialist does */
  title: string;
  /** Why the user should care */
  whyMatters?: string;
  /** Current generation status */
  status: "idle" | "generating" | "done" | "error";
  /** Primary CTA label */
  actionLabel: string;
  /** Called when user clicks CTA */
  onAction: () => void;
  /** Estimated runtime (for generating state) */
  estimatedTime?: string;
  /** What will be produced */
  whatProduced?: string;
  /** What unlocks after this completes */
  unlocks?: string;
  /** Streaming log lines during generation */
  logLines?: LogLine[];
  /** Error message */
  error?: string;
  /** Already-generated content (shown below the guided section) */
  children?: ReactNode;
  /** Whether to show the guided section (true when content doesn't exist yet) */
  show?: boolean;
}

export default function GuidedSection({
  title, whyMatters, status, actionLabel, onAction,
  estimatedTime, whatProduced, unlocks,
  logLines, error, children, show = true,
}: GuidedSectionProps) {
  const [startTime] = useState(Date.now());
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (status !== "generating") { setElapsed(0); return; }
    const t = setInterval(() => setElapsed(Math.floor((Date.now() - startTime) / 1000)), 1000);
    return () => clearInterval(t);
  }, [status, startTime]);

  const fmtTime = (s: number) => {
    if (s < 60) return `${s}s`;
    return `${Math.floor(s / 60)}m ${s % 60}s`;
  };

  if (!show && status !== "generating") {
    return <>{children}</>;
  }

  return (
    <div>
      {/* Guided section */}
      <div className="anim-fade-up" style={{
        padding: "20px", borderRadius: "var(--r-md)",
        border: `1px solid ${
          status === "done" ? "rgba(194,255,77,0.25)" :
          status === "error" ? "rgba(239,68,68,0.25)" :
          status === "generating" ? "rgba(61,124,246,0.25)" :
          "var(--border)"
        }`,
        background: status === "done" ? "rgba(194,255,77,0.03)" :
                    status === "generating" ? "rgba(61,124,246,0.03)" :
                    "var(--surface-1)",
        marginBottom: "20px",
      }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px", gap: "12px", flexWrap: "wrap" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
              <h3 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-1)", letterSpacing: "-0.01em" }}>{title}</h3>
              <StepBadge status={status === "idle" ? "pending" : status === "generating" ? "running" : status === "error" ? "error" : "done"} />
            </div>
            {whyMatters && <p style={{ fontSize: "12px", color: "var(--text-2)", lineHeight: 1.5 }}>{whyMatters}</p>}
          </div>

          {/* Primary action */}
          {status === "idle" && (
            <button onClick={onAction} className="btn btn-primary" style={{ whiteSpace: "nowrap", fontSize: "13px", padding: "10px 20px" }}>
              {actionLabel}
            </button>
          )}
        </div>

        {/* Info grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "10px", marginBottom: status === "idle" ? 0 : "12px" }}>
          {status === "generating" && estimatedTime && (
            <Info label="Estimated time" value={estimatedTime} />
          )}
          {whatProduced && status !== "generating" && (
            <Info label="Produces" value={whatProduced} />
          )}
          {unlocks && status === "done" && (
            <Info label="Unlocks" value={unlocks} />
          )}
          {status === "generating" && (
            <Info label="Elapsed" value={fmtTime(elapsed)} />
          )}
        </div>

        {/* Streaming log */}
        {status === "generating" && logLines && <GenLog lines={logLines} />}

        {/* Error */}
        {status === "error" && error && (
          <div style={{ marginTop: "10px", padding: "10px 12px", background: "rgba(239,68,68,0.06)", borderRadius: "var(--r-sm)", border: "1px solid rgba(239,68,68,0.15)", fontSize: "11px", color: "#fca5a5", display: "flex", alignItems: "center", gap: "8px" }}>
            <span>⚠</span>
            <span>{error}</span>
            <button onClick={onAction} className="btn btn-ghost" style={{ marginLeft: "auto", padding: "4px 10px", fontSize: "10px" }}>Retry</button>
          </div>
        )}

        {/* Done — offer next action */}
        {status === "done" && (
          <div style={{ marginTop: "10px", padding: "8px 12px", background: "rgba(194,255,77,0.06)", borderRadius: "var(--r-sm)", fontSize: "11px", color: "var(--lime)", display: "flex", alignItems: "center", gap: "8px" }}>
            <span>✓</span>
            <span>Complete.</span>
            {unlocks && <span style={{ color: "var(--text-3)" }}>Next: {unlocks}</span>}
          </div>
        )}
      </div>

      {/* Generated content */}
      {children}
    </div>
  );
}

// ─── Info pill ─────────────────────────────────────────────────────────────────

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span style={{ fontSize: "10px", color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.05em", fontWeight: 500, display: "block", marginBottom: "2px" }}>{label}</span>
      <span style={{ fontSize: "12px", color: "var(--text-2)", fontWeight: 600 }}>{value}</span>
    </div>
  );
}
