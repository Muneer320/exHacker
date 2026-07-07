"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import type { Components } from "react-markdown";
import { useMemo } from "react";
import MermaidViewer from "@/components/diagrams/MermaidViewer";

// ─── Components ───────────────────────────────────────────────────────────────

const components: Components = {
  h1: ({ children, ...props }) => (
    <h1 {...props} style={{ fontSize: "22px", fontWeight: 700, color: "var(--text-1)", margin: "20px 0 8px", fontFamily: "var(--font-display)", letterSpacing: "-0.02em", borderBottom: "1px solid var(--border)", paddingBottom: "8px" }}>
      {children}
    </h1>
  ),
  h2: ({ children, ...props }) => (
    <h2 {...props} style={{ fontSize: "17px", fontWeight: 600, color: "var(--text-1)", margin: "16px 0 6px", fontFamily: "var(--font-display)", letterSpacing: "-0.01em" }}>
      {children}
    </h2>
  ),
  h3: ({ children, ...props }) => (
    <h3 {...props} style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-1)", margin: "14px 0 4px" }}>
      {children}
    </h3>
  ),
  p: ({ children }) => (
    <p style={{ fontSize: "13px", color: "var(--text-2)", lineHeight: 1.7, margin: "6px 0" }}>{children}</p>
  ),
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noopener noreferrer" style={{ color: "var(--blue-light)", textDecoration: "underline", textUnderlineOffset: "2px" }}>
      {children} ↗
    </a>
  ),
  ul: ({ children }) => (
    <ul style={{ margin: "6px 0", paddingLeft: "20px", listStyle: "disc", color: "var(--text-2)", fontSize: "13px", lineHeight: 1.7 }}>{children}</ul>
  ),
  ol: ({ children }) => (
    <ol style={{ margin: "6px 0", paddingLeft: "20px", color: "var(--text-2)", fontSize: "13px", lineHeight: 1.7, listStyle: "decimal" }}>{children}</ol>
  ),
  li: ({ children }) => <li style={{ margin: "2px 0" }}>{children}</li>,
  blockquote: ({ children }) => (
    <blockquote style={{ borderLeft: "2px solid var(--blue)", padding: "8px 16px", margin: "10px 0", background: "var(--surface-1)", fontSize: "13px", color: "var(--text-2)", lineHeight: 1.6 }}>
      {children}
    </blockquote>
  ),
  hr: () => <hr style={{ border: "none", borderTop: "1px solid var(--border)", margin: "20px 0" }} />,
  table: ({ children }) => (
    <div style={{ overflowX: "auto", margin: "12px 0" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead style={{ borderBottom: "2px solid var(--blue)" }}>{children}</thead>,
  th: ({ children }) => <th style={{ padding: "6px 10px", textAlign: "left", fontWeight: 700, color: "var(--blue-light)", whiteSpace: "nowrap" }}>{children}</th>,
  td: ({ children }) => <td style={{ padding: "6px 10px", borderTop: "1px solid var(--border)", color: "var(--text-2)" }}>{children}</td>,
  img: ({ src, alt }) => (
    <img src={src} alt={alt || ""} style={{ maxWidth: "100%", borderRadius: "4px", margin: "12px 0" }} loading="lazy" />
  ),
  input: ({ checked, type }) => {
    if (type === "checkbox") {
      return (
        <span style={{ color: checked ? "var(--lime)" : "var(--text-3)", marginRight: "6px", fontSize: "14px" }}>
          {checked ? "☑" : "☐"}
        </span>
      );
    }
    return null;
  },
  pre: ({ children }) => <>{children}</>,
  code({ className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || "");
    const codeString = String(children).replace(/\n$/, "");

    // Handle mermaid code blocks inline
    if (match && match[1] === "mermaid") {
      return <MermaidViewer code={codeString} title="mermaid" />;
    }

    if (match) {
      return (
        <div style={{ margin: "12px 0", borderRadius: "4px", overflow: "hidden", fontSize: "12px", position: "relative" }}>
          <div style={{ display: "flex", alignItems: "center", padding: "4px 10px", background: "#1e1e1e", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
            <span style={{ fontSize: "10px", color: "var(--text-3)" }}>{match[1]}</span>
            <button
              onClick={() => navigator.clipboard.writeText(codeString)}
              style={{ marginLeft: "auto", background: "transparent", border: "none", color: "var(--text-3)", fontSize: "10px", cursor: "pointer", padding: "2px 6px" }}
            >
              Copy
            </button>
          </div>
          <SyntaxHighlighter
            style={oneDark}
            language={match[1]}
            PreTag="div"
            customStyle={{ margin: 0, borderRadius: 0, padding: "14px", fontSize: "12px", lineHeight: 1.6 }}
          >
            {codeString}
          </SyntaxHighlighter>
        </div>
      );
    }

    // Inline code
    return (
      <code style={{ fontFamily: "var(--font-mono)", fontSize: "11px", background: "var(--surface-2)", padding: "1px 5px", borderRadius: "2px", color: "var(--lime)" }} {...props}>
        {children}
      </code>
    );
  },
};

// ─── Main Component ───────────────────────────────────────────────────────────

export default function MarkdownRenderer({ content, className }: { content: string; className?: string }) {
  const body = useMemo(() => {
    if (!content) return "";
    // Skip files that contain "not found" or "No content"
    if (content.trim().toLowerCase().startsWith("# not found")) return "";
    return content;
  }, [content]);

  if (!body) {
    return (
      <div style={{ textAlign: "center", padding: "48px", color: "var(--text-3)", fontSize: "13px" }}>
        Document not available.
      </div>
    );
  }

  return (
    <div className={className} style={{ maxWidth: "100%", overflow: "hidden" }}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {body}
      </ReactMarkdown>
    </div>
  );
}
