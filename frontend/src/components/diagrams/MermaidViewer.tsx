"use client";

import { useEffect, useRef, useState } from "react";

interface MermaidViewerProps {
  code: string;
  title?: string;
}

// Maximum length to render. Beyond this, show a download link instead.
const MAX_CHARS = 10000;

export default function MermaidViewer({ code, title }: MermaidViewerProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [rendered, setRendered] = useState(false);

  useEffect(() => {
    if (!ref.current || !code || rendered) return;

    // Reset
    ref.current.innerHTML = "";

    // Guard against empty/trivial code
    const trimmed = code.trim();
    if (!trimmed || trimmed.length < 6) {
      setError("Diagram too short to render.");
      return;
    }
    if (trimmed.length > MAX_CHARS) {
      setError("Diagram too large to render inline.");
      return;
    }

    let cancelled = false;

    import("mermaid").then((mermaid) => {
      if (cancelled) return;
      mermaid.default.initialize({
        startOnLoad: false,
        theme: "dark",
        themeVariables: {
          primaryColor: "#161616",
          primaryTextColor: "#f2f2f2",
          primaryBorderColor: "rgba(255,255,255,0.06)",
          lineColor: "#3d7cf6",
          secondaryColor: "#202020",
          tertiaryColor: "#0e0e0e",
          fontFamily: "Inter, sans-serif",
          fontSize: "12px",
          edgeLabelBackground: "#161616",
          nodeBorder: "rgba(255,255,255,0.10)",
        },
        flowchart: { useMaxWidth: true, htmlLabels: true },
        sequence: { useMaxWidth: true },
        gantt: { useMaxWidth: true },
      });

      const id = `mermaid-${Math.random().toString(36).slice(2, 8)}`;

      mermaid.default.render(id, trimmed).then((svg) => {
        if (cancelled || !ref.current) return;
        ref.current.innerHTML = svg.svg;
        setRendered(true);
      }).catch((err) => {
        if (!cancelled) setError(String(err.message || err));
      });
    }).catch(() => {
      if (!cancelled) setError("Failed to load mermaid renderer.");
    });

    return () => { cancelled = true; };
  }, [code, rendered]);

  if (!code?.trim()) return null;

  if (error) {
    return (
      <div style={{
        padding: "16px", background: "var(--surface-0)", borderRadius: "4px",
        border: "1px solid rgba(239,68,68,0.15)", fontSize: "11px", color: "#fca5a5",
        fontFamily: "var(--font-mono)", whiteSpace: "pre-wrap",
      }}>
        <div style={{ fontWeight: 600, marginBottom: "4px", color: "var(--error)" }}>⚠ Diagram Render Error</div>
        <div>{error}</div>
        <details style={{ marginTop: "8px" }}>
          <summary style={{ cursor: "pointer", color: "var(--text-3)" }}>Show source</summary>
          <pre style={{ marginTop: "8px", color: "var(--text-2)", fontSize: "10px" }}>{code}</pre>
        </details>
      </div>
    );
  }

  return (
    <div>
      <div className="term-bar" style={{ padding: "6px 12px", borderTopLeftRadius: "4px", borderTopRightRadius: "4px" }}>
        <span className="term-dot term-dot-r" /><span className="term-dot term-dot-y" /><span className="term-dot term-dot-g" />
        <span style={{ marginLeft: "auto", fontSize: "9px", color: "var(--text-3)" }}>{title || "diagram"}</span>
      </div>
      <div
        ref={ref}
        style={{
          padding: "20px", overflow: "auto", background: "var(--surface-0)",
          border: "1px solid var(--border-mid)", borderTop: "none",
          borderBottomLeftRadius: "4px", borderBottomRightRadius: "4px",
          minHeight: "100px", display: "flex", alignItems: "center", justifyContent: "center",
        }}
      />
    </div>
  );
}
