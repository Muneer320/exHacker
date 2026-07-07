"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { getIdeas, generateIdeas, selectIdea, IdeaData } from "@/services/api";
import { Card, Pill, ScoreBar, SeverityBadge, LoadingState } from "@/components/shared/ui";
import IdeaComparison from "@/components/comparison/IdeaComparison";
import GuidedSection from "@/components/shared/GuidedSection";
import { useToast } from "@/components/shared/Toast";

const SCORE_DEFS = [
  { key: "innovation", label: "Innovation", color: "var(--blue)" },
  { key: "creativity", label: "Creativity", color: "var(--sky)" },
  { key: "technical_depth", label: "Technical Depth", color: "var(--blue-light)" },
  { key: "feasibility", label: "Feasibility", color: "var(--lime)" },
  { key: "demo_potential", label: "Demo Potential", color: "var(--sky)" },
  { key: "judge_appeal", label: "Judge Appeal", color: "var(--blue-light)" },
  { key: "business_potential", label: "Business Potential", color: "var(--lime)" },
  { key: "originality", label: "Originality", color: "var(--blue)" },
  { key: "confidence", label: "Confidence", color: "var(--lime)" },
  { key: "overall", label: "Overall", color: "var(--blue)" },
];

function IdeaCard({ idea, isSelected, onSelect }: { idea: IdeaData; isSelected: boolean; onSelect: () => void }) {
  const s = idea.scores;
  const [expanded, setExpanded] = useState(false);

  return (
    <Card accent={isSelected ? "var(--lime)" : "var(--blue)"} hover style={{
      opacity: isSelected ? 1 : undefined,
      cursor: "pointer", position: "relative",
    }} onClick={() => setExpanded(!expanded)}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <h3 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-1)", letterSpacing: "-0.01em" }}>{idea.title}</h3>
            {isSelected && <Pill color="var(--lime)" bg="rgba(194,255,77,0.12)">✓ Selected</Pill>}
          </div>
          <p style={{ fontSize: "12px", color: "var(--text-2)", fontStyle: "italic" }}>{idea.hook}</p>
        </div>
        {s?.overall !== null && s?.overall !== undefined && (
          <div style={{ textAlign: "center", minWidth: "50px" }}>
            <div style={{ fontSize: "24px", fontWeight: 800, color: s.overall >= 80 ? "var(--lime)" : s.overall >= 60 ? "var(--warning)" : "var(--error)", fontFamily: "var(--font-display)", lineHeight: 1 }}>{s.overall}</div>
            <div style={{ fontSize: "9px", color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Overall</div>
          </div>
        )}
      </div>
      {idea.strategy_label && <Pill color="var(--blue-light)" bg="var(--blue-dim)" style={{ marginBottom: "10px" }}>{idea.strategy_label}</Pill>}
      {idea.elevator_pitch && <p style={{ fontSize: "12px", color: "var(--text-2)", lineHeight: 1.6, marginBottom: "12px", paddingLeft: "10px", borderLeft: "2px solid var(--blue)" }}>{idea.elevator_pitch}</p>}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4px 16px", marginBottom: "12px" }}>
        {SCORE_DEFS.filter(sd => sd.key !== "overall" && sd.key !== "confidence").map(sd => (
          <div key={sd.key} style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ fontSize: "10px", color: "var(--text-3)", minWidth: "56px", textAlign: "right" }}>{sd.label}</span>
            <div style={{ flex: 1 }}><ScoreBar value={(s as any)?.[sd.key] ?? 0} color={sd.color} size="sm" /></div>
            <span style={{ fontSize: "10px", color: "var(--text-2)", fontWeight: 600, minWidth: "20px", fontFamily: "var(--font-mono)" }}>{(s as any)?.[sd.key] ?? "—"}</span>
          </div>
        ))}
      </div>
      {idea.core_features?.length > 0 && (
        <div style={{ display: "flex", gap: "4px", flexWrap: "wrap", marginBottom: "8px" }}>
          {idea.core_features.map((f, i) => <Pill key={i} color="var(--lime)" bg="rgba(194,255,77,0.08)">{f}</Pill>)}
          {idea.stretch_features?.map((f, i) => <Pill key={`s-${i}`} color="var(--warning)" bg="rgba(245,158,11,0.08)">{f} ✱</Pill>)}
        </div>
      )}
      {expanded && (
        <div style={{ borderTop: "1px solid var(--border)", marginTop: "12px", paddingTop: "12px" }}>
          {idea.problem_statement && <div style={{ marginBottom: "10px" }}><span className="label" style={{ marginBottom: "4px", display: "block" }}>Problem</span><p style={{ fontSize: "12px", color: "var(--text-2)", lineHeight: 1.6 }}>{idea.problem_statement}</p></div>}
          {idea.solution && <div style={{ marginBottom: "10px" }}><span className="label" style={{ marginBottom: "4px", display: "block" }}>Solution</span><p style={{ fontSize: "12px", color: "var(--text-2)", lineHeight: 1.6 }}>{idea.solution}</p></div>}
          {idea.competitive_differentiation && <div style={{ marginBottom: "10px" }}><span className="label" style={{ marginBottom: "4px", display: "block" }}>Differentiation</span><p style={{ fontSize: "12px", color: "var(--sky)", lineHeight: 1.6 }}>{idea.competitive_differentiation}</p></div>}
          {idea.technical_risks?.map((r, i) => <div key={i} style={{ display: "flex", gap: "8px", marginBottom: "4px", fontSize: "12px", color: "var(--text-2)" }}><SeverityBadge severity={r.severity} /><span>{r.risk}</span></div>)}
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginTop: "8px" }}>
            {idea.estimated_build_hours && <Pill>⏱ ~{idea.estimated_build_hours}h</Pill>}
            {idea.estimated_difficulty !== null && <Pill>📊 Difficulty: {Math.round(idea.estimated_difficulty)}/100</Pill>}
            {idea.target_platform && <Pill>📱 {idea.target_platform}</Pill>}
          </div>
        </div>
      )}
      {!isSelected && (
        <div style={{ marginTop: "12px" }}>
          <button onClick={(e) => { e.stopPropagation(); onSelect(); }} className="btn btn-primary" style={{ width: "100%", justifyContent: "center", fontSize: "12px" }}>
            Select This Direction
          </button>
        </div>
      )}
    </Card>
  );
}

