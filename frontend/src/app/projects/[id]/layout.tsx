"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, usePathname, useRouter } from "next/navigation";
import { getProject, Project } from "@/services/api";
import { PipelineProvider, usePipeline } from "@/components/pipeline/PipelineContext";
import PipelineSidebar from "@/components/pipeline/PipelineSidebar";
import { ToastProvider } from "@/components/shared/Toast";
import CommandPalette from "@/components/shared/CommandPalette";

export const WORKSPACE_SECTIONS = [
  { id: "overview",     label: "Overview",             icon: "◈" },
  { id: "challenge",    label: "Challenge",            icon: "◇" },
  { id: "research",     label: "Research",             icon: "◎" },
  { id: "competitors",  label: "Competitors",          icon: "⊕" },
  { id: "ideas",        label: "Ideas",                icon: "✦" },
  { id: "architecture", label: "Architecture",         icon: "▣" },
  { id: "docs",         label: "Documentation",        icon: "☰" },
  { id: "timeline",     label: "Timeline",             icon: "◈" },
  { id: "exports",      label: "Exports",              icon: "⊞" },
];

// ─── Workspace Shell Layout ────────────────────────────────────────────────────

export default function ProjectWorkspaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const params = useParams();
  const projectId = params.id as string;
  const router = useRouter();
  const pathname = usePathname();
  const [project, setProject] = useState<Project | null>(null);

  // Determine active section from URL path
  const activeSection = WORKSPACE_SECTIONS.find(
    (s) => pathname.endsWith(`/${s.id}`)
  )?.id || "overview";

  useEffect(() => {
    if (!projectId) return;
    getProject(projectId).then((res) => {
      if (res.success) setProject(res.data.project);
    });
  }, [projectId]);

  if (!project) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", background: "transparent", color: "var(--text-2)" }}>
      Loading...
    </div>
  );

  return (
    <PipelineProvider projectName={project.name}>
      <ToastProvider>
        <div style={{ display: "flex", minHeight: "100vh", background: "transparent", position: "relative", zIndex: 1 }}>
          {/* Pipeline sidebar */}
          <PipelineSidebar />

          {/* Main workspace */}
          <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
            {/* Top bar */}
            <div style={{ display: "flex", alignItems: "center", gap: "12px", padding: "12px 20px", borderBottom: "1px solid var(--border)", background: "var(--surface-0)" }}>
              <button onClick={() => router.push("/projects")} className="btn btn-ghost" style={{ padding: "6px 12px", fontSize: "12px" }}>
                ← Projects
              </button>
              <div style={{ width: "1px", height: "18px", background: "var(--border)" }} />
              <span style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: "14px", color: "var(--text-1)", letterSpacing: "-0.01em" }}>
                {project.name}
              </span>
              <span className="badge" style={{ fontSize: "10px", padding: "2px 8px" }}>
                {project.status}
              </span>
            </div>

            {/* Workspace navigation */}
            <div style={{ display: "flex", gap: "0", borderBottom: "1px solid var(--border)", padding: "0 16px", background: "transparent" }}>
              {WORKSPACE_SECTIONS.map((section) => (
                <button
                  key={section.id}
                  onClick={() => router.push(`/projects/${projectId}/${section.id === "overview" ? "" : section.id}`)}
                  style={{
                    display: "flex", alignItems: "center", gap: "6px",
                    padding: "10px 14px", fontSize: "11px", fontWeight: 500,
                    color: activeSection === section.id ? "var(--blue-light)" : "var(--text-3)",
                    borderBottom: activeSection === section.id ? "2px solid var(--blue)" : "2px solid transparent",
                    background: "transparent", cursor: "pointer", borderTop: "none",
                    borderLeft: "none", borderRight: "none",
                    transition: "color 0.15s, border-color 0.15s", whiteSpace: "nowrap",
                  }}
                >
                  <span style={{ fontSize: "12px" }}>{section.icon}</span>
                  {section.label}
                </button>
              ))}
            </div>

            {/* Page content */}
            <PipelineSync projectId={projectId}>
              <div style={{ flex: 1, overflow: "auto", padding: "24px" }}>
                {children}
              </div>
            </PipelineSync>
          </div>
        </div>
        <CommandPalette projectId={projectId} />
      </ToastProvider>
    </PipelineProvider>
  );
}

// ─── Pipeline Sync ─────────────────────────────────────────────────────────────

function PipelineSync({ projectId, children }: { projectId: string; children: React.ReactNode }) {
  const { state, dispatch } = usePipeline();

  useEffect(() => {
    if (!projectId) return;
    // Check which specialists have data and mark them as completed
    const checkStages = async () => {
      const checks = [
        { id: "challenge", url: `/projects/${projectId}/challenge` },
        { id: "research", url: `/projects/${projectId}/research` },
        { id: "competitors", url: `/projects/${projectId}/competitors` },
        { id: "ideas", url: `/projects/${projectId}/ideas` },
        { id: "architecture", url: `/projects/${projectId}/architecture` },
        { id: "docs", url: `/projects/${projectId}/docs` },
      ];
      for (const check of checks) {
        try {
          const res = await fetch(check.url);
          if (res.ok) {
            const d = await res.json();
            if (d?.data && !d.error) {
              dispatch({ type: "SET_STAGE_STATUS", stageId: check.id, status: "completed" });
            }
          }
        } catch {}
      }
    };
    checkStages();
  }, [projectId]);

  return <>{children}</>;
}
