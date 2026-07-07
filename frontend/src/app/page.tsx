"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Navbar from "../components/layout/Navbar";

// ─── Data ─────────────────────────────────────────────────────────────────────
const PIPELINE = [
  { id: "01", name: "Challenge Analyst",     desc: "Extracts themes, constraints, and hidden opportunities." },
  { id: "02", name: "Research Specialist",   desc: "Scans competitors, APIs, OSS, winners, and trends." },
  { id: "03", name: "Competitor Analyst",    desc: "Identifies gaps, white space, and differentiation." },
  { id: "04", name: "Idea Generator",        desc: "Produces 5 distinct, fully scored concepts." },
  { id: "05", name: "Idea Selection",        desc: "You review and choose the winning concept.", isYou: true },
  { id: "06", name: "Solution Architect",    desc: "Designs complete technical architecture." },
  { id: "07", name: "Documentation Writer",  desc: "Generates PRD, README, API docs, and pitch." },
];

const STATS = [
  { num: "7", label: "AI Specialists", color: "var(--blue-light)" },
  { num: "5", label: "Generated Ideas", color: "var(--lime)" },
  { num: "10", label: "Doc Files", color: "var(--sky)" },
  { num: "∞", label: "Hackathons", color: "var(--text-2)" },
];

const TERMINAL_LINES = [
  { cls: "term-dim",  text: "# exHacker v3 — initialising pipeline" },
  { cls: "term-key",  text: "» session: hackathon-2026-07" },
  { cls: "",          text: "" },
  { cls: "term-run",  text: "▶  [01] Challenge Analyst       running…" },
  { cls: "term-done", text: "✔  [01] Challenge Analyst       done  (4.1s)" },
  { cls: "term-run",  text: "▶  [02] Research Specialist     running…" },
  { cls: "term-done", text: "✔  [02] Research Specialist     done  (3.8s)" },
  { cls: "term-run",  text: "▶  [03] Competitor Analyst      running…" },
  { cls: "term-done", text: "✔  [03] Competitor Analyst      done  (4.2s)" },
  { cls: "term-run",  text: "▶  [04] Idea Generator          running…" },
  { cls: "term-done", text: "✔  [04] Idea Generator          done  (6.2s)" },
  { cls: "term-val",  text: "   → 5 ideas generated · avg score 7.6/10" },
  { cls: "term-dim",  text: "⏸  [05] Idea Selection          YOUR TURN" },
];

const EXAMPLES = [
  "Build an AI-powered solution to improve financial literacy for college students",
  "Create a platform connecting underprivileged students with STEM mentors",
  "Design a tool to help small businesses manage inventory with computer vision",
];

// ─── Terminal animation ─────────────────────────────────────────────────────────
function Terminal() {
  const [count, setCount] = useState(0);
  const [blink, setBlink] = useState(true);
  useEffect(() => {
    const t = setInterval(() => setCount(n => n < TERMINAL_LINES.length ? n + 1 : n), 280);
    const b = setInterval(() => setBlink(v => !v), 530);
    return () => { clearInterval(t); clearInterval(b); };
  }, []);
  const visible = TERMINAL_LINES.slice(0, count);
  return (
    <div className="term-window anim-fade-up-3">
      <div className="term-bar">
        <div className="term-dot term-dot-r" /><div className="term-dot term-dot-y" /><div className="term-dot term-dot-g" />
        <span style={{ marginLeft: "auto", fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-3)", letterSpacing: "0.05em" }}>
          exhacker · agent-pipeline
        </span>
      </div>
      <div className="term-body" style={{ minHeight: "240px" }}>
        {visible.map((l, i) => (
          <div key={i} className={l.cls || ""} style={{ minHeight: "1.9em" }}>{l.text}</div>
        ))}
        {count < TERMINAL_LINES.length && (
          <span style={{ color: "var(--blue-light)", borderRight: `1px solid ${blink ? "var(--blue-light)" : "transparent"}`, paddingRight: "1px" }}>&nbsp;</span>
        )}
      </div>
    </div>
  );
}

// ─── FeatureCard ───────────────────────────────────────────────────────────────
function FeatureCard({ num, title, desc, color }: { num: string; title: string; desc: string; color: string }) {
  return (
    <div style={{ padding: "28px 0", borderBottom: "1px solid var(--border)", display: "flex", gap: "28px", alignItems: "flex-start" }}>
      <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-3)", minWidth: "24px", paddingTop: "5px" }}>{num}</span>
      <div style={{ flex: 1 }}>
        <p style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: "17px", color, marginBottom: "8px", letterSpacing: "-0.01em" }}>{title}</p>
        <p style={{ fontSize: "13px", color: "var(--text-2)", lineHeight: 1.65 }}>{desc}</p>
      </div>
    </div>
  );
}

