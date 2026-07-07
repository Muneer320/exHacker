"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { Pill, LoadingState } from "@/components/shared/ui";
import MarkdownRenderer from "@/components/markdown/MarkdownRenderer";

const FILE_ORDER = [
  { file: "README.md", label: "README", icon: "📖" },
  { file: "PRD.md", label: "PRD", icon: "📋" },
  { file: "ARCHITECTURE.md", label: "Architecture", icon: "🏗️" },
  { file: "API.md", label: "API", icon: "🔌" },
  { file: "DATABASE.md", label: "Database", icon: "🗄️" },
  { file: "TECH_STACK.md", label: "Tech Stack", icon: "⚙️" },
  { file: "FRONTEND.md", label: "Frontend", icon: "🎨" },
  { file: "BACKEND.md", label: "Backend", icon: "🖥️" },
  { file: "IMPLEMENTATION_PLAN.md", label: "Plan", icon: "📅" },
  { file: "PITCH.md", label: "Pitch", icon: "🎤" },
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
        const res = await fetch(`/api/v1/projects/${projectId}/docs/${file}`);
        if (res.ok) return { file, content: await res.text() };
      } catch {}
      return { file, content: "" };
    })).then(results => {
      const map: Record<string, string> = {};
      results.forEach(r => { if (r.content) map[r.file] = r.content; });
      setDocs(map);
    }).finally(() => setLoading(false));
  }, [projectId]);

  if (loading) return <LoadingState label="Loading documentation..." />;

  const activeContent = docs[activeFile];
  const fileMeta = FILE_ORDER.find(f => f.file === activeFile);

  return (
    <div>
      <div className="anim-fade-up" style={{ marginBottom: "16px" }}>
        <span className="sec-num">[ DOCS ]</span>
        <h2 className="d4" style={{ color: "var(--text-1)", marginBottom: "4px" }}>Documentation</h2>
        <p className="body-sm">{Object.keys(docs).length} files generated</p>
      </div>

      <div style={{ display: "flex", gap: "0", border: "1px solid var(--border)", borderRadius: "var(--r-md)", overflow: "hidden" }}>
        {/* Sidebar */}
        <div style={{ width: "200px", minWidth: "200px", borderRight: "1px solid var(--border)", background: "var(--surface-0)" }}>
          {FILE_ORDER.map(({ file, label, icon }) => {
            const hasContent = !!docs[file];
            const isActive = activeFile === file;
            return (
              <button key={file} onClick={() => hasContent && setActiveFile(file)} disabled={!hasContent} style={{
                display: "flex", alignItems: "center", gap: "8px", width: "100%", padding: "10px 14px",
                fontSize: "12px", fontWeight: isActive ? 600 : 400, textAlign: "left",
                color: !hasContent ? "var(--text-3)" : isActive ? "var(--blue-light)" : "var(--text-2)",
                background: isActive ? "var(--blue-dim)" : "transparent",
                border: "none", borderLeft: isActive ? "2px solid var(--blue)" : "2px solid transparent",
                cursor: hasContent ? "pointer" : "default", transition: "all 0.1s",
              }}>
                <span style={{ fontSize: "12px", opacity: hasContent ? 1 : 0.4 }}>{icon}</span>
                <span style={{ flex: 1 }}>{label}</span>
                {hasContent && <span style={{ fontSize: "8px", color: "var(--lime)" }}>✓</span>}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* Toolbar */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px", padding: "8px 14px", borderBottom: "1px solid var(--border)", background: "var(--surface-0)" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-1)" }}>{fileMeta?.label || activeFile}</span>
            <div style={{ flex: 1 }} />
            {activeContent && (
              <>
                <button className="btn btn-ghost" style={{ padding: "4px 10px", fontSize: "10px" }} onClick={() => { navigator.clipboard.writeText(activeContent); }}>📋 Copy</button>
                <button className="btn btn-ghost" style={{ padding: "4px 10px", fontSize: "10px" }} onClick={() => { const b = new Blob([activeContent], { type: "text/markdown" }); const a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = activeFile; a.click(); }}>⬇ Download</button>
              </>
            )}
          </div>

          {/* Markdown renderer */}
          <div style={{ padding: "24px", overflow: "auto", maxHeight: "70vh" }}>
            {activeContent ? (
              <MarkdownRenderer content={activeContent} />
            ) : (
              <div style={{ textAlign: "center", padding: "48px", color: "var(--text-3)", fontSize: "13px" }}>
                This document hasn't been generated yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
