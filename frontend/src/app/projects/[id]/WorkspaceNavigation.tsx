"use client";

import Link from "next/link";
import { WORKSPACE_SECTIONS } from "./layout";

export default function WorkspaceNavigation({
  projectId,
  activeSection,
}: {
  projectId: string;
  activeSection: string;
}) {
  return (
    <nav style={{
      display: "flex", gap: "0", padding: "0 12px",
      borderBottom: "1px solid var(--border)",
      background: "var(--surface-0)", overflowX: "auto",
      scrollbarWidth: "none",
    }}>
      {WORKSPACE_SECTIONS.map(section => {
        const isActive = activeSection === section.id;
        return (
          <Link
            key={section.id}
            href={`/projects/${projectId}/${section.id}`}
            style={{
              display: "flex", alignItems: "center", gap: "6px",
              padding: "10px 14px", textDecoration: "none",
              fontSize: "12px", fontWeight: isActive ? 600 : 400,
              color: isActive ? "var(--blue-light)" : "var(--text-3)",
              borderBottom: isActive ? "2px solid var(--blue)" : "2px solid transparent",
              transition: "all 0.15s", whiteSpace: "nowrap",
              letterSpacing: "0.02em",
            }}
            onMouseEnter={e => { if (!isActive) (e.currentTarget).style.color = "var(--text-2)"; }}
            onMouseLeave={e => { if (!isActive) (e.currentTarget).style.color = "var(--text-3)"; }}
          >
            <span style={{ fontSize: "12px" }}>{section.icon}</span>
            {section.label}
          </Link>
        );
      })}
    </nav>
  );
}
