"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { getProject, Project } from "@/services/api";
import { usePipeline } from "@/components/pipeline/PipelineContext";
import { PIPELINE_STAGES } from "@/components/pipeline/types";
import { Card, Pill, Grid } from "@/components/shared/ui";

const QUICK_ACTIONS = [
  { section: "challenge", label: "Analyze challenge", icon: "🧠", desc: "Extract constraints, opportunities, and strategy" },
  { section: "research", label: "Run research", icon: "🔍", desc: "Scan competitors, APIs, OSS, trends" },
  { section: "ideas", label: "Generate ideas", icon: "💡", desc: "Create 5 scored product concepts" },
  { section: "architecture", label: "Design architecture", icon: "🏗️", desc: "Complete technical blueprint" },
  { section: "docs", label: "Build docs", icon: "📝", desc: "Generate 10 documentation files" },
  { section: "exports", label: "Export package", icon: "📦", desc: "Download your project" },
];

export default function OverviewPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const { state } = usePipeline();
  const [project, setProject] = useState<Project | null>(null);

  useEffect(() => { if (projectId) getProject(projectId).then(r => { if (r.success) setProject(r.data.project); }); }, [projectId]);

  if (!project) return null;

  const stages = PIPELINE_STAGES;
  const completed = Object.values(state.stages).filter(s => s.status === "completed" || s.status === "cached").length;
  const total = stages.length;
  const pct = Math.round((completed / total) * 100);

  return (
    <div className="anim-fade-up">
      {/* Header */}
      <div style={{ marginBottom: "24px" }}>
        <span className="sec-num">[ MISSION CONTROL ]</span>
        <h2 className="d4" style={{ color: "var(--text-1)", marginBottom: "4px" }}>{project.name}</h2>
        <p className="body-sm">{project.idea?.slice(0, 120)}{project.idea?.length > 120 ? "..." : ""}</p>
      </div>

      {/* Progress */}
      <Card style={{ marginBottom: "24px", padding: "20px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
          <div>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)" }}>Pipeline Progress</span>
            <span style={{ fontSize: "11px", color: "var(--text-3)", marginLeft: "8px" }}>{completed}/{total} stages</span>
          </div>
          <Pill color={pct === 100 ? "var(--lime)" : "var(--blue-light)"} bg={pct === 100 ? "rgba(194,255,77,0.12)" : "var(--blue-dim)"}>
            {pct}% complete
          </Pill>
        </div>
        <div style={{ height: "4px", borderRadius: "2px", background: "var(--surface-3)", overflow: "hidden" }}>
          <div style={{ width: `${pct}%`, height: "100%", borderRadius: "2px", background: pct === 100 ? "var(--lime)" : "var(--blue)", transition: "width 0.8s cubic-bezier(.25,.8,.25,1)" }} />
        </div>
        <div style={{ display: "flex", gap: "0", marginTop: "12px" }}>
          {stages.map((stage, i) => {
            const s = state.stages[stage.id];
            const isDone = s?.status === "completed" || s?.status === "cached";
            const isActive = s?.status === "running" || s?.status === "streaming";
            return (
              <div key={stage.id} style={{ flex: 1, textAlign: "center", position: "relative" }}>
                <div style={{
                  width: "20px", height: "20px", borderRadius: "50%", margin: "0 auto 4px",
                  background: isDone ? "var(--lime)" : isActive ? "var(--blue)" : "var(--surface-3)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "8px", color: isDone || isActive ? "#000" : "var(--text-3)", fontWeight: 700,
                  transition: "all 0.3s",
                }}>
                  {isDone ? "✓" : isActive ? "•" : String(i + 1)}
                </div>
                <span style={{ fontSize: "8px", color: isDone ? "var(--lime)" : "var(--text-3)", display: "block", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {stage.shortName}
                </span>
                {i < stages.length - 1 && (
                  <div style={{ position: "absolute", top: "10px", left: "60%", right: "-40%", height: "1px", background: isDone ? "var(--lime)" : "var(--surface-3)" }} />
                )}
              </div>
            );
          })}
        </div>
      </Card>

      {/* Quick actions */}
      <span className="sec-num" style={{ marginBottom: "12px" }}>[ QUICK ACTIONS ]</span>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "8px", marginBottom: "24px" }}>
        {QUICK_ACTIONS.map(qa => {
          const stageState = state.stages[qa.section];
          const isDone = stageState?.status === "completed" || stageState?.status === "cached";
          return (
            <button
              key={qa.section}
              onClick={() => router.push(`/projects/${projectId}/${qa.section}`)}
              style={{
                display: "flex", gap: "12px", alignItems: "center",
                padding: "14px 16px", background: isDone ? "rgba(194,255,77,0.04)" : "var(--surface-1)",
                border: `1px solid ${isDone ? "rgba(194,255,77,0.15)" : "var(--border)"}`,
                borderRadius: "var(--r-md)", cursor: "pointer", textAlign: "left",
                transition: "all 0.15s",
              }}
              onMouseEnter={e => { (e.currentTarget).style.borderColor = "var(--border-mid)"; (e.currentTarget).style.background = "var(--surface-2)"; }}
              onMouseLeave={e => { (e.currentTarget).style.borderColor = isDone ? "rgba(194,255,77,0.15)" : "var(--border)"; (e.currentTarget).style.background = isDone ? "rgba(194,255,77,0.04)" : "var(--surface-1)"; }}
            >
              <span style={{ fontSize: "18px" }}>{qa.icon}</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <span style={{ fontSize: "12px", fontWeight: 600, color: isDone ? "var(--lime)" : "var(--text-1)" }}>{qa.label}</span>
                  {isDone && <span style={{ fontSize: "9px", color: "var(--lime)" }}>✓</span>}
                </div>
                <span style={{ fontSize: "10px", color: "var(--text-3)", display: "block", marginTop: "1px" }}>{qa.desc}</span>
              </div>
              <span style={{ fontSize: "10px", color: "var(--text-3)" }}>→</span>
            </button>
          );
        })}
      </div>

      {/* Stats */}
      <span className="sec-num" style={{ marginBottom: "12px" }}>[ PROJECT STATS ]</span>
      <Grid cols={3} gap="10px">
        <Card style={{ padding: "16px", textAlign: "center" }}>
          <span style={{ fontSize: "24px", fontWeight: 800, color: "var(--blue-light)", fontFamily: "var(--font-display)", display: "block", lineHeight: 1, marginBottom: "4px" }}>{completed}</span>
          <span style={{ fontSize: "10px", color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Stages Done</span>
        </Card>
        <Card style={{ padding: "16px", textAlign: "center" }}>
          <span style={{ fontSize: "24px", fontWeight: 800, color: "var(--lime)", fontFamily: "var(--font-display)", display: "block", lineHeight: 1, marginBottom: "4px" }}>{project.status}</span>
          <span style={{ fontSize: "10px", color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Status</span>
        </Card>
        <Card style={{ padding: "16px", textAlign: "center" }}>
          <span style={{ fontSize: "24px", fontWeight: 800, color: "var(--sky)", fontFamily: "var(--font-display)", display: "block", lineHeight: 1, marginBottom: "4px" }}>{stages.length - completed}</span>
          <span style={{ fontSize: "10px", color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Remaining</span>
        </Card>
      </Grid>
    </div>
  );
}
