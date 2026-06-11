"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Navbar from "../../components/Navbar";
import { startWorkflow } from "../../lib/api";
import { CompletedStep } from "../../types/project";

// ─── Data ─────────────────────────────────────────────────────────────────────
const TRACKS   = ["AI / ML","Healthcare","Education","Sustainability","FinTech","Web3","Social Impact","Productivity","Climate","Accessibility"];
const SPONSORS = ["Google","Microsoft","OpenAI","AWS","Meta","Stripe","Vercel","MongoDB","Anthropic","Nvidia"];
const EXAMPLES = [
  "Build an AI-powered solution to reduce food waste in urban communities",
  "Create a platform connecting underprivileged students with STEM mentors",
  "Design a tool to help small businesses manage inventory with computer vision",
];
const PIPELINE = [
  { id:"01", name:"Problem Analyst",    desc:"Breaks down the challenge" },
  { id:"02", name:"Opportunity Planner",desc:"Maps market gaps" },
  { id:"03", name:"Idea Generator",     desc:"Creates 10 concepts" },
  { id:"04", name:"Idea Validator",     desc:"Scores all ideas" },
  { id:"05", name:"Idea Selection",     desc:"You choose the winner", isYou:true },
  { id:"06", name:"Solution Architect", desc:"Full blueprint" },
  { id:"07", name:"Presentation Agent",desc:"10-slide deck" },
  { id:"08", name:"Pitch Agent",        desc:"3 pitch scripts" },
  { id:"09", name:"Report Generator",   desc:"Final report" },
];

function toggle<T>(arr: T[], val: T): T[] {
  return arr.includes(val) ? arr.filter(x => x !== val) : [...arr, val];
}
function buildList(sel: string[], text: string): string[] {
  const fromText = text.split(",").map(s => s.trim()).filter(Boolean);
  return [...new Set([...sel, ...fromText])];
}

// ─── Loading screen ───────────────────────────────────────────────────────────
function LoadingScreen() {
  return (
    <>
      <Navbar />
      <main style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--black)", paddingTop: "60px" }}>
        <div style={{ textAlign: "center" }}>
          <div className="spinner" style={{ margin: "0 auto 28px" }} />
          <div style={{ width: "32px", height: "1px", background: "var(--blue)", margin: "0 auto 20px", opacity: 0.6 }} />
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "16px", fontWeight: 700, letterSpacing: "-0.01em", color: "var(--text-1)", marginBottom: "8px" }}>
            Analysing <span style={{ color: "var(--blue-light)" }}>Challenge</span>
          </h2>
          <p style={{ fontSize: "12px", color: "var(--text-3)", letterSpacing: "0.05em" }}>
            Problem Analyst is running · ~15 seconds
          </p>
          <div style={{ display: "flex", gap: "6px", justifyContent: "center", marginTop: "20px" }}>
            {[0,1,2].map(i => (
              <div key={i} style={{ width: "4px", height: "4px", borderRadius: "50%", background: "var(--blue)", animation: `pulse 1.4s ${i*0.22}s ease-in-out infinite` }} />
            ))}
          </div>
        </div>
      </main>
    </>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────
