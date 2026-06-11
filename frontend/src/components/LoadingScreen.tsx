"use client";

import { useEffect, useState } from "react";

// ─── Palette ──────────────────────────────────────────────────────────────────
const VOID    = "#171715";
const DEEP    = "#2d2d2a";
const SURFACE = "#383835";
const SLATE   = "#848fa5";
const MINT    = "#c5fffd";
const INK     = "rgba(255,255,255,0.88)";
const INK_DIM = "rgba(132,143,165,0.85)";
const INK_MUT = "rgba(132,143,165,0.5)";
const INK_GHO = "rgba(132,143,165,0.28)";
const RIM     = "rgba(132,143,165,0.14)";
const RIM_M   = "rgba(197,255,253,0.22)";

const AGENTS = [
  { n: "01", name: "Problem Analyst",     desc: "Decomposing the challenge" },
  { n: "02", name: "Opportunity Planner", desc: "Mapping market opportunities" },
  { n: "03", name: "Idea Generator",      desc: "Generating 10 concepts" },
  { n: "04", name: "Idea Validator",      desc: "Scoring feasibility & fit" },
  { n: "05", name: "Idea Selection",      desc: "Picking the winner" },
  { n: "06", name: "Solution Architect",  desc: "Building the blueprint" },
  { n: "07", name: "Presentation Agent",  desc: "Creating 10 slides" },
  { n: "08", name: "Pitch Agent",         desc: "Writing pitch scripts" },
  { n: "09", name: "Report Generator",    desc: "Compiling final report" },
];

