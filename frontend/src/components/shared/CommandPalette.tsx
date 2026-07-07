"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";

interface CmdItem {
  id: string;
  label: string;
  description: string;
  icon: string;
  shortcut?: string;
  action: () => void;
}

export default function CommandPalette({ projectId }: { projectId?: string }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedIdx, setSelectedIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const base = projectId ? `/projects/${projectId}` : "";

  const allItems: CmdItem[] = [
    ...(projectId ? [
      { id: "overview", label: "Go to Overview", description: "Project overview and status", icon: "◈", action: () => router.push(`${base}/overview`) },
      { id: "challenge", label: "Go to Challenge", description: "Challenge intelligence", icon: "🧠", action: () => router.push(`${base}/challenge`) },
      { id: "research", label: "Go to Research", description: "Research dashboard", icon: "🔍", action: () => router.push(`${base}/research`) },
      { id: "competitors", label: "Go to Competitors", description: "Competitor analysis", icon: "🎯", action: () => router.push(`${base}/competitors`) },
      { id: "ideas", label: "Go to Ideas", description: "Idea selection", icon: "💡", action: () => router.push(`${base}/ideas`) },
      { id: "architecture", label: "Go to Architecture", description: "Architecture blueprint", icon: "🏗️", action: () => router.push(`${base}/architecture`) },
      { id: "docs", label: "Go to Documentation", description: "Documentation files", icon: "📝", action: () => router.push(`${base}/docs`) },
      { id: "timeline", label: "Go to Timeline", description: "Decision timeline", icon: "⏱", action: () => router.push(`${base}/timeline`) },
      { id: "exports", label: "Go to Exports", description: "Export package", icon: "📦", action: () => router.push(`${base}/exports`) },
      { id: "projects", label: "Back to Projects", description: "All projects list", icon: "📋", action: () => router.push("/projects") },
    ] : [
      { id: "home", label: "Go to Home", description: "Landing page", icon: "🏠", action: () => router.push("/") },
      { id: "projects", label: "Go to Projects", description: "All projects", icon: "📋", action: () => router.push("/projects") },
    ]),
  ];

  const filtered = query.trim()
    ? allItems.filter(item =>
        item.label.toLowerCase().includes(query.toLowerCase()) ||
        item.description.toLowerCase().includes(query.toLowerCase())
      )
    : allItems;

  // Toggle with Ctrl+K / Cmd+K
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen(o => !o);
      }
      if (e.key === "Escape" && open) {
        setOpen(false);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open]);

  // Focus input when opened
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setQuery("");
      setSelectedIdx(0);
    }
  }, [open]);

  const execute = useCallback((item: CmdItem) => {
    setOpen(false);
    item.action();
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") { e.preventDefault(); setSelectedIdx(i => Math.min(i + 1, filtered.length - 1)); }
    if (e.key === "ArrowUp") { e.preventDefault(); setSelectedIdx(i => Math.max(i - 1, 0)); }
    if (e.key === "Enter" && filtered[selectedIdx]) { execute(filtered[selectedIdx]); }
  };

  if (!open) return null;

  return (
    <>
      {/* Overlay */}
      <div
        style={{ position: "fixed", inset: 0, zIndex: 999, background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)" }}
        onClick={() => setOpen(false)}
      />

      {/* Palette */}
      <div className="anim-fade-up" style={{
        position: "fixed", top: "15%", left: "50%", transform: "translateX(-50%)",
        zIndex: 1000, width: "520px", maxWidth: "90vw",
        background: "var(--surface-1)", border: "1px solid var(--border-mid)",
        borderRadius: "var(--r-lg)", boxShadow: "0 24px 80px rgba(0,0,0,0.5)",
        overflow: "hidden",
      }}>
        {/* Search */}
        <div style={{ padding: "12px 16px", borderBottom: "1px solid var(--border)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "14px", color: "var(--text-3)" }}>⌘</span>
            <input
              ref={inputRef}
              value={query}
              onChange={e => { setQuery(e.target.value); setSelectedIdx(0); }}
              onKeyDown={handleKeyDown}
              placeholder="Type a command or search..."
              style={{
                flex: 1, background: "transparent", border: "none", outline: "none",
                color: "var(--text-1)", fontSize: "14px", fontFamily: "var(--font-body)",
              }}
            />
            <button
              onClick={() => setOpen(false)}
              style={{ background: "var(--surface-2)", border: "1px solid var(--border-mid)", borderRadius: "var(--r-sm)", padding: "2px 6px", fontSize: "10px", color: "var(--text-3)", cursor: "pointer" }}
            >
              ESC
            </button>
          </div>
        </div>

        {/* Results */}
        <div style={{ maxHeight: "300px", overflow: "auto", padding: "4px" }}>
          {filtered.length === 0 && (
            <div style={{ padding: "20px", textAlign: "center", color: "var(--text-3)", fontSize: "13px" }}>
              No results for "{query}"
            </div>
          )}
          {filtered.map((item, i) => (
            <div
              key={item.id}
              onClick={() => execute(item)}
              style={{
                display: "flex", alignItems: "center", gap: "10px",
                padding: "8px 12px", borderRadius: "var(--r-sm)", cursor: "pointer",
                background: i === selectedIdx ? "var(--blue-dim)" : "transparent",
                transition: "background 0.1s",
              }}
              onMouseEnter={() => setSelectedIdx(i)}
            >
              <span style={{ fontSize: "16px", width: "24px", textAlign: "center" }}>{item.icon}</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: "13px", fontWeight: 500, color: "var(--text-1)" }}>{item.label}</div>
                <div style={{ fontSize: "11px", color: "var(--text-3)" }}>{item.description}</div>
              </div>
              {item.shortcut && (
                <span style={{ fontSize: "10px", color: "var(--text-3)", fontFamily: "var(--font-mono)", padding: "2px 5px", background: "var(--surface-2)", borderRadius: "2px" }}>
                  {item.shortcut}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
