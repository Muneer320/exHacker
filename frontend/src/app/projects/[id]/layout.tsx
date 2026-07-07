"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, usePathname, useRouter } from "next/navigation";
import { getProject, Project } from "@/services/api";
import { PipelineProvider } from "@/components/pipeline/PipelineContext";
import PipelineSidebar from "@/components/pipeline/PipelineSidebar";
import WorkspaceNavigation from "./WorkspaceNavigation";
import { ToastProvider } from "@/components/shared/Toast";

// ─── Navigation sections ──────────────────────────────────────────────────────

export const WORKSPACE_SECTIONS = [
  { id: "overview",     label: "Overview",             icon: "◈" },
  { id: "challenge",    label: "Challenge",            icon: "🧠" },
  { id: "research",     label: "Research",             icon: "🔍" },
  { id: "competitors",  label: "Competitors",          icon: "🎯" },
  { id: "ideas",        label: "Ideas",                icon: "💡" },
  { id: "architecture", label: "Architecture",         icon: "🏗️" },
  { id: "docs",         label: "Documentation",        icon: "📝" },
  { id: "timeline",     label: "Timeline",             icon: "⏱" },
  { id: "exports",      label: "Exports",              icon: "📦" },
];

// ─── Workspace Shell Layout ────────────────────────────────────────────────────

export default function ProjectWorkspaceLayout({ children }: { children: React.ReactNode }) {
  const params = useParams();
  const pathname = usePathname();
  const router = useRouter();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);

  // Determine active section from pathname
  const activeSection = pathname.split("/").pop() || "overview";
  // If it's just /projects/[id] (no section), redirect to overview
  const isRoot = !WORKSPACE_SECTIONS.find(s => s.id === activeSection);

  useEffect(() => {
    if (isRoot && projectId) {
      router.replace(`/projects/${projectId}/overview`);
      return;
    }
    if (!projectId) return;
    setLoading(true);
    getProject(projectId).then(res => {
      if (res.success) setProject(res.data.project);
    }).finally(() => setLoading(false));
  }, [projectId, isRoot, router]);

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", background: "var(--black)" }}>
      <div className="spinner" />
    </div>
  );

  if (!project) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", background: "var(--black)", color: "var(--text-2)" }}>
      Project not found
    </div>
  );

  return (
    <PipelineProvider projectName={project.name}>
      <ToastProvider>
        <div style={{ display: "flex", minHeight: "100vh", background: "var(--black)" }}>
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
          <WorkspaceNavigation
            projectId={projectId}
            activeSection={activeSection}
          />

          {/* Page content */}
          <div style={{ flex: 1, overflow: "auto", padding: "24px" }}>
            {children}
          </div>
        </div>
      </div></ToastProvider>
    </PipelineProvider>
  );
}