export default function LoadingScreen({ hackathonName }: { hackathonName?: string }) {
  const [current,  setCurrent]  = useState(0);
  const [done,     setDone]     = useState<number[]>([]);
  const [elapsed,  setElapsed]  = useState(0);
  const [blink,    setBlink]    = useState(true);

  // Clock
  useEffect(() => {
    const t = setInterval(() => setElapsed((e) => e + 1), 1000);
    return () => clearInterval(t);
  }, []);

  // Cursor blink
  useEffect(() => {
    const b = setInterval(() => setBlink((v) => !v), 560);
    return () => clearInterval(b);
  }, []);

  // Step advance
  useEffect(() => {
    const t = setInterval(() => {
      setCurrent((p) => {
        if (p < AGENTS.length - 1) {
          setDone((d) => [...d, p]);
          return p + 1;
        }
        return p;
      });
    }, 5500);
    return () => clearInterval(t);
  }, []);

  const pct = Math.round((done.length / AGENTS.length) * 100);
  const fmt = (s: number) => s < 60 ? `${s}s` : `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;

  return (
    <div
      className="z1"
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "100px 24px 60px",
      }}
    >
      <div style={{ width: "100%", maxWidth: "640px" }}>

        {/* ── Header ── */}
        <div style={{ marginBottom: "44px" }}>
          <p
            style={{
              fontSize: "10px",
              letterSpacing: "2.5px",
              color: SLATE,
              fontFamily: "'DM Sans', sans-serif",
              fontWeight: 600,
              textTransform: "uppercase",
              marginBottom: "12px",
            }}
          >
            ◆ {hackathonName ? `Strategy for ${hackathonName}` : "Generating Strategy"}
          </p>
          <h2
            className="font-display"
            style={{
              fontSize: "28px",
              fontWeight: 700,
              letterSpacing: "4px",
              textTransform: "uppercase",
              color: INK,
              marginBottom: "24px",
              lineHeight: 1.1,
            }}
          >
            Agents <span style={{ color: MINT }}>Running</span>
          </h2>

          {/* Active agent name */}
          <div
            key={current}
            className="anim-reveal-in"
            style={{ display: "flex", alignItems: "center", gap: "12px", minHeight: "40px" }}
          >
            <div
              style={{
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                background: MINT,
                boxShadow: `0 0 12px rgba(197,255,253,0.5)`,
                flexShrink: 0,
              }}
            />
            <div>
              <p style={{ fontSize: "14px", color: INK, fontFamily: "'DM Sans', sans-serif", fontWeight: 500, marginBottom: "2px" }}>
                {AGENTS[current].name}
              </p>
              <p style={{ fontSize: "11px", color: INK_MUT, fontFamily: "'DM Sans', sans-serif", letterSpacing: "0.3px" }}>
                {AGENTS[current].desc}
                <span
                  style={{
                    display: "inline-block",
                    width: "6px",
                    height: "12px",
                    background: SLATE,
                    verticalAlign: "text-bottom",
                    marginLeft: "4px",
                    opacity: blink ? 0.7 : 0,
                    transition: "opacity 0.15s",
                  }}
                />
              </p>
            </div>
            <span
              style={{
                marginLeft: "auto",
                fontSize: "10px",
                color: INK_GHO,
                letterSpacing: "1px",
                fontFamily: "'DM Sans', sans-serif",
              }}
            >
              {fmt(elapsed)}
            </span>
          </div>
        </div>

        {/* ── Progress bar ── */}
        <div
          style={{
            height: "1px",
            background: RIM,
            marginBottom: "28px",
            overflow: "hidden",
            position: "relative",
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${pct}%`,
              background: `linear-gradient(90deg, rgba(197,255,253,0.2), ${MINT}, rgba(197,255,253,0.2))`,
              transition: "width 1.2s ease",
              boxShadow: `0 0 8px rgba(197,255,253,0.3)`,
            }}
          />
        </div>

        {/* ── Agent grid ── */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "1px",
            background: RIM,
          }}
        >
          {AGENTS.map((agent, i) => {
            const isDone   = done.includes(i);
            const isActive = i === current;
            const isPending = !isDone && !isActive;

            return (
              <div
                key={agent.n}
                style={{
                  background: isActive
                    ? "rgba(197,255,253,0.04)"
                    : isDone
                    ? "rgba(56,56,53,0.6)"
                    : "rgba(45,45,42,0.9)",
                  padding: "16px 14px",
                  borderLeft: isActive ? `2px solid ${MINT}` : "2px solid transparent",
                  transition: "all 0.5s ease",
                }}
              >
                {/* Number / check */}
                <div
                  className="font-display"
                  style={{
                    fontSize: "9px",
                    letterSpacing: "1.5px",
                    color: isDone
                      ? "rgba(197,255,253,0.5)"
                      : isActive
                      ? MINT
                      : INK_GHO,
                    marginBottom: "8px",
                  }}
                >
                  {isDone ? "✓" : agent.n}
                </div>

                {/* Name */}
                <p
                  style={{
                    fontSize: "11px",
                    fontWeight: 500,
                    color: isDone
                      ? INK_MUT
                      : isActive
                      ? INK
                      : INK_GHO,
                    letterSpacing: "0.3px",
                    lineHeight: 1.35,
                    fontFamily: "'DM Sans', sans-serif",
                    marginBottom: "4px",
                  }}
                >
                  {agent.name}
                </p>

                {/* Desc / status */}
                <p
                  style={{
                    fontSize: "9px",
                    color: isDone
                      ? INK_GHO
                      : isActive
                      ? INK_MUT
                      : "rgba(132,143,165,0.18)",
                    fontFamily: "'DM Sans', sans-serif",
                    lineHeight: 1.4,
                  }}
                >
                  {isDone ? "Complete" : isActive ? agent.desc : "Waiting"}
                </p>

                {/* Active indicator bar */}
                {isActive && (
                  <div
                    style={{
                      marginTop: "10px",
                      height: "1px",
                      background: `rgba(197,255,253,0.2)`,
                      borderRadius: "1px",
                      overflow: "hidden",
                      position: "relative",
                    }}
                  >
                    <div
                      style={{
                        position: "absolute",
                        top: 0,
                        left: "-60%",
                        width: "60%",
                        height: "100%",
                        background: `linear-gradient(90deg, transparent, ${MINT}, transparent)`,
                        animation: "slide-right 1.8s linear infinite",
                      }}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* ── Footer note ── */}
        <p
          style={{
            textAlign: "center",
            marginTop: "20px",
            fontSize: "10px",
            color: INK_GHO,
            letterSpacing: "1.5px",
            fontFamily: "'DM Sans', sans-serif",
            textTransform: "uppercase",
          }}
        >
          Do not close this tab · Usually 30–90 seconds
        </p>
      </div>
    </div>
  );
}
