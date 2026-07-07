"use client";

import { ReactNode } from "react";

// ─── Card ─────────────────────────────────────────────────────────────────────

export function Card({ children, accent, hover, style, onClick }: { children: ReactNode; accent?: string; hover?: boolean; style?: React.CSSProperties; onClick?: () => void }) {
  return (
    <div style={{
      background: "var(--surface-1)", borderRadius: "var(--r-md)",
      border: accent ? `1px solid ${accent}30` : "1px solid var(--border)",
      borderLeft: accent ? `2px solid ${accent}` : undefined,
      padding: "20px", transition: hover ? "all 0.15s" : undefined, ...style,
    }}
      onMouseEnter={hover ? e => { (e.currentTarget).style.borderColor = "var(--border-mid)"; } : undefined}
      onMouseLeave={hover ? e => { (e.currentTarget).style.borderColor = accent ? `${accent}30` : "var(--border)"; } : undefined}
      onClick={onClick}
    >
      {children}
    </div>
  );
}

// ─── Section ─────────────────────────────────────────────────────────────────

export function Section({ title, icon, color, children }: { title: string; icon?: ReactNode; color?: string; children: ReactNode }) {
  return (
    <div style={{ marginBottom: "20px" }}>
      <div style={{
        display: "flex", alignItems: "center", gap: "6px",
        marginBottom: "12px", color: color || "var(--text-2)",
      }}>
        {icon && <span style={{ fontSize: "13px" }}>{icon}</span>}
        <span style={{
          fontSize: "11px", fontWeight: 600, letterSpacing: "0.08em",
          textTransform: "uppercase", color: color || "var(--text-3)",
        }}>
          {title}
        </span>
      </div>
      {children}
    </div>
  );
}

// ─── ScoreBar ────────────────────────────────────────────────────────────────

export function ScoreBar({ value, color, size }: { value: number; color?: string; size?: "sm" | "md" }) {
  const h = size === "sm" ? "4px" : "6px";
  return (
    <div style={{ height: h, borderRadius: "3px", background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
      <div style={{
        width: `${Math.min(100, Math.max(0, value))}%`, height: "100%",
        borderRadius: "3px", background: color || "var(--blue)",
        transition: "width 1s cubic-bezier(.25,.8,.25,1)",
      }} />
    </div>
  );
}

// ─── ScoreRow ────────────────────────────────────────────────────────────────

export function ScoreRow({ label, value, color, showValue }: { label: string; value: number | null; color?: string; showValue?: boolean }) {
  if (value === null || value === undefined) return null;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
      <span style={{ fontSize: "11px", color: "var(--text-3)", minWidth: "70px", textAlign: "right", flexShrink: 0 }}>{label}</span>
      <div style={{ flex: 1 }}>
        <ScoreBar value={value} color={color} />
      </div>
      {showValue !== false && (
        <span style={{ fontSize: "11px", color: "var(--text-2)", fontWeight: 600, minWidth: "24px", fontFamily: "var(--font-mono)" }}>{Math.round(value)}</span>
      )}
    </div>
  );
}

// ─── Badge ────────────────────────────────────────────────────────────────────

export function Pill({ children, color, bg, style }: { children: ReactNode; color?: string; bg?: string; style?: React.CSSProperties }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: "4px",
      padding: "2px 8px", borderRadius: "99px", fontSize: "10px",
      fontWeight: 600, color: color || "var(--text-2)",
      background: bg || "var(--surface-2)", letterSpacing: "0.02em", ...style,
    }}>
      {children}
    </span>
  );
}

// ─── SeverityBadge ───────────────────────────────────────────────────────────

export function SeverityBadge({ severity }: { severity: string }) {
  const colors: Record<string, string> = { high: "var(--error)", medium: "var(--warning)", low: "var(--info)" };
  const color = colors[severity] || "var(--text-3)";
  return <Pill color={color} bg={`${color}15`}>{severity}</Pill>;
}

// ─── Grid ─────────────────────────────────────────────────────────────────────

export function Grid({ cols, gap, children }: { cols?: number; gap?: string; children: ReactNode }) {
  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: cols ? `repeat(${cols}, 1fr)` : "repeat(auto-fit, minmax(280px, 1fr))",
      gap: gap || "12px",
    }}>
      {children}
    </div>
  );
}

// ─── StatCard ─────────────────────────────────────────────────────────────────

export function StatCard({ label, value, color }: { label: string; value: string | number; color?: string }) {
  return (
    <Card>
      <div style={{ textAlign: "center" }}>
        <p style={{ fontSize: "22px", fontWeight: 800, color: color || "var(--blue-light)", fontFamily: "var(--font-display)", letterSpacing: "-0.02em", lineHeight: 1, marginBottom: "6px" }}>
          {value}
        </p>
        <p style={{ fontSize: "10px", color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 500 }}>
          {label}
        </p>
      </div>
    </Card>
  );
}

// ─── EmptyState ──────────────────────────────────────────────────────────────

export function EmptyState({ icon, title, description, action }: { icon: string; title: string; description: string; action?: ReactNode }) {
  return (
    <div style={{
      textAlign: "center", padding: "64px 24px",
      border: "1px dashed var(--border)", borderRadius: "var(--r-lg)",
    }}>
      <p style={{ fontSize: "32px", marginBottom: "12px" }}>{icon}</p>
      <h3 style={{ fontSize: "15px", fontWeight: 600, marginBottom: "6px", color: "var(--text-1)" }}>{title}</h3>
      <p style={{ fontSize: "13px", color: "var(--text-2)", marginBottom: "20px", maxWidth: "400px", margin: "0 auto 20px" }}>{description}</p>
      {action}
    </div>
  );
}

// ─── LoadingState ─────────────────────────────────────────────────────────────

export function LoadingState({ label }: { label?: string }) {
  return (
    <div style={{ textAlign: "center", padding: "64px 24px" }}>
      <div className="spinner" style={{ margin: "0 auto 16px" }} />
      <p style={{ fontSize: "13px", color: "var(--text-2)" }}>{label || "Loading..."}</p>
    </div>
  );
}
