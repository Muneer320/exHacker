"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { Pill, LoadingState } from "@/components/shared/ui";

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

// ─── Simple Markdown Renderer ─────────────────────────────────────────────────

function MarkdownRenderer({ content }: { content: string }) {
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let inCodeBlock = false;
  let codeLines: string[] = [];
  let codeLang = "";

  const flushCode = () => {
    if (codeLines.length > 0) {
      elements.push(
        <div key={`code-${elements.length}`} style={{ background: "var(--surface-0)", borderRadius: "var(--r-sm)", margin: "12px 0", overflow: "auto", fontFamily: "var(--font-mono)", fontSize: "12px", lineHeight: 1.6 }}>
          <div className="term-bar" style={{ padding: "4px 10px" }}><span className="term-dot term-dot-r" /><span className="term-dot term-dot-y" /><span className="term-dot term-dot-g" /><span style={{ marginLeft: "auto", fontSize: "9px", color: "var(--text-3)" }}>{codeLang || "code"}</span></div>
          <pre style={{ padding: "14px", whiteSpace: "pre" }}>{codeLines.map((l, i) => <div key={i} style={{ color: "var(--text-2)" }}>{l}</div>)}</pre>
        </div>
      );
      codeLines = [];
      codeLang = "";
    }
  };

  lines.forEach((line, idx) => {
    // Code blocks
    if (line.startsWith("```")) {
      if (inCodeBlock) { inCodeBlock = false; flushCode(); return; }
      inCodeBlock = true;
      codeLang = line.slice(3).trim();
      return;
    }
    if (inCodeBlock) { codeLines.push(line); return; }

    const key = `l-${idx}`;

    // Headings
    if (line.startsWith("# ")) { elements.push(<h1 key={key} style={{ fontSize: "22px", fontWeight: 700, color: "var(--text-1)", margin: "16px 0 8px", fontFamily: "var(--font-display)", letterSpacing: "-0.02em" }}>{line.slice(2)}</h1>); return; }
    if (line.startsWith("## ")) { elements.push(<h2 key={key} style={{ fontSize: "17px", fontWeight: 600, color: "var(--text-1)", margin: "14px 0 6px", fontFamily: "var(--font-display)", letterSpacing: "-0.01em" }}>{line.slice(3)}</h2>); return; }
    if (line.startsWith("### ")) { elements.push(<h3 key={key} style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-1)", margin: "12px 0 4px" }}>{line.slice(4)}</h3>); return; }

    // Table
    if (line.startsWith("|")) {
      if (line.includes("---")) return; // Skip separator rows
      const cells = line.split("|").filter(c => c.trim());
      const isHeader = lines[idx + 1]?.includes("---");
      if (isHeader) {
        elements.push(
          <div key={key} style={{ display: "flex", gap: "16px", padding: "6px 0", borderBottom: "2px solid var(--blue)", marginTop: "8px" }}>
            {cells.map((c, i) => <div key={i} style={{ flex: 1, fontSize: "11px", fontWeight: 700, color: "var(--blue-light)" }}>{c.trim()}</div>)}
          </div>
        );
      } else {
        elements.push(
          <div key={key} style={{ display: "flex", gap: "16px", padding: "4px 0", borderBottom: "1px solid var(--border)" }}>
            {cells.map((c, i) => <div key={i} style={{ flex: 1, fontSize: "11px", color: "var(--text-2)" }}>{c.trim()}</div>)}
          </div>
        );
      }
      return;
    }

    // Blockquote
    if (line.startsWith("> ")) {
      elements.push(<blockquote key={key} style={{ borderLeft: "2px solid var(--blue)", padding: "8px 14px", margin: "8px 0", background: "var(--surface-1)", fontSize: "12px", color: "var(--text-2)", lineHeight: 1.6 }}>{renderInline(line.slice(2))}</blockquote>);
      return;
    }

    // List items
    if (line.startsWith("- ") || line.startsWith("* ")) {
      elements.push(<div key={key} style={{ display: "flex", gap: "8px", padding: "1px 0", fontSize: "12px", color: "var(--text-2)", lineHeight: 1.6 }}><span style={{ color: "var(--blue-light)" }}>·</span><span>{renderInline(line.slice(2))}</span></div>);
      return;
    }
    if (/^\d+\. /.test(line)) {
      const match = line.match(/^(\d+)\. (.+)/);
      if (match) {
        elements.push(<div key={key} style={{ display: "flex", gap: "8px", padding: "1px 0", fontSize: "12px", color: "var(--text-2)", lineHeight: 1.6 }}><span style={{ color: "var(--blue-light)", minWidth: "16px", fontFamily: "var(--font-mono)" }}>{match[1]}.</span><span>{renderInline(match[2])}</span></div>);
        return;
      }
    }

    // Horizontal rule
    if (line.startsWith("---") || line.startsWith("***")) {
      elements.push(<hr key={key} style={{ border: "none", borderTop: "1px solid var(--border)", margin: "16px 0" }} />);
      return;
    }

    // Empty line
    if (line.trim() === "") { elements.push(<div key={key} style={{ height: "8px" }} />); return; }

    // Paragraph
    elements.push(<p key={key} style={{ fontSize: "13px", color: "var(--text-2)", lineHeight: 1.7, margin: "4px 0" }}>{renderInline(line)}</p>);
  });

  // Flush remaining code block
  if (inCodeBlock) flushCode();

  return <div>{elements}</div>;
}

// ─── Inline Markdown ─────────────────────────────────────────────────────────

function renderInline(text: string): React.ReactNode {
  // Bold + inline code
  const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) return <strong key={i} style={{ fontWeight: 700, color: "var(--text-1)" }}>{part.slice(2, -2)}</strong>;
    if (part.startsWith("`") && part.endsWith("`")) return <code key={i} style={{ fontFamily: "var(--font-mono)", fontSize: "11px", background: "var(--surface-2)", padding: "1px 4px", borderRadius: "2px", color: "var(--lime)" }}>{part.slice(1, -1)}</code>;
    return part;
  });
}
