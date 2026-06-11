"use client";

import { RankedIdea } from "../types/project";

const SLATE   = "#848fa5";
const MINT    = "#c5fffd";
const INK     = "rgba(255,255,255,0.88)";
const INK_DIM = "rgba(132,143,165,0.85)";
const INK_MUT = "rgba(132,143,165,0.5)";
const INK_GHO = "rgba(132,143,165,0.28)";
const RIM     = "rgba(132,143,165,0.14)";
const RIM_M   = "rgba(197,255,253,0.22)";

function DimBar({ value, color }: { value: number; color: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
      <div style={{ flex: 1, height: "2px", background: "rgba(132,143,165,0.12)", borderRadius: "1px", overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${value * 10}%`, background: color, borderRadius: "1px", transition: "width 0.8s ease" }} />
      </div>
      <span style={{ fontSize: "11px", color: INK_DIM, fontFamily: "'Cinzel', serif", minWidth: "18px", textAlign: "right" }}>{typeof value === "number" ? value.toFixed(1) : value}</span>
    </div>
  );
}

export default function PitchCard({ rankedIdea: idea, rank }: { rankedIdea: RankedIdea; rank: number }) {
  const isTop = rank === 1;

  return (
    <div
      style={{
        background: "rgba(45,45,42,0.9)",
        border: `1px solid ${isTop ? RIM_M : RIM}`,
        padding: "24px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        borderTop: isTop ? `2px solid rgba(197,255,253,0.35)` : undefined,
        position: "relative",
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", gap: "12px", alignItems: "flex-start" }}>
        <div
          style={{
            width: "28px",
            height: "28px",
            border: `1px solid ${isTop ? RIM_M : RIM}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: "'Cinzel', serif",
            fontSize: "11px",
            color: isTop ? MINT : SLATE,
            flexShrink: 0,
          }}
        >
          {rank}
        </div>
        <div style={{ flex: 1 }}>
          <h3 style={{ fontSize: "14px", fontFamily: "'Cinzel', serif", letterSpacing: "0.5px", color: INK, marginBottom: "4px", lineHeight: 1.35 }}>
            {idea.title}
          </h3>
          {idea.why_ranked_here && (
            <p style={{ fontSize: "11px", color: INK_MUT, lineHeight: 1.65, fontFamily: "'DM Sans', sans-serif" }}>
              {idea.why_ranked_here}
            </p>
          )}
        </div>
        {/* Final score */}
        <div style={{ textAlign: "center", flexShrink: 0 }}>
          <div
            className="font-display"
            style={{ fontSize: "24px", color: isTop ? MINT : SLATE, lineHeight: 1 }}
          >
            {typeof idea.final_score === "number" ? idea.final_score.toFixed(1) : "—"}
          </div>
          <div style={{ fontSize: "8px", color: INK_GHO, letterSpacing: "1px", fontFamily: "'DM Sans', sans-serif" }}>/10</div>
        </div>
      </div>

      {/* Score bars */}
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        <span style={{ fontSize: "9px", letterSpacing: "2px", color: INK_MUT, textTransform: "uppercase", fontFamily: "'DM Sans', sans-serif" }}>Dimension Scores</span>
        {[
          { l: "Innovation",    v: idea.innovation_score,       c: MINT },
          { l: "Feasibility",   v: idea.feasibility_score,      c: SLATE },
          { l: "Hackathon Fit", v: idea.hackathon_fit_score,    c: MINT },
          { l: "Market",        v: idea.market_potential_score, c: SLATE },
          { l: "Wow Factor",    v: idea.technical_wow_factor,   c: MINT },
        ].map(({ l, v, c }) => (
          <div key={l} style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <span style={{ fontSize: "9px", color: INK_MUT, textTransform: "uppercase", letterSpacing: "1px", fontFamily: "'DM Sans', sans-serif", minWidth: "80px" }}>{l}</span>
            <DimBar value={v} color={c} />
          </div>
        ))}
      </div>

      {/* Strengths / Weaknesses */}
      {(idea.strengths?.length > 0 || idea.weaknesses?.length > 0) && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1px", background: RIM, borderTop: `1px solid ${RIM}`, paddingTop: "14px" }}>
          {idea.strengths?.length > 0 && (
            <div style={{ background: "rgba(45,45,42,0.8)", padding: "12px 14px" }}>
              <p style={{ fontSize: "9px", letterSpacing: "2px", color: MINT, textTransform: "uppercase", fontFamily: "'DM Sans', sans-serif", marginBottom: "8px" }}>Strengths</p>
              <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {idea.strengths.slice(0, 3).map((s, i) => (
                  <li key={i} style={{ fontSize: "11px", color: INK_DIM, lineHeight: 1.6, paddingLeft: "10px", position: "relative", marginBottom: "2px", fontFamily: "'DM Sans', sans-serif" }}>
                    <span style={{ position: "absolute", left: 0, color: MINT }}>›</span>{s}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {idea.weaknesses?.length > 0 && (
            <div style={{ background: "rgba(45,45,42,0.8)", padding: "12px 14px" }}>
              <p style={{ fontSize: "9px", letterSpacing: "2px", color: SLATE, textTransform: "uppercase", fontFamily: "'DM Sans', sans-serif", marginBottom: "8px" }}>Weaknesses</p>
              <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {idea.weaknesses.slice(0, 3).map((w, i) => (
                  <li key={i} style={{ fontSize: "11px", color: INK_DIM, lineHeight: 1.6, paddingLeft: "10px", position: "relative", marginBottom: "2px", fontFamily: "'DM Sans', sans-serif" }}>
                    <span style={{ position: "absolute", left: 0, color: SLATE }}>›</span>{w}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
