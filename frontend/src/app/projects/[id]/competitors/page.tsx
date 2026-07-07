"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { analyzeCompetitors, CompetitorData } from "@/services/api";
import { Card, Section, ScoreRow, ScoreBar, Grid, Pill, SeverityBadge, LoadingState } from "@/components/shared/ui";
import GuidedSection from "@/components/shared/GuidedSection";

export default function CompetitorsPage() {
  const params = useParams();
  const projectId = params.id as string;
  const [data, setData] = useState<CompetitorData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { if (projectId) { setLoading(true); analyzeCompetitors(projectId).then(r => { if (r.success) setData(r.data); }).finally(() => setLoading(false)); } }, [projectId]);

  if (loading) return <LoadingState label="Loading competitor analysis..." />;
  if (!data) return null;

  const gap = data.gap_analysis || {};

  return (
    <div>
      <div className="anim-fade-up" style={{ marginBottom: "20px" }}>
        <span className="sec-num">[ COMPETITORS ]</span>
        <h2 className="d4" style={{ color: "var(--text-1)", marginBottom: "4px" }}>Competitor Intelligence</h2>
        <p className="body-sm">{data.competitors?.length || 0} competitors · Innovation score: {data.innovation_score ?? "—"}</p>
      </div>

      {/* Summary */}
      {data.summary && <div className="anim-fade-up-1 card" style={{ marginBottom: "20px", borderLeft: "2px solid var(--blue)" }}><p style={{ fontSize: "13px", color: "var(--text-2)", lineHeight: 1.7 }}>{data.summary}</p></div>}

      {/* Competitor profiles */}
      <Section title="Competitors" icon="🎯" color="var(--blue)">
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {(data.competitors || []).map((c, i) => (
            <Card key={i} hover>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                <div>
                  <h4 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-1)", marginBottom: "2px" }}>{c.name}</h4>
                  <p style={{ fontSize: "12px", color: "var(--text-2)" }}>{c.description}</p>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "11px", fontFamily: "var(--font-mono)", color: "var(--blue-light)" }}>Innovation: {c.innovation_level}</div>
                  <Pill>{c.market_maturity}</Pill>
                </div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginBottom: "8px" }}>
                <div><span className="label" style={{ display: "block", marginBottom: "4px" }}>Target</span><p style={{ fontSize: "12px", color: "var(--text-2)" }}>{c.target_users}</p></div>
                <div><span className="label" style={{ display: "block", marginBottom: "4px" }}>Business Model</span><p style={{ fontSize: "12px", color: "var(--text-2)" }}>{c.business_model}</p></div>
              </div>
              {c.strengths?.length > 0 && <div style={{ display: "flex", gap: "4px", flexWrap: "wrap", marginBottom: "6px" }}>{c.strengths.map((s, i) => <Pill key={i} color="var(--lime)" bg="rgba(194,255,77,0.08)">{s}</Pill>)}</div>}
              {c.weaknesses?.length > 0 && <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>{c.weaknesses.map((w, i) => <Pill key={i} color="var(--error)" bg="rgba(239,68,68,0.08)">{w}</Pill>)}</div>}
              {c.missing_features?.length > 0 && <p style={{ fontSize: "11px", color: "var(--warning)", marginTop: "6px" }}>Missing: {c.missing_features.join(", ")}</p>}
              {c.tech_stack?.length > 0 && <p style={{ fontSize: "10px", color: "var(--text-3)", marginTop: "4px", fontFamily: "var(--font-mono)" }}>{c.tech_stack.join(" · ")}</p>}
            </Card>
          ))}
        </div>
      </Section>

      {/* Gap Analysis */}
      <Section title="Gap Analysis" icon="🔍" color="var(--lime)">
        <Grid gap="8px">
          {gap.patterns?.length > 0 && <Card><span className="label" style={{ display: "block", marginBottom: "6px", color: "var(--blue-light)" }}>Patterns</span>{(gap.patterns as string[]).map((p, i) => <p key={i} style={{ fontSize: "12px", color: "var(--text-2)", marginBottom: "3px" }}>· {p}</p>)}</Card>}
          {gap.white_space?.length > 0 && <Card accent="var(--lime)"><span className="label" style={{ display: "block", marginBottom: "6px", color: "var(--lime)" }}>White Space</span>{(gap.white_space as string[]).map((w, i) => <p key={i} style={{ fontSize: "12px", color: "var(--lime)", marginBottom: "3px" }}>→ {w}</p>)}</Card>}
          {gap.pain_points?.length > 0 && <Card><span className="label" style={{ display: "block", marginBottom: "6px", color: "var(--error)" }}>Pain Points</span>{(gap.pain_points as string[]).map((p, i) => <p key={i} style={{ fontSize: "12px", color: "var(--text-2)", marginBottom: "3px" }}>· {p}</p>)}</Card>}
          {gap.to_avoid?.length > 0 && <Card accent="var(--error)"><span className="label" style={{ display: "block", marginBottom: "6px", color: "var(--error)" }}>Avoid</span>{(gap.to_avoid as string[]).map((a, i) => <p key={i} style={{ fontSize: "12px", color: "var(--error)", marginBottom: "3px" }}>✕ {a}</p>)}</Card>}
        </Grid>
      </Section>

      {/* Differentiation */}
      {data.quick_wins?.length > 0 && (
        <Section title="Quick Wins (< 6h)" icon="⚡" color="var(--lime)">
          <Grid gap="8px">
            {data.quick_wins.map((o, i) => (
              <Card key={i} hover>
                <h4 style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "6px" }}>{o.title}</h4>
                <div style={{ display: "flex", gap: "8px", fontSize: "11px", color: "var(--text-3)" }}>
                  <span>Difficulty: {o.difficulty}</span>
                  <span>Impact: {o.impact}</span>
                  <span>Judge: {o.judge_appeal}</span>
                  <span>~{o.effort_hours}h</span>
                </div>
              </Card>
            ))}
          </Grid>
        </Section>
      )}

      {/* Innovation breakdown */}
      {data.innovation_breakdown && (
        <Section title="Innovation Score" icon="🏆" color="var(--blue-light)">
          <Card>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
              {Object.entries(data.innovation_breakdown).filter(([k]) => k !== "overall").map(([key, val]) => (
                <ScoreRow key={key} label={key.replace(/_/g, " ")} value={val as number} color="var(--blue-light)" />
              ))}
            </div>
          </Card>
        </Section>
      )}

      {/* Warnings */}
      {data.warnings?.length > 0 && (
        <Section title="Warnings" icon="⚠️" color="var(--warning)">
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {data.warnings.map((w, i) => (
              <Card key={i} accent="var(--warning)">
                <h4 style={{ fontSize: "13px", fontWeight: 600, color: "var(--warning)", marginBottom: "4px" }}>{w.warning}</h4>
                <p style={{ fontSize: "12px", color: "var(--text-2)", marginBottom: "4px" }}>{w.why}</p>
                <p style={{ fontSize: "11px", color: "var(--lime)" }}>→ {w.alternative}</p>
              </Card>
            ))}
          </div>
        </Section>
      )}
    </div>
  );
}
