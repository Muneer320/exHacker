"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { Pill, LoadingState } from "@/components/shared/ui";
import MarkdownRenderer from "@/components/markdown/MarkdownRenderer";

const API_BASE_URL = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
  ? 'https://exhacker-backend.vercel.app/api/v1'
  : 'http://localhost:8000/api/v1';

const FILE_ORDER = [
  { file: "README.md",             label: "README",            icon: "◈" },
  { file: "PRD.md",               label: "PRD",               icon: "☰" },
  { file: "ARCHITECTURE.md",      label: "Architecture",      icon: "▣" },
  { file: "API.md",               label: "API",               icon: "◎" },
  { file: "DATABASE.md",          label: "Database",          icon: "◇" },
  { file: "TECH_STACK.md",        label: "Tech Stack",        icon: "✦" },
  { file: "FRONTEND.md",          label: "Frontend",          icon: "⊕" },
  { file: "BACKEND.md",           label: "Backend",           icon: "⊞" },
  { file: "IMPLEMENTATION_PLAN.md", label: "Plan",            icon: "◈" },
  { file: "PITCH.md",             label: "Pitch",             icon: "◆" },
];

export default function DocsPage() {
  const params = useParams();
  const projectId = params.id as string;
  const [docs, setDocs] = useState<Record<string, string>>({});
  const [activeFile, setActiveFile] = useState("README.md");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!projectId) return;
    setLoading(true);
    Promise.all(FILE_ORDER.map(async ({ file }) => {
      try {
        const res = await fetch(`${API_BASE_URL}/projects/${projectId}/docs/${file}`);
        if (res.ok) return { file, content: await res.text() };
      } catch {}
      return { file, content: "" };
    })).then(results => {
      const map: Record<string, string> = {};
      results.forEach(r => { if (r.content) map[r.file] = r.content; });
      setDocs(map);
      setLoading(false);
    });
  }, [projectId]);

  const activeContent = docs[activeFile];
  const docMeta = FILE_ORDER.find(f => f.file === activeFile);

  if (loading) return <LoadingState label="Loading documentation..." />;

  return (
    <div style={{ display: "flex", gap: "0", height: "calc(100vh - 180px)", border: "1px solid var(--border)", borderRadius: "var(--r-md)", overflow: "hidden" }}>
      {/* Sidebar */}
      <div style={{ width: "200px", borderRight: "1px solid var(--border)", overflow: "auto", flexShrink: 0 }}>
        <div style={{ padding: "12px 14px", borderBottom: "1px solid var(--border)", fontSize: "11px", fontWeight: 600, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Files
        </div>
        {FILE_ORDER.map(({ file, label, icon }) => {
          const hasContent = !!docs[file];
          return (
            <button
              key={file}
              onClick={() => setActiveFile(file)}
              disabled={!hasContent}
              style={{
                display: "flex", alignItems: "center", gap: "8px", width: "100%", padding: "8px 14px",
                fontSize: "12px", color: activeFile === file ? "var(--blue-light)" : hasContent ? "var(--text-2)" : "var(--text-3)",
                background: activeFile === file ? "var(--blue-dim)" : "transparent",
                border: "none", cursor: hasContent ? "pointer" : "default", textAlign: "left",
                borderLeft: activeFile === file ? "2px solid var(--blue)" : "2px solid transparent",
              }}
            >
              <span style={{ fontSize: "11px" }}>{icon}</span>
              <span style={{ flex: 1 }}>{label}</span>
              {!hasContent && <span style={{ fontSize: "9px", color: "var(--text-3)" }}>—</span>}
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: "auto", padding: "24px" }}>
        {docMeta && (
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px", paddingBottom: "12px", borderBottom: "1px solid var(--border)" }}>
            <span style={{ fontSize: "12px" }}>{docMeta.icon}</span>
            <h3 style={{ fontSize: "15px", fontWeight: 700, color: "var(--text-1)" }}>{docMeta.label}</h3>
            <div style={{ flex: 1 }} />
            {activeContent && (
              <button
                onClick={() => {
                  const blob = new Blob([activeContent], { type: "text/markdown" });
                  const a = document.createElement("a");
                  a.href = URL.createObjectURL(blob);
                  a.download = activeFile;
                  a.click();
                }}
                className="btn btn-ghost"
                style={{ fontSize: "10px", padding: "4px 10px" }}
              >
                Download
              </button>
            )}
          </div>
        )}
        {activeContent ? (
          <MarkdownRenderer content={activeContent} />
        ) : (
          <div style={{ padding: "40px", textAlign: "center", color: "var(--text-3)" }}>
            <p>No content available for this document.</p>
            <p style={{ fontSize: "11px", marginTop: "8px" }}>Generate documentation from the challenge page first.</p>
          </div>
        )}
      </div>
    </div>
  );
}
