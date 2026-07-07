"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { getProject, Project } from "@/services/api";

export default function OverviewPage() {
  const params = useParams();
  const projectId = params.id as string;
  const [project, setProject] = useState<Project | null>(null);

  useEffect(() => {
    if (!projectId) return;
    getProject(projectId).then(res => {
      if (res.success) setProject(res.data.project);
    });
  }, [projectId]);

  if (!project) return <div className="spinner" />;

  return (
    <div>
      <div className="anim-fade-up" style={{ marginBottom: "24px" }}>
        <span className="sec-num" style={{ marginBottom: "8px" }}>[ OVERVIEW ]</span>
        <h2 className="d4" style={{ color: "var(--text-1)", marginBottom: "8px" }}>{project.name}</h2>
        <p className="body-md">{project.idea}</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px" }}>
        <div className="card">
          <span className="label">Status</span>
          <p style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-1)" }}>{project.status}</p>
        </div>
        <div className="card">
          <span className="label">Created</span>
          <p style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-1)" }}>
            {new Date(project.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="card">
          <span className="label">Specialists</span>
          <p style={{ fontSize: "16px", fontWeight: 600, color: "var(--blue-light)" }}>7</p>
        </div>
      </div>
    </div>
  );
}
