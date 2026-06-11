"use client";

import { useState } from "react";
import { ProjectResult } from "../types/project";

const VOID    = "#171715";
const SLATE   = "#848fa5";
const MINT    = "#c5fffd";
const INK_DIM = "rgba(132,143,165,0.85)";
const INK_MUT = "rgba(132,143,165,0.5)";
const RIM     = "rgba(132,143,165,0.14)";

export default function ReportCard({ result }: { result: ProjectResult }) {
  const [copied, setCopied] = useState(false);

  const text = result.final_report || "";

  async function handleCopy() {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2200);
  }

  return (
    <div>
      {/* Toolbar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "10px 16px",
          background: "rgba(56,56,53,0.7)",
          border: `1px solid ${RIM}`,
          borderBottom: "none",
        }}
      >
        <div style={{ display: "flex", gap: "6px" }}>
          {[SLATE, SLATE, SLATE].map((c, i) => (
            <div key={i} style={{ width: "9px", height: "9px", borderRadius: "50%", background: `rgba(132,143,165,0.3)` }} />
          ))}
          <span style={{ marginLeft: "8px", fontSize: "10px", letterSpacing: "1px", color: INK_MUT, fontFamily: "monospace" }}>
            exhacker · final_report.md
          </span>
        </div>
        <button onClick={handleCopy} className="btn-ghost" style={{ fontSize: "10px", padding: "5px 14px" }}>
          {copied ? "✓ Copied" : "Copy Report"}
        </button>
      </div>

      {/* Report content */}
      <div
        style={{
          background: VOID,
          border: `1px solid ${RIM}`,
          padding: "28px 32px",
          fontFamily: "'DM Mono', 'Fira Code', 'Courier New', monospace",
          fontSize: "12px",
          color: INK_DIM,
          lineHeight: 1.9,
          whiteSpace: "pre-wrap",
          overflowX: "auto",
          maxHeight: "700px",
          overflowY: "auto",
        }}
      >
        {text || (
          <span style={{ color: INK_MUT, fontStyle: "italic" }}>No report generated yet.</span>
        )}
      </div>

      {/* Footer */}
      <div
        style={{
          padding: "10px 16px",
          background: "rgba(45,45,42,0.5)",
          border: `1px solid ${RIM}`,
          borderTop: "none",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span style={{ fontSize: "9px", color: INK_MUT, letterSpacing: "1.5px", fontFamily: "'DM Sans', sans-serif", textTransform: "uppercase" }}>
          {text.length} characters · {text.split("\n").length} lines
        </span>
        <span style={{ fontSize: "9px", color: `rgba(197,255,253,0.4)`, letterSpacing: "1px", fontFamily: "'DM Sans', sans-serif" }}>
          exHacker Report
        </span>
      </div>
    </div>
  );
}
