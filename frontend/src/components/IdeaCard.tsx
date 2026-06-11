"use client";

import { Idea } from "../types/project";

const VOID    = "#171715";
const DEEP    = "#2d2d2a";
const SLATE   = "#848fa5";
const MINT    = "#c5fffd";
const INK     = "rgba(255,255,255,0.88)";
const INK_DIM = "rgba(132,143,165,0.85)";
const INK_MUT = "rgba(132,143,165,0.5)";
const RIM     = "rgba(132,143,165,0.14)";
const RIM_M   = "rgba(197,255,253,0.22)";

function ScoreBar({ value, color }: { value: number; color: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
      <div style={{ flex: 1, height: "2px", background: "rgba(132,143,165,0.12)", borderRadius: "1px", overflow: "hidden" }}>
        <div
          style={{
            height: "100%",
            width: `${value * 10}%`,
            background: color,
            borderRadius: "1px",
            transition: "width 0.8s ease",
          }}
        />
      </div>
      <span style={{ fontSize: "11px", color: INK_DIM, fontFamily: "'Cinzel', serif", minWidth: "18px", textAlign: "right" }}>{value}</span>
    </div>
  );
}

export default function IdeaCard({ idea, rank }: { idea: Idea; rank: number }) {
  const isTop = rank === 1;

  return (
    <div
      style={{
        background: `rgba(45,45,42,0.9)`,
        border: `1px solid ${isTop ? RIM_M : RIM}`,
        padding: "24px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        borderTop: isTop ? `2px solid rgba(197,255,253,0.35)` : undefined,
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Rank */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
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
          }}
        >
          {rank}
        </div>
        {isTop && (
          <span
            style={{
              fontSize: "8px",
              letterSpacing: "1.5px",
              padding: "2px 8px",
              border: `1px solid rgba(197,255,253,0.25)`,
              color: MINT,
              textTransform: "uppercase",
              fontFamily: "'DM Sans', sans-serif",
            }}
          >
            Top Pick
          </span>
        )}
      </div>

      {/* Title */}
      <div>
        <h3
          style={{
            fontSize: "14px",
            fontFamily: "'Cinzel', serif",
            letterSpacing: "0.5px",
            color: INK,
            marginBottom: "8px",
            lineHeight: 1.35,
          }}
        >
          {idea.title}
        </h3>
        <p
          style={{
            fontSize: "12px",
            color: INK_DIM,
            lineHeight: 1.7,
            fontFamily: "'DM Sans', sans-serif",
          }}
        >
          {idea.description}
        </p>
      </div>

      {/* Scores */}
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
          <span style={{ fontSize: "9px", letterSpacing: "2px", color: INK_MUT, textTransform: "uppercase", fontFamily: "'DM Sans', sans-serif" }}>Scores</span>
        </div>
        {[
          { l: "Feasibility",   v: idea.feasibility_score,   c: MINT },
          { l: "Innovation",    v: idea.innovation_score,    c: SLATE },
          { l: "Hackathon Fit", v: idea.hackathon_fit_score, c: MINT },
        ].map(({ l, v, c }) => (
          <div key={l} style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <span style={{ fontSize: "9px", color: INK_MUT, textTransform: "uppercase", letterSpacing: "1px", fontFamily: "'DM Sans', sans-serif", minWidth: "80px" }}>{l}</span>
            <ScoreBar value={v} color={c} />
          </div>
        ))}
      </div>

      {/* Problem solved */}
      {idea.problem_solved && (
        <div style={{ borderTop: `1px solid ${RIM}`, paddingTop: "14px" }}>
          <p style={{ fontSize: "9px", letterSpacing: "2px", color: INK_MUT, textTransform: "uppercase", fontFamily: "'DM Sans', sans-serif", marginBottom: "6px" }}>Problem Solved</p>
          <p style={{ fontSize: "12px", color: INK_DIM, lineHeight: 1.65, fontFamily: "'DM Sans', sans-serif" }}>{idea.problem_solved}</p>
        </div>
      )}

      {/* Why it wins */}
      {idea.why_it_wins && (
        <div style={{ borderTop: `1px solid ${RIM}`, paddingTop: "12px" }}>
          <p style={{ fontSize: "9px", letterSpacing: "2px", color: isTop ? MINT : SLATE, textTransform: "uppercase", fontFamily: "'DM Sans', sans-serif", marginBottom: "6px" }}>Why It Wins</p>
          <p style={{ fontSize: "12px", color: INK_DIM, lineHeight: 1.65, fontFamily: "'DM Sans', sans-serif" }}>{idea.why_it_wins}</p>
        </div>
      )}
    </div>
  );
}
