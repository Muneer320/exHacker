"use client";

import { useState } from "react";
import { IdeaData } from "@/services/api";
import { Pill, ScoreBar } from "@/components/shared/ui";
import MermaidViewer from "@/components/diagrams/MermaidViewer";

const SCORES = [
  { key: "overall", label: "Overall", color: "var(--blue)" },
  { key: "innovation", label: "Innovation", color: "var(--blue)" },
  { key: "creativity", label: "Creativity", color: "var(--sky)" },
  { key: "technical_depth", label: "Tech Depth", color: "var(--blue-light)" },
  { key: "feasibility", label: "Feasibility", color: "var(--lime)" },
  { key: "demo_potential", label: "Demo Potential", color: "var(--sky)" },
  { key: "judge_appeal", label: "Judge Appeal", color: "var(--blue-light)" },
  { key: "business_potential", label: "Business", color: "var(--lime)" },
  { key: "originality", label: "Originality", color: "var(--blue)" },
  { key: "confidence", label: "Confidence", color: "var(--lime)" },
];

function getScore(idea: IdeaData, key: string): number | null {
  const s = idea.scores as unknown as Record<string, number | null> | undefined;
  if (!s) return null;
  return s[key] ?? null;
}

export default function IdeaComparison({ ideas }: { ideas: IdeaData[] }) {
  const [selected, setSelected] = useState<string[]>([]);

  const toggleIdea = (id: string) => {
    if (selected.includes(id)) {
      setSelected(selected.filter(s => s !== id));
    } else {
      if (selected.length >= 3) return; // Max 3
      setSelected([...selected, id]);
    }
  };

  const compareIdeas = ideas.filter(i => selected.includes(i.id));

  return (
    <div>
      {/* Selection */}
      <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "20px" }}>
        <span style={{ fontSize: "11px", color: "var(--text-3)", alignSelf: "center", marginRight: "8px" }}>
          Select up to 3 ideas to compare:
        </span>
        {ideas.map(idea => {
          const isSel = selected.includes(idea.id);
          return (
            <button
              key={idea.id}
              onClick={() => toggleIdea(idea.id)}
              className={`chip ${isSel ? "active" : ""}`}
              style={isSel ? { background: "var(--blue-dim)", borderColor: "var(--blue)", color: "var(--blue-light)" } : {}}
            >
              {idea.title}
            </button>
          );
        })}
        {selected.length > 0 && (
          <button onClick={() => setSelected([])} className="chip" style={{ color: "var(--text-3)" }}>
            Clear all
          </button>
        )}
      </div>

      {/* Comparison table */}
      {compareIdeas.length === 0 && (
        <div style={{ textAlign: "center", padding: "48px", border: "1px dashed var(--border)", borderRadius: "var(--r-md)" }}>
          <p style={{ fontSize: "13px", color: "var(--text-3)" }}>Select ideas above to compare them side by side.</p>
        </div>
      )}

      {compareIdeas.length >= 2 && (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px", minWidth: "600px" }}>
            {/* Scores section */}
            <thead>
              <tr>
                <th style={{ padding: "10px 14px", textAlign: "left", borderBottom: "2px solid var(--blue)", color: "var(--text-3)", fontWeight: 600, fontSize: "11px", whiteSpace: "nowrap", minWidth: "120px" }}>
                  Score
                </th>
                {compareIdeas.map(idea => (
                  <th key={idea.id} style={{ padding: "10px 14px", textAlign: "center", borderBottom: "2px solid var(--blue)", color: "var(--text-1)", fontWeight: 700, fontSize: "13px" }}>
                    {idea.title}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {SCORES.map(score => (
                <tr key={score.key}>
                  <td style={{ padding: "8px 14px", borderBottom: "1px solid var(--border)", color: "var(--text-3)", fontWeight: 500, fontSize: "11px" }}>
                    {score.label}
                  </td>
                  {compareIdeas.map(idea => {
                    const val = getScore(idea, score.key);
                    return (
                      <td key={idea.id} style={{ padding: "8px 14px", borderBottom: "1px solid var(--border)", textAlign: "center" }}>
                        {val !== null ? (
                          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                            <span style={{
                              fontSize: "16px", fontWeight: 800, fontFamily: "var(--font-display)",
                              color: val >= 80 ? "var(--lime)" : val >= 60 ? "var(--warning)" : "var(--error)",
                              minWidth: "28px",
                            }}>
                              {Math.round(val)}
                            </span>
                            <div style={{ flex: 1, maxWidth: "80px" }}>
                              <ScoreBar value={val} color={score.color} size="sm" />
                            </div>
                          </div>
                        ) : (
                          <span style={{ color: "var(--text-3)" }}>—</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>

            {/* Features section */}
            {compareIdeas.some(i => i.core_features?.length > 0 || i.stretch_features?.length > 0) && (
              <>
                <thead>
                  <tr>
                    <th style={{ padding: "10px 14px", textAlign: "left", borderBottom: "2px solid var(--lime)", color: "var(--lime)", fontWeight: 600, fontSize: "11px", whiteSpace: "nowrap" }}>
                      Features
                    </th>
                    {compareIdeas.map(idea => (
                      <th key={idea.id} style={{ padding: "10px 14px", borderBottom: "2px solid var(--lime)" }} />
                    ))}
                  </tr>
                </thead>
                <tr>
                  <td style={{ padding: "8px 14px", borderBottom: "1px solid var(--border)", color: "var(--text-3)", fontSize: "11px", verticalAlign: "top" }}>
                    Core
                  </td>
                  {compareIdeas.map(idea => (
                    <td key={idea.id} style={{ padding: "8px 14px", borderBottom: "1px solid var(--border)", verticalAlign: "top" }}>
                      <div style={{ display: "flex", gap: "3px", flexWrap: "wrap" }}>
                        {(idea.core_features || []).map((f, i) => (
                          <Pill key={i} color="var(--lime)" bg="rgba(194,255,77,0.08)">{f}</Pill>
                        ))}
                      </div>
                    </td>
                  ))}
                </tr>
                <tr>
                  <td style={{ padding: "8px 14px", borderBottom: "1px solid var(--border)", color: "var(--text-3)", fontSize: "11px", verticalAlign: "top" }}>
                    Stretch
                  </td>
                  {compareIdeas.map(idea => (
                    <td key={idea.id} style={{ padding: "8px 14px", borderBottom: "1px solid var(--border)", verticalAlign: "top" }}>
                      <div style={{ display: "flex", gap: "3px", flexWrap: "wrap" }}>
                        {(idea.stretch_features || []).map((f, i) => (
                          <Pill key={i} color="var(--warning)" bg="rgba(245,158,11,0.08)">{f} ✱</Pill>
                        ))}
                      </div>
                    </td>
                  ))}
                </tr>
              </>
            )}

            {/* Effort / Difficulty */}
            {compareIdeas.some(i => i.estimated_build_hours || i.estimated_difficulty) && (
              <>
                <thead>
                  <tr>
                    <th style={{ padding: "10px 14px", textAlign: "left", borderBottom: "2px solid var(--warning)", color: "var(--warning)", fontWeight: 600, fontSize: "11px" }}>
                      Effort
                    </th>
                    {compareIdeas.map(idea => (
                      <th key={idea.id} style={{ padding: "10px 14px", borderBottom: "2px solid var(--warning)" }} />
                    ))}
                  </tr>
                </thead>
                {compareIdeas.some(i => i.estimated_build_hours) && (
                  <tr>
                    <td style={{ padding: "8px 14px", borderBottom: "1px solid var(--border)", color: "var(--text-3)", fontSize: "11px" }}>Build Time</td>
                    {compareIdeas.map(idea => (
                      <td key={idea.id} style={{ padding: "8px 14px", borderBottom: "1px solid var(--border)", textAlign: "center", fontSize: "13px", fontWeight: 600, color: "var(--text-1)" }}>
                        {idea.estimated_build_hours ? `~${idea.estimated_build_hours}h` : "—"}
                      </td>
                    ))}
                  </tr>
                )}
                {compareIdeas.some(i => i.estimated_difficulty) && (
                  <tr>
                    <td style={{ padding: "8px 14px", borderBottom: "1px solid var(--border)", color: "var(--text-3)", fontSize: "11px" }}>Difficulty</td>
                    {compareIdeas.map(idea => (
                      <td key={idea.id} style={{ padding: "8px 14px", borderBottom: "1px solid var(--border)", textAlign: "center" }}>
                        {idea.estimated_difficulty ? (
                          <Pill color={idea.estimated_difficulty >= 70 ? "var(--error)" : idea.estimated_difficulty >= 40 ? "var(--warning)" : "var(--lime)"}
                                bg="var(--surface-2)">
                            {Math.round(idea.estimated_difficulty)}/100
                          </Pill>
                        ) : "—"}
                      </td>
                    ))}
                  </tr>
                )}
              </>
            )}

            {/* Differentiation section */}
            {compareIdeas.some(i => i.competitive_differentiation || i.usp) && (
              <>
                <thead>
                  <tr>
                    <th style={{ padding: "10px 14px", textAlign: "left", borderBottom: "2px solid var(--sky)", color: "var(--sky)", fontWeight: 600, fontSize: "11px" }}>
                      Differentiation
                    </th>
                    {compareIdeas.map(idea => (
                      <th key={idea.id} style={{ padding: "10px 14px", borderBottom: "2px solid var(--sky)" }} />
                    ))}
                  </tr>
                </thead>
                {compareIdeas.map((idea, idx) => (
                  <tr key={idea.id}>
                    {idx === 0 && (
                      <td style={{ padding: "8px 14px", borderBottom: "1px solid var(--border)", color: "var(--text-3)", fontSize: "11px", verticalAlign: "top" }}>
                        USP
                      </td>
                    )}
                    {idx === 0 ? (
                      <td style={{ padding: "8px 14px", borderBottom: "1px solid var(--border)", color: "var(--text-2)", fontSize: "12px", lineHeight: 1.5 }}>
                        {idea.usp || idea.competitive_differentiation || "—"}
                      </td>
                    ) : (
                      <td style={{ padding: "8px 14px", borderBottom: "1px solid var(--border)", color: "var(--text-2)", fontSize: "12px", lineHeight: 1.5 }}>
                        {idea.usp || idea.competitive_differentiation || "—"}
                      </td>
                    )}
                  </tr>
                ))}
              </>
            )}
          </table>
        </div>
      )}
    </div>
  );
}
