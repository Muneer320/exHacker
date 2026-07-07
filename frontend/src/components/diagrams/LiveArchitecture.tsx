"use client";

import { useState, useEffect, useRef } from "react";
import MermaidViewer from "@/components/diagrams/MermaidViewer";

interface LiveArchProps {
  /** Full architecture data from S7 */
  arch: any;
  /** Whether to auto-play the evolution animation */
  autoPlay?: boolean;
}

interface ArchComponent {
  name: string;
  tech: string;
  purpose: string;
  mermaidId: string;
}

// ─── Live Architecture Evolution ──────────────────────────────────────────────

export default function LiveArchitecture({ arch, autoPlay = true }: LiveArchProps) {
  const [visibleComponents, setVisibleComponents] = useState<Set<string>>(new Set());
  const [phase, setPhase] = useState<"idle" | "building" | "complete">(autoPlay ? "building" : "idle");
  const [activePhase, setActivePhase] = useState(0);
  const phasesRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  // Components from the architecture data
  const components: ArchComponent[] = (arch?.components || []).map((c: any, i: number) => ({
    name: c.name || `Component ${i + 1}`,
    tech: c.tech || c.framework || "",
    purpose: c.purpose || c.description || "",
    mermaidId: `comp-${i}`,
  }));

  const hasMermaid = !!(arch?.mermaid_system || arch?.mermaid_request_flow || arch?.mermaid_data_flow || arch?.mermaid_deployment);
  const buildPhases = [
    { label: "Frontend", description: "Setting up the user interface layer...", components: components.filter(c => c.tech?.toLowerCase().includes("next") || c.tech?.toLowerCase().includes("react") || c.tech?.toLowerCase().includes("vue") || c.name?.toLowerCase().includes("frontend") || c.name?.toLowerCase().includes("ui") || c.name?.toLowerCase().includes("web")) },
    { label: "Backend", description: "Connecting the API layer...", components: components.filter(c => c.tech?.toLowerCase().includes("api") || c.tech?.toLowerCase().includes("fastapi") || c.tech?.toLowerCase().includes("express") || c.tech?.toLowerCase().includes("backend") || c.name?.toLowerCase().includes("server") || c.name?.toLowerCase().includes("api")) },
    { label: "Database", description: "Designing data storage...", components: components.filter(c => c.tech?.toLowerCase().includes("db") || c.tech?.toLowerCase().includes("sql") || c.tech?.toLowerCase().includes("postgres") || c.tech?.toLowerCase().includes("mongo") || c.name?.toLowerCase().includes("database") || c.name?.toLowerCase().includes("data") || c.name?.toLowerCase().includes("storage")) },
    { label: "Infrastructure", description: "Connecting services and deployment...", components: components.filter(c => !c.name?.toLowerCase().includes("frontend") && !c.name?.toLowerCase().includes("backend") && !c.name?.toLowerCase().includes("database") && !c.name?.toLowerCase().includes("data")) },
  ];

  // Non-empty phases
  const activePhases = buildPhases.filter(p => p.components.length > 0 || (activePhase < 4 && phase === "building"));

  useEffect(() => {
    if (phase !== "building") return;
    const timers: ReturnType<typeof setTimeout>[] = [];

    // Reveal phases one by one
    activePhases.forEach((p, pi) => {
      const timer = setTimeout(() => {
        setActivePhase(pi + 1);
        p.components.forEach((c) => {
          setVisibleComponents(prev => new Set(prev).add(c.name));
        });
        if (pi === activePhases.length - 1) {
          setTimeout(() => setPhase("complete"), 500);
        }
      }, (pi + 1) * 1200);
      timers.push(timer);
    });

    phasesRef.current = timers;
    return () => timers.forEach(t => clearTimeout(t));
  }, [phase]); // eslint-disable-line react-hooks/exhaustive-deps

  const startEvolution = () => {
    setVisibleComponents(new Set());
    setActivePhase(0);
    setPhase("building");
  };

  return (
    <div>
      {/* Phase progression */}
      {phase === "building" && (
        <div style={{ marginBottom: "16px" }}>
          <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
            {activePhases.map((p, i) => (
              <div key={p.label} style={{
                flex: 1, padding: "6px 8px", borderRadius: "var(--r-sm)", textAlign: "center",
                background: i < activePhase ? "rgba(194,255,77,0.08)" : i === activePhase ? "var(--blue-dim)" : "var(--surface-1)",
                border: `1px solid ${i < activePhase ? "rgba(194,255,77,0.2)" : i === activePhase ? "var(--blue)" : "var(--border)"}`,
                transition: "all 0.3s",
              }}>
                <div style={{ fontSize: "10px", fontWeight: 600, color: i < activePhase ? "var(--lime)" : i === activePhase ? "var(--blue-light)" : "var(--text-3)" }}>
                  {p.label}
                </div>
                <div style={{ fontSize: "8px", color: "var(--text-3)", marginTop: "2px" }}>{p.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System diagram — always visible, grows */}
      {hasMermaid && (
        <div style={{
          opacity: phase === "complete" ? 1 : phase === "building" ? 0.6 : 0.8,
          transition: "opacity 0.5s",
        }}>
          <MermaidViewer code={arch.mermaid_system} title="system architecture" />
        </div>
      )}

      {/* Components grid — reveals one by one */}
      {phase !== "idle" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "8px", marginTop: "16px" }}>
          {components.map((c, i) => {
            const isVisible = visibleComponents.has(c.name);
            return (
              <div key={c.name} style={{
                padding: "14px", background: "var(--surface-1)", borderRadius: "var(--r-md)",
                border: "1px solid var(--border)",
                opacity: isVisible ? 1 : 0,
                transform: isVisible ? "translateY(0)" : "translateY(10px)",
                transition: `all 0.4s ${i * 0.1}s ease`,
                pointerEvents: isVisible ? "auto" : "none",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px" }}>
                  <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--blue)" }} />
                  <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-1)" }}>{c.name}</span>
                </div>
                {c.tech && <span style={{ fontSize: "10px", color: "var(--blue-light)", fontFamily: "var(--font-mono)" }}>{c.tech}</span>}
                <p style={{ fontSize: "10px", color: "var(--text-3)", marginTop: "4px", lineHeight: 1.4 }}>{c.purpose}</p>
              </div>
            );
          })}
        </div>
      )}

      {/* Completion celebration */}
      {phase === "complete" && (
        <div className="anim-fade-up" style={{ textAlign: "center", padding: "20px", marginTop: "8px" }}>
          <span style={{ fontSize: "11px", color: "var(--lime)", fontWeight: 600 }}>✓ Architecture complete · {components.length} components · Ready for documentation</span>
        </div>
      )}

      {/* Trigger button for idle state */}
      {phase === "idle" && (
        <div style={{ textAlign: "center", padding: "24px" }}>
          <button onClick={startEvolution} className="btn btn-primary">
            ▶ Build Architecture
          </button>
        </div>
      )}
    </div>
  );
}