export default function GeneratePage() {
  const router = useRouter();
  const [challenge,    setChallenge]    = useState("");
  const [hackathon,    setHackathon]    = useState("");
  const [sponsorsText, setSponsorsText] = useState("");
  const [tracksText,   setTracksText]   = useState("");
  const [selTracks,    setSelTracks]    = useState<string[]>([]);
  const [selSponsors,  setSelSponsors]  = useState<string[]>([]);
  const [loading,      setLoading]      = useState(false);
  const [error,        setError]        = useState<string|null>(null);

  async function handleSubmit() {
    if (!challenge.trim()) { setError("Please enter a challenge statement."); return; }
    setError(null);
    setLoading(true);
    try {
      const firstStep = await startWorkflow({
        challenge_statement: challenge,
        hackathon_name: hackathon,
        sponsors: buildList(selSponsors, sponsorsText),
        tracks:   buildList(selTracks, tracksText),
      });
      sessionStorage.setItem("exhacker_session_id", firstStep.session_id);
      sessionStorage.setItem("exhacker_workflow_steps", JSON.stringify([
        { step: firstStep.completed_step, label: firstStep.completed_step_label, output: firstStep.output } satisfies CompletedStep,
      ]));
      sessionStorage.setItem("exhacker_workflow_meta", JSON.stringify({
        currentStep: firstStep.next_step,
        nextIsSelectStep: firstStep.next_is_select_step,
        done: firstStep.done,
      }));
      sessionStorage.setItem("exhacker_challenge_info", JSON.stringify({
        challenge_statement: challenge, hackathon_name: hackathon,
      }));
      router.push("/workflow");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setLoading(false);
    }
  }

  if (loading) return <LoadingScreen />;

  return (
    <>
      <Navbar />
      <main style={{ minHeight: "100vh", background: "transparent", paddingTop: "60px" }}>

        {/* ══ HERO SECTION ══════════════════════════════════════════════════ */}
        <section style={{ padding: "72px 0 56px", borderBottom: "1px solid var(--border)", position: "relative", overflow: "hidden", background: "transparent" }}>
          {/* Bg glow */}
          <div style={{ position: "absolute", top: "-100px", right: "0", width: "500px", height: "500px", background: "radial-gradient(circle, rgba(61,124,246,0.07) 0%, transparent 70%)", pointerEvents: "none", borderRadius: "50%" }} />

          <div className="container">
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "80px", alignItems: "center" }}>

              {/* Left */}
              <div className="anim-fade-up">
                <span className="sec-num">[ NEW PROJECT ]</span>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "24px" }}>
                  <span className="badge badge-lime">
                    <span style={{ width: "5px", height: "5px", borderRadius: "50%", background: "var(--lime)" }} />
                    New Project
                  </span>
                </div>
                <h1 className="d2" style={{ color: "var(--text-1)", marginBottom: "8px" }}>
                  Describe Your
                </h1>
                <h1 className="d2" style={{ marginBottom: "24px" }}>
                  <span style={{ color: "var(--lime)" }}>Challenge.</span>
                </h1>
                <p className="body-md" style={{ maxWidth: "380px", marginBottom: "36px" }}>
                  Nine specialised AI agents run one at a time. You review, edit,
                  and approve each output before the next begins.
                </p>
                {/* Stats */}
                <div style={{ display: "flex", gap: "28px", paddingTop: "24px", borderTop: "1px solid var(--border)" }}>
                  {[{ num:"9", label:"AI Agents" }, { num:"10", label:"Ideas" }, { num:"3", label:"Pitch Scripts" }].map(s => (
                    <div key={s.label}>
                      <div style={{ fontFamily: "var(--font-display)", fontWeight: 800, fontSize: "24px", color: "var(--blue-light)", letterSpacing: "-0.02em", lineHeight: 1, marginBottom: "3px" }}>{s.num}</div>
                      <div style={{ fontSize: "9px", letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--text-3)", fontWeight: 500 }}>{s.label}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Right: Pipeline preview terminal */}
              <div className="anim-fade-up-2 term-window">
                <div className="term-bar">
                  <div className="term-dot term-dot-r" /><div className="term-dot term-dot-y" /><div className="term-dot term-dot-g" />
                  <span style={{ marginLeft: "auto", fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-3)" }}>exhacker · what happens next</span>
                </div>
                <div style={{ padding: "6px 0" }}>
                  {PIPELINE.map(s => (
                    <div key={s.id} style={{
                      display: "flex", alignItems: "center", gap: "12px", padding: "9px 16px",
                      borderLeft: s.isYou ? "2px solid var(--blue)" : "2px solid transparent",
                      background: s.isYou ? "var(--blue-dim)" : "transparent",
                    }}>
                      <span style={{ fontFamily: "var(--font-mono)", fontSize: "9px", color: s.isYou ? "var(--blue-light)" : "var(--text-3)", minWidth: "20px", letterSpacing: "0.05em" }}>{s.id}</span>
                      <span style={{ fontSize: "12px", color: s.isYou ? "var(--text-1)" : "var(--text-2)", fontWeight: s.isYou ? 600 : 400, flex: 1 }}>{s.name}</span>
                      {s.isYou && <span className="badge badge-blue" style={{ fontSize: "9px", padding: "1px 6px" }}>YOU</span>}
                      {!s.isYou && <span style={{ fontSize: "11px", color: "var(--text-3)" }}>{s.desc}</span>}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ══ FORM + FILTERS ════════════════════════════════════════════════ */}
        <section style={{ padding: "64px 0", background: "rgba(14,14,14,0.82)", backdropFilter: "blur(4px)", borderBottom: "1px solid var(--border)" }}>
          <div className="container">
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "80px" }}>

              {/* Form */}
              <div className="anim-fade-up">
                <span className="sec-num" style={{ marginBottom: "12px" }}>[ FILL IN THE DETAILS ]</span>
                <h2 style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: "24px", letterSpacing: "-0.02em", color: "var(--text-1)", marginBottom: "32px" }}>
                  Your Challenge
                </h2>

                {/* Challenge textarea */}
                <div style={{ marginBottom: "20px" }}>
                  <label style={{ display: "block", fontSize: "11px", fontWeight: 500, letterSpacing: "0.08em", textTransform: "uppercase", color: "var(--text-3)", marginBottom: "8px" }}>
                    Challenge Statement <span style={{ color: "var(--blue)" }}>*</span>
                  </label>
                  <textarea
                    className="field"
                    value={challenge}
                    onChange={e => setChallenge(e.target.value)}
                    placeholder="Describe the hackathon challenge you're tackling..."
                    style={{ height: "120px" }}
                  />
                  {/* Example buttons */}
                  <div style={{ display: "flex", gap: "6px", marginTop: "8px", flexWrap: "wrap" }}>
                    {EXAMPLES.map((ex, i) => (
                      <button key={i} onClick={() => setChallenge(ex)} style={{
                        fontSize: "10px", color: "var(--text-3)", background: "var(--surface-2)",
                        border: "1px solid var(--border-mid)", padding: "4px 10px",
                        cursor: "pointer", borderRadius: "2px", transition: "all 0.15s",
                      }}
                        onMouseEnter={e => { (e.currentTarget).style.color = "var(--text-1)"; (e.currentTarget).style.borderColor = "var(--border-strong)"; }}
                        onMouseLeave={e => { (e.currentTarget).style.color = "var(--text-3)"; (e.currentTarget).style.borderColor = "var(--border-mid)"; }}
                      >
                        Example {i+1} ↗
                      </button>
                    ))}
                  </div>
                </div>

                {/* Hackathon name */}
                <div style={{ marginBottom: "28px" }}>
                  <label style={{ display: "block", fontSize: "11px", fontWeight: 500, letterSpacing: "0.08em", textTransform: "uppercase", color: "var(--text-3)", marginBottom: "8px" }}>
                    Hackathon Name <span style={{ fontSize: "10px", color: "var(--text-3)", letterSpacing: "normal", textTransform: "none" }}>— optional</span>
                  </label>
                  <input type="text" className="field" value={hackathon} onChange={e => setHackathon(e.target.value)} placeholder="e.g. HackMIT 2025, Google Solution Challenge..." />
                </div>

                {/* Error */}
                {error && (
                  <div style={{ marginBottom: "20px", padding: "12px 16px", background: "rgba(239,68,68,0.06)", border: "1px solid rgba(239,68,68,0.2)", color: "#fca5a5", fontSize: "13px", display: "flex", gap: "8px", alignItems: "center", borderRadius: "4px" }}>
                    <span>⚠</span><span>{error}</span>
                  </div>
                )}

                <button id="generate-btn" onClick={handleSubmit} disabled={!challenge.trim()} className="btn btn-primary" style={{ width: "100%", padding: "14px", fontSize: "13px", justifyContent: "center" }}>
                  <span>◆</span> Begin Step-by-Step Analysis
                </button>
                <p style={{ textAlign: "center", marginTop: "12px", fontSize: "10px", color: "var(--text-3)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
                  9 Agents · You Control Each Step · Full Strategy
                </p>
              </div>

              {/* Filters */}
              <div className="anim-fade-up-1">
                <span className="sec-num" style={{ marginBottom: "12px" }}>[ NARROW THE SCOPE ]</span>
                <h2 style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: "24px", letterSpacing: "-0.02em", color: "var(--text-1)", marginBottom: "32px" }}>
                  Optional Filters
                </h2>

                {/* Tracks */}
                <div style={{ marginBottom: "28px" }}>
                  <label style={{ display: "block", fontSize: "11px", fontWeight: 500, letterSpacing: "0.08em", textTransform: "uppercase", color: "var(--text-3)", marginBottom: "10px" }}>Tracks</label>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "10px" }}>
                    {TRACKS.map(t => (
                      <button key={t} onClick={() => setSelTracks(toggle(selTracks, t))}
                        className={`chip ${selTracks.includes(t) ? "active" : ""}`}
                      >
                        {selTracks.includes(t) && <span style={{ fontSize: "9px" }}>✓</span>}{t}
                      </button>
                    ))}
                  </div>
                  <input type="text" className="field" value={tracksText} onChange={e => setTracksText(e.target.value)} placeholder="Or type custom tracks, comma-separated..." style={{ fontSize: "12px" }} />
                </div>

                {/* Sponsors */}
                <div>
                  <label style={{ display: "block", fontSize: "11px", fontWeight: 500, letterSpacing: "0.08em", textTransform: "uppercase", color: "var(--text-3)", marginBottom: "10px" }}>Sponsors</label>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "10px" }}>
                    {SPONSORS.map(s => (
                      <button key={s} onClick={() => setSelSponsors(toggle(selSponsors, s))}
                        className={`chip ${selSponsors.includes(s) ? "active" : ""}`}
                      >
                        {selSponsors.includes(s) && <span style={{ fontSize: "9px" }}>✓</span>}{s}
                      </button>
                    ))}
                  </div>
                  <input type="text" className="field" value={sponsorsText} onChange={e => setSponsorsText(e.target.value)} placeholder="Or type custom sponsors, comma-separated..." style={{ fontSize: "12px" }} />
                </div>
              </div>
            </div>
          </div>
        </section>

      </main>
    </>
  );
}
