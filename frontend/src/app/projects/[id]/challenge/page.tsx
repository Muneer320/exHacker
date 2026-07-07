"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { analyzeChallenge, getChallengeAnalysis, ChallengeData } from "@/services/api";
import { Card, Section, ScoreRow, Grid, Pill, SeverityBadge, LoadingState, EmptyState, ScoreBar } from "@/components/shared/ui";

export default function ChallengePage() {
  const params = useParams();
  const projectId = params.id as string;
  const [data, setData] = useState<ChallengeData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { if (projectId) { setLoading(true); getChallengeAnalysis(projectId).then(r => { if (r.success && r.data?.executive_summary) setData(r.data); }).finally(() => setLoading(false)); } }, [projectId]);

  const handleAnalyze = async () => {
    setLoading(true);
    const res = await analyzeChallenge(projectId);
    if (res.success) setData(res.data);
    setLoading(false);
  };

  if (loading) return <LoadingState label="Analyzing challenge..." />;

  if (!data || !data.executive_summary) return (
    <EmptyState icon="🧠" title="Challenge Intelligence" description="Analyze the challenge to get structured intelligence: core problems, hidden opportunities, and a recommended strategy."
      action={<button onClick={handleAnalyze} className="btn btn-primary">Analyze Challenge</button>} />
  );

  return (
    <div>
      <div className="anim-fade-up" style={{ marginBottom: "20px" }}>
        <span className="sec-num">[ CHALLENGE ]</span>
        <h2 className="d4" style={{ color: "var(--text-1)", marginBottom: "4px" }}>Challenge Intelligence</h2>
        {data.confidence > 0 && <Pill color={data.confidence >= 0.8 ? "var(--lime)" : "var(--warning)"} bg={data.confidence >= 0.8 ? "rgba(194,255,77,0.12)" : "rgba(245,158,11,0.12)"}>{Math.round(data.confidence * 100)}% confidence</Pill>}
      </div>

      {/* Executive Summary */}
      <div className="anim-fade-up-1 card" style={{ marginBottom: "20px", borderLeft: "2px solid var(--blue)", background: "linear-gradient(135deg, rgba(61,124,246,0.06) 0%, transparent 100%)" }}>
        <span className="label" style={{ color: "var(--blue-light)", marginBottom: "8px", display: "block" }}>Executive Summary</span>
        <p style={{ fontSize: "14px", color: "var(--text-1)", lineHeight: 1.7 }}>{data.executive_summary}</p>
      </div>

      {/* Core Problem + Difficulty */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "20px" }}>
        <Card>
          <span className="label" style={{ color: "var(--blue-light)", marginBottom: "8px", display: "block" }}>Core Problem</span>
          <p style={{ fontSize: "13px", color: "var(--text-2)", lineHeight: 1.6, marginBottom: "8px" }}>{data.core_problem?.problem}</p>
          {data.core_problem?.who_experiences && <p style={{ fontSize: "11px", color: "var(--text-3)" }}><strong>Who:</strong> {data.core_problem.who_experiences}</p>}
          {data.core_problem?.why_important && <p style={{ fontSize: "11px", color: "var(--text-3)" }}><strong>Why:</strong> {data.core_problem.why_important}</p>}
        </Card>
        {data.difficulty && (
          <Card>
            <span className="label" style={{ color: "var(--blue-light)", marginBottom: "8px", display: "block" }}>Difficulty Assessment</span>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              {Object.entries(data.difficulty).filter(([k]) => k !== "overall" && data.difficulty?.[k as keyof typeof data.difficulty] !== null).map(([k, v]) => (
                <ScoreRow key={k} label={k.charAt(0).toUpperCase() + k.slice(1)} value={v as number} />
              ))}
            </div>
          </Card>
        )}
      </div>

      {/* Hidden Problems */}
      {data.hidden_problems?.length > 0 && (
        <Section title="Hidden Problems" icon="⚠️" color="var(--warning)">
          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            {data.hidden_problems.map((hp, i) => (
              <Card key={i} accent="var(--warning)" style={{ padding: "12px 16px" }}>
                <p style={{ fontSize: "12px", color: "var(--text-2)" }}>{hp}</p>
              </Card>
            ))}
          </div>
        </Section>
      )}

      {/* Stakeholders */}
      {data.stakeholders?.length > 0 && (
        <Section title="Stakeholders" icon="👥" color="var(--info)">
          <Grid gap="8px">
            {data.stakeholders.map((s, i) => (
              <Card key={i} style={{ padding: "14px" }}>
                <h5 style={{ fontSize: "12px", fontWeight: 700, color: "var(--blue-light)", marginBottom: "4px" }}>{s.role}</h5>
                <p style={{ fontSize: "11px", color: "var(--text-2)" }}>{s.description}</p>
              </Card>
            ))}
          </Grid>
        </Section>
      )}

      {/* Constraints */}
      {data.constraints?.length > 0 && (
        <Section title="Constraints" icon="🔒" color="var(--error)">
          <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
            {data.constraints.map((c, i) => (
              <Card key={i} accent="var(--error)" style={{ padding: "10px 14px", maxWidth: "320px" }}>
                <Pill color="var(--error)" bg="rgba(239,68,68,0.08)" style={{ marginBottom: "4px" }}>{c.type}</Pill>
                <p style={{ fontSize: "11px", color: "var(--text-2)" }}>{c.description}</p>
              </Card>
            ))}
          </div>
        </Section>
      )}

      {/* Success Criteria */}
      {data.success_criteria?.length > 0 && (
        <Section title="Success Criteria" icon="🏆" color="var(--lime)">
          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            {data.success_criteria.map((sc, i) => (
              <Card key={i} style={{ padding: "12px 16px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                  <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-1)" }}>{sc.criterion}</span>
                  <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--lime)" }}>{sc.weight}%</span>
                </div>
                <ScoreBar value={sc.weight ?? 0} color="var(--lime)" size="sm" />
                <p style={{ fontSize: "11px", color: "var(--text-3)", marginTop: "4px" }}>{sc.description}</p>
              </Card>
            ))}
          </div>
        </Section>
      )}

      {/* Opportunities */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "20px" }}>
        {data.opportunity_areas?.length > 0 && (
          <Card>
            <span className="label" style={{ color: "var(--info)", marginBottom: "8px", display: "block" }}>Opportunity Areas</span>
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
              {data.opportunity_areas.map((oa, i) => <Pill key={i} color="var(--info)" bg="var(--sky-dim)">{oa}</Pill>)}
            </div>
          </Card>
        )}
        {data.innovation_opportunities?.length > 0 && (
          <Card>
            <span className="label" style={{ color: "var(--blue-light)", marginBottom: "8px", display: "block" }}>Innovation Opportunities</span>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              {data.innovation_opportunities.map((io, i) => (
                <div key={i} style={{ padding: "8px", borderRadius: "var(--r-sm)", background: "var(--surface-0)" }}>
                  <h6 style={{ fontSize: "11px", fontWeight: 700, color: "var(--blue-light)", marginBottom: "2px" }}>{io.area}</h6>
                  <p style={{ fontSize: "10px", color: "var(--text-3)" }}>{io.description}</p>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>

      {/* Risk Areas */}
      {data.risk_areas?.length > 0 && (
        <Section title="Risk Areas" icon="⚠️" color="var(--error)">
          <Grid gap="8px">
            {data.risk_areas.map((r, i) => {
              const colors: Record<string, string> = { high: "var(--error)", medium: "var(--warning)", low: "var(--info)" };
              return (
                <Card key={i} style={{ padding: "14px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                    <h5 style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)" }}>{r.area}</h5>
                    <Pill color={colors[r.severity] || "var(--text-3)"} bg={`${(colors[r.severity] || "var(--text-3)")}15`}>{r.severity}</Pill>
                  </div>
                  <p style={{ fontSize: "11px", color: "var(--text-2)" }}>{r.description}</p>
                </Card>
              );
            })}
          </Grid>
        </Section>
      )}

      {/* Recommended Strategy */}
      {data.recommended_strategy && (
        <div className="card" style={{ borderLeft: "2px solid var(--info)", background: "linear-gradient(135deg, rgba(6,182,212,0.04) 0%, transparent 100%)" }}>
          <span className="label" style={{ color: "var(--info)", marginBottom: "8px", display: "block" }}>Recommended Strategy</span>
          <p style={{ fontSize: "14px", color: "var(--text-1)", lineHeight: 1.7, fontStyle: "italic" }}>{data.recommended_strategy}</p>
        </div>
      )}
    </div>
  );
}
