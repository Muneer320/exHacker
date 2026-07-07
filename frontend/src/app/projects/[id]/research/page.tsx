"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { startResearchV2, ResearchData2 } from "@/services/api";
import { Card, Section, Pill, ScoreBar, Grid, LoadingState, EmptyState } from "@/components/shared/ui";

const CATEGORY_COLORS: Record<string, string> = {
  product: "var(--blue)", startup: "var(--sky)", oss: "var(--lime)", github: "var(--blue-light)",
  paper: "var(--info)", api: "var(--blue)", framework: "var(--lime)", hackathon_winner: "var(--warning)",
  trend: "var(--sky)", insight: "var(--text-2)",
};

export default function ResearchPage() {
  const params = useParams();
  const projectId = params.id as string;
  const [data, setData] = useState<ResearchData2 | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  useEffect(() => { if (projectId) { setLoading(true); startResearchV2(projectId).then(r => { if (r.success) setData(r.data); }).finally(() => setLoading(false)); } }, [projectId]);

  if (loading) return <LoadingState label="Running research..." />;
  if (!data) return null;

  const cats = data.summary?.categories || [];
  const syn = data.synthesis?.synthesis;
  const techRecs = data.synthesis?.technology_recommendations || [];
  const diffOpps = data.synthesis?.differentiation_opportunities || [];

  return (
    <div>
      <div className="anim-fade-up" style={{ marginBottom: "20px" }}>
        <span className="sec-num">[ RESEARCH ]</span>
        <h2 className="d4" style={{ color: "var(--text-1)", marginBottom: "4px" }}>Research Dashboard</h2>
        <p className="body-sm">{data.summary?.total_results || 0} results across {data.summary?.categories_found || 0} categories</p>
      </div>

      {/* Synthesis */}
      {syn?.summary && (
        <div className="anim-fade-up-1 card" style={{ marginBottom: "20px", borderLeft: "2px solid var(--blue)", background: "linear-gradient(135deg, rgba(61,124,246,0.04) 0%, transparent 100%)" }}>
          <span className="label" style={{ color: "var(--blue-light)", marginBottom: "8px", display: "block" }}>Research Synthesis</span>
          <p style={{ fontSize: "13px", color: "var(--text-2)", lineHeight: 1.7, marginBottom: "12px" }}>{syn.summary}</p>
          {syn.key_opportunities?.length > 0 && (
            <div><span className="label" style={{ marginBottom: "6px", display: "block", color: "var(--lime)" }}>Opportunities</span>
              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>{syn.key_opportunities.map((o, i) => <Pill key={i} color="var(--lime)" bg="rgba(194,255,77,0.08)">{o}</Pill>)}</div>
            </div>
          )}
          {syn.critical_gaps?.length > 0 && (
            <div style={{ marginTop: "8px" }}><span className="label" style={{ marginBottom: "6px", display: "block", color: "var(--error)" }}>Gaps</span>
              {syn.critical_gaps.map((g, i) => <p key={i} style={{ fontSize: "11px", color: "var(--error)", marginBottom: "2px" }}>· {g}</p>)}
            </div>
          )}
        </div>
      )}

      {/* Category filters */}
      <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "16px" }}>
        <button onClick={() => setActiveCategory(null)} className={`chip ${!activeCategory ? "active" : ""}`}>All</button>
        {cats.filter(c => c.count > 0).map(c => (
          <button key={c.id} onClick={() => setActiveCategory(c.id)} className={`chip ${activeCategory === c.id ? "active" : ""}`}>
            {c.label} <span style={{ fontSize: "10px", opacity: 0.6 }}>({c.count})</span>
          </button>
        ))}
      </div>

      {/* Category results */}
      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        {cats.filter(c => c.count > 0 && (!activeCategory || c.id === activeCategory)).map(cat => (
          <div key={cat.id}>
            <Section title={cat.label} color={CATEGORY_COLORS[cat.id] || "var(--text-2)"}>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                {cat.items.map(item => (
                  <Card key={item.id} hover style={{ padding: "14px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "4px" }}>
                      <div>
                        <h4 style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "2px" }}>{item.title}</h4>
                        {item.url && <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: "10px", color: "var(--blue-light)", textDecoration: "none" }}>{item.url} ↗</a>}
                      </div>
                      <div style={{ display: "flex", gap: "4px", alignItems: "center" }}>
                        {item.confidence !== null && <Pill color="var(--lime)" bg="rgba(194,255,77,0.08)">{Math.round(item.confidence * 100)}%</Pill>}
                        {item.relevance && <Pill color={item.relevance === "high" ? "var(--blue-light)" : "var(--text-3)"} bg={item.relevance === "high" ? "var(--blue-dim)" : "var(--surface-2)"}>{item.relevance}</Pill>}
                      </div>
                    </div>
                    {item.snippet && <p style={{ fontSize: "11px", color: "var(--text-2)", lineHeight: 1.5 }}>{item.snippet}</p>}
                  </Card>
                ))}
              </div>
            </Section>
          </div>
        ))}
      </div>

      {/* Technology recommendations */}
      {techRecs.length > 0 && (
        <Section title="Technology Recommendations" icon="⚙️" color="var(--lime)">
          <Grid gap="8px">
            {techRecs.map((t, i) => (
              <Card key={i} style={{ padding: "14px" }}>
                <h4 style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "4px" }}>{t.technology}</h4>
                <p style={{ fontSize: "11px", color: "var(--text-2)", marginBottom: "4px" }}>{t.why}</p>
                <Pill color={t.confidence === "high" ? "var(--lime)" : "var(--warning)"} bg={t.confidence === "high" ? "rgba(194,255,77,0.08)" : "rgba(245,158,11,0.08)"}>{t.confidence}</Pill>
                {t.appears_in_results > 0 && <span style={{ fontSize: "10px", color: "var(--text-3)", marginLeft: "8px" }}>appears in {t.appears_in_results} results</span>}
              </Card>
            ))}
          </Grid>
        </Section>
      )}

      {/* Risks */}
      {data.synthesis?.risks_from_research && data.synthesis.risks_from_research.length > 0 && (
        <Section title="Risks from Research" icon="⚠️" color="var(--error)">
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {data.synthesis.risks_from_research.map((r, i) => (
              <Card key={i} accent="var(--error)" style={{ padding: "12px 16px" }}>
                <h5 style={{ fontSize: "12px", fontWeight: 600, color: "var(--error)", marginBottom: "2px" }}>{r.risk}</h5>
                <p style={{ fontSize: "11px", color: "var(--text-2)" }}>{r.evidence}</p>
              </Card>
            ))}
          </div>
        </Section>
      )}
    </div>
  );
}