export default function IdeasPage() {
  const params = useParams();
  const projectId = params.id as string;
  const [ideas, setIdeas] = useState<IdeaData[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [compareMode, setCompareMode] = useState(false);
  const toast = useToast();

  const loadIdeas = async () => {
    setLoading(true);
    const res = await getIdeas(projectId);
    if (res.success && res.data?.ideas?.length) {
      setIdeas(res.data.ideas);
      const sel = res.data.ideas.find(i => i.is_selected);
      if (sel) setSelectedId(sel.id);
    }
    setLoading(false);
  };

  useEffect(() => { if (projectId) loadIdeas(); }, [projectId]);

  const handleGenerate = async () => {
    setGenerating(true);
    toast.addToast({ type: "info", title: "Generating ideas...", message: "The Idea Generator is creating 5 differentiated concepts." });
    const res = await generateIdeas(projectId);
    setGenerating(false);
    if (res.success && res.data?.ideas?.length) {
      setIdeas(res.data.ideas);
      toast.addToast({ type: "success", title: "Ideas generated!", message: `${res.data.count} concepts ready for review.` });
    } else {
      toast.addToast({ type: "error", title: "Generation failed", message: "Could not generate ideas. Please try again." });
    }
  };

  const handleSelect = async (ideaId: string) => {
    const res = await selectIdea(projectId, ideaId);
    if (res.success) {
      setSelectedId(ideaId);
      setIdeas(prev => prev.map(i => ({ ...i, is_selected: i.id === ideaId })));
      toast.addToast({ type: "success", title: "Direction selected", message: "This idea will guide your architecture and implementation." });
    }
  };

  if (loading) return <LoadingState label="Loading ideas..." />;

  if (ideas.length === 0) {
    return (
      <GuidedSection
        title="Idea Generation"
        whyMatters="Generate 5 distinct product concepts scored across 10 dimensions including innovation, feasibility, judge appeal, and business potential."
        status={generating ? "generating" : "idle"}
        actionLabel="Generate Ideas"
        onAction={handleGenerate}
        estimatedTime="~15 seconds"
        whatProduced="5 scored product ideas with full reasoning, features, risks, and comparison data"
        unlocks="Architecture design, documentation generation, and export"
        logLines={generating ? [
          { text: "Loading challenge context...", type: "info" },
          { text: "Analyzing competitor landscape...", type: "search" },
          { text: "Generating idea concepts...", type: "ai" },
          { text: "Scoring and ranking...", type: "synthesis" },
          { text: "✓ Ready for review", type: "done" },
        ] : undefined}
      />
    );
  }

  return (
    <div>
      <div className="anim-fade-up" style={{ marginBottom: "20px" }}>
        <span className="sec-num">[ IDEAS ]</span>
        <h2 className="d4" style={{ color: "var(--text-1)", marginBottom: "4px" }}>Choose Your Direction</h2>
        <p className="body-sm">{ideas.length} ideas · Select the one that best fits your team</p>
        <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
          <button onClick={() => setCompareMode(!compareMode)} className={`btn ${compareMode ? "btn-primary" : "btn-ghost"}`} style={{ fontSize: "11px", padding: "6px 14px" }}>
            {compareMode ? "✓ Done Comparing" : "⇄ Compare Ideas"}
          </button>
          <button onClick={handleGenerate} disabled={generating} className="btn btn-ghost" style={{ fontSize: "11px", padding: "6px 14px" }}>
            {generating ? "Generating..." : "↻ Regenerate"}
          </button>
        </div>
      </div>

      {compareMode && ideas.length >= 2 && (
        <div className="anim-fade-up" style={{ marginBottom: "24px" }}>
          <IdeaComparison ideas={ideas} />
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        {ideas.map(idea => (
          <div key={idea.id} className="anim-fade-up">
            <IdeaCard idea={idea} isSelected={selectedId === idea.id} onSelect={() => handleSelect(idea.id)} />
          </div>
        ))}
      </div>
    </div>
  );
}