// ─── Main Landing Page ─────────────────────────────────────────────────────────
export default function Home() {
  const router = useRouter();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreate = async () => {
    const idea = input.trim();
    if (!idea) { setError("Please describe your challenge."); return; }
    setError(null);
    setLoading(true);
    try {
      const { createProject } = await import("../services/api");
      const res = await createProject(idea);
      if (res.success) {
        router.push(`/projects/${res.data.project.id}?tab=challenge`);
      } else {
        setError(res.error?.message || "Failed to create project.");
      }
    } catch {
      setError("Something went wrong. Try again.");
    }
    setLoading(false);
  };

  return (
    <>
      <Navbar />
      <main style={{ background: "transparent" }}>

        {/* ══ HERO ════════════════════════════════════════════════════════════════ */}
        <section style={{ minHeight: "100vh", display: "flex", flexDirection: "column", paddingTop: "60px", position: "relative", overflow: "hidden", background: "transparent" }}>
          <div className="container" style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", padding: "80px 40px" }}>
            <div className="anim-fade-up" style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "40px", flexWrap: "wrap" }}>
              <span className="badge badge-blue">
                <span style={{ width: "5px", height: "5px", borderRadius: "50%", background: "var(--blue)", animation: "pulse 1.8s infinite" }} />
                AI-Powered Product Studio
              </span>
              <span className="badge">7 Specialists · Human-in-the-Loop</span>
            </div>

            <div className="anim-fade-up-1" style={{ marginBottom: "32px" }}>
              <h1 className="d1" style={{ color: "var(--text-1)", marginBottom: "0" }}>BUILD YOUR</h1>
              <h1 className="d1" style={{ marginBottom: "0" }}>
                <span className="grad-blue">HACKATHON</span>
              </h1>
              <h1 className="d1" style={{ color: "var(--text-1)" }}>IN MINUTES.</h1>
            </div>

            <p className="body-lg anim-fade-up-2" style={{ maxWidth: "520px", marginBottom: "44px" }}>
              Paste your challenge. Seven specialised AI agents research, analyse, and architect your complete strategy — while you stay in control of every decision.
            </p>

            {/* Creation form */}
            <div className="anim-fade-up-3" style={{ maxWidth: "560px", marginBottom: "64px" }}>
              <div style={{ display: "flex", gap: "8px", marginBottom: "12px" }}>
                <input
                  className="field"
                  value={input}
                  onChange={e => { setInput(e.target.value); setError(null); }}
                  onKeyDown={e => e.key === "Enter" && handleCreate()}
                  placeholder="Describe your hackathon challenge or idea..."
                  style={{ flex: 1, height: "48px", fontSize: "14px" }}
                />
                <button
                  onClick={handleCreate}
                  disabled={!input.trim() || loading}
                  className="btn btn-lime"
                  style={{ height: "48px", padding: "0 28px", fontSize: "14px", fontWeight: 700 }}
                >
                  {loading ? "Starting..." : "Start Free"}
                </button>
              </div>
              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                {EXAMPLES.map((ex, i) => (
                  <button key={i} onClick={() => setInput(ex)} className="chip" style={{ fontSize: "10px" }}>
                    Example {i + 1} ↗
                  </button>
                ))}
              </div>
              {error && (
                <div style={{ marginTop: "12px", padding: "10px 14px", background: "rgba(239,68,68,0.06)", border: "1px solid rgba(239,68,68,0.2)", color: "#fca5a5", fontSize: "13px", borderRadius: "4px", display: "flex", gap: "8px", alignItems: "center" }}>
                  <span>⚠</span><span>{error}</span>
                </div>
              )}
            </div>

            {/* Stats */}
            <div className="anim-fade-up-4" style={{ display: "flex", gap: "0", borderTop: "1px solid var(--border)" }}>
              {STATS.map((s, i) => (
                <div key={s.label} style={{ padding: "20px 0", paddingRight: "40px", marginRight: "40px", borderRight: i < STATS.length - 1 ? "1px solid var(--border)" : "none" }}>
                  <div style={{ fontFamily: "var(--font-display)", fontWeight: 800, fontSize: "28px", color: s.color, letterSpacing: "-0.02em", lineHeight: 1, marginBottom: "4px" }}>{s.num}</div>
                  <div style={{ fontSize: "10px", color: "var(--text-3)", letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 500 }}>{s.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ══ HOW IT WORKS ════════════════════════════════════════════════════════ */}
        <section style={{ borderTop: "1px solid var(--border)", padding: "100px 0", background: "rgba(14,14,14,0.82)", backdropFilter: "blur(2px)" }}>
          <div className="container">
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "80px", alignItems: "start", marginBottom: "72px" }}>
              <div>
                <span className="sec-num">[ 01 ] — PROCESS</span>
                <h2 className="d3" style={{ color: "var(--text-1)", marginBottom: "16px" }}>
                  Seven specialists.<br />
                  <span className="grad-blue">One winning strategy.</span>
                </h2>
                <p className="body-md" style={{ maxWidth: "360px" }}>
                  Each specialist runs asynchronously. You review and approve each output before the next specialist begins. No black boxes — every decision is explainable.
                </p>
              </div>
              <Terminal />
            </div>

            {/* Pipeline grid */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: "1px", background: "var(--border)" }}>
              {PIPELINE.map(s => (
                <div key={s.id} style={{
                  background: s.isYou ? "var(--blue-dim)" : "var(--surface-0)",
                  padding: "28px 24px", borderLeft: s.isYou ? "2px solid var(--blue)" : "2px solid transparent",
                  transition: "background 0.2s", cursor: "default",
                }}
                  onMouseEnter={e => { (e.currentTarget).style.background = s.isYou ? "var(--blue-dim)" : "var(--surface-1)"; }}
                  onMouseLeave={e => { (e.currentTarget).style.background = s.isYou ? "var(--blue-dim)" : "var(--surface-0)"; }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "10px" }}>
                    <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: s.isYou ? "var(--blue-light)" : "var(--text-3)", letterSpacing: "0.05em" }}>{s.id}</span>
                    {s.isYou && <span className="badge badge-blue" style={{ fontSize: "9px", padding: "2px 8px" }}>YOU</span>}
                  </div>
                  <p style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: "14px", color: "var(--text-1)", marginBottom: "8px", letterSpacing: "-0.01em" }}>{s.name}</p>
                  <p style={{ fontSize: "12px", color: "var(--text-2)", lineHeight: 1.6 }}>{s.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ══ OUTPUTS ═══════════════════════════════════════════════════════════ */}
        <section style={{ padding: "100px 0", borderTop: "1px solid var(--border)", background: "rgba(8,8,8,0.75)" }}>
          <div className="container">
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "80px", alignItems: "start" }}>
              <div>
                <span className="sec-num">[ 02 ] — OUTPUTS</span>
                <h2 className="d3" style={{ color: "var(--text-1)", marginBottom: "16px" }}>
                  Everything you need<br />
                  <span style={{ color: "var(--lime)" }}>to win.</span>
                </h2>
                <p className="body-md" style={{ marginBottom: "40px", maxWidth: "340px" }}>
                  From challenge analysis to a complete documentation package, every deliverable is generated, structured, and exportable.
                </p>
                <button onClick={() => document.getElementById("create-input")?.focus()} className="btn btn-primary" style={{ textDecoration: "none" }}>
                  Get Started Now <span>→</span>
                </button>
              </div>
              <div style={{ borderTop: "1px solid var(--border)" }}>
                {[
                  { num: "→", title: "5 Scored Ideas", desc: "Each scored across 8 dimensions with confidence and reasoning.", color: "var(--lime)" },
                  { num: "→", title: "Architecture Blueprint", desc: "Complete technical architecture with diagrams, API contracts, and trade-offs.", color: "var(--sky)" },
                  { num: "→", title: "10 Documentation Files", desc: "PRD, README, tech stack, API docs, database design, implementation plan, and pitch guide.", color: "var(--blue-light)" },
                  { num: "→", title: "Research Intelligence", desc: "10-category research with competitor analysis, trends, and technology recommendations.", color: "var(--lime)" },
                  { num: "→", title: "Decision Journal", desc: "Every meaningful decision tracked, explained, and auditable.", color: "var(--sky)" },
                ].map((f, i) => (
                  <FeatureCard key={i} num={f.num} title={f.title} desc={f.desc} color={f.color} />
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ══ FINAL CTA ════════════════════════════════════════════════════════ */}
        <section style={{ padding: "100px 0 120px", borderTop: "1px solid var(--border)", background: "rgba(14,14,14,0.80)", backdropFilter: "blur(2px)", textAlign: "center", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)", width: "600px", height: "600px", background: "radial-gradient(circle, rgba(61,124,246,0.06) 0%, transparent 65%)", pointerEvents: "none", borderRadius: "50%" }} />
          <div className="container" style={{ position: "relative", zIndex: 1 }}>
            <span className="sec-num" style={{ display: "block", textAlign: "center", marginBottom: "24px" }}>[ 03 ] — GET STARTED</span>
            <h2 className="d2" style={{ color: "var(--text-1)", marginBottom: "20px" }}>Your next hackathon</h2>
            <h2 className="d2" style={{ marginBottom: "32px" }}>
              <span className="grad-blue">starts here.</span>
            </h2>
            <p className="body-md" style={{ marginBottom: "40px", maxWidth: "440px", margin: "0 auto 40px" }}>
              No account needed. Paste your challenge and let the specialists work. You will have a complete strategy in under 3 minutes.
            </p>
            <div style={{ display: "flex", gap: "12px", justifyContent: "center", flexWrap: "wrap" }}>
              <input
                id="create-input"
                className="field"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Describe your hackathon idea..."
                style={{ maxWidth: "420px" }}
                onKeyDown={e => e.key === "Enter" && handleCreate()}
              />
              <button onClick={handleCreate} disabled={!input.trim()} className="btn btn-lime" style={{ padding: "13px 28px", fontSize: "13px", fontWeight: 700 }}>
                Build My Strategy <span>→</span>
              </button>
            </div>
          </div>
        </section>

        {/* ══ Footer ════════════════════════════════════════════════════════════ */}
        <footer style={{ borderTop: "1px solid var(--border)", padding: "28px 0", background: "rgba(8,8,8,0.90)" }}>
          <div className="container" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "12px" }}>
            <span style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: "13px", color: "var(--text-3)" }}>exHacker</span>
            <span style={{ fontSize: "11px", color: "var(--text-3)" }}>AI-Powered Strategy · 7 Specialists · Open Source</span>
          </div>
        </footer>

      </main>
    </>
  );
}
