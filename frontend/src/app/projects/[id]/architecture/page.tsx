"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { getArchitecture, generateArchitecture, type ArchitectureData } from "@/services/api";
import { Card, Section, Pill, Grid, LoadingState } from "@/components/shared/ui";
import MermaidViewer from "@/components/diagrams/MermaidViewer";
import LiveArchitecture from "@/components/diagrams/LiveArchitecture";
import GuidedSection from "@/components/shared/GuidedSection";
import { useToast } from "@/components/shared/Toast";
import { HiOutlineRefresh } from "react-icons/hi";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const _MermaidBlock = ({ code }: { code: string }) => {
  if (!code || code === "") return null;
  return <MermaidViewer code={code} />;
};

export default function ArchitecturePage() {
  const params = useParams();
  const projectId = params.id as string;
  const [arch, setArch] = useState<ArchitectureData | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const toast = useToast();

  const fetchArch = async () => {
    setLoading(true);
    const res = await getArchitecture(projectId);
    if (res.success && res.data?.architecture?.system_overview) {
      setArch(res.data.architecture);
    } else {
      setArch(null);
    }
    setLoading(false);
  };

  useEffect(() => { if (projectId) fetchArch(); }, [projectId]);

  const handleGenerate = async () => {
    setGenerating(true);
    toast.addToast({ type: "info", title: "Generating architecture...", message: "The Solution Architect is designing your system." });
    const res = await generateArchitecture(projectId);
    setGenerating(false);
    if (res.success && res.data?.architecture?.system_overview) {
      setArch(res.data.architecture);
      toast.addToast({ type: "success", title: "Architecture generated!", message: "Your complete technical blueprint is ready." });
    } else {
      toast.addToast({ type: "error", title: "Generation failed", message: "Could not generate architecture. Please try again." });
    }
  };

  if (loading) return <LoadingState label="Loading architecture..." />;

  if (!arch) return (
    <GuidedSection
      title="Architecture Blueprint"
      status={generating ? "generating" : "idle"}
      actionLabel="Generate Architecture"
      onAction={handleGenerate}
      estimatedTime="~20 seconds"
      whatProduced="Complete technical blueprint with system diagrams, components, database design, API contracts, and deployment plan"
      unlocks="Documentation generation and export"
      logLines={generating ? [
        { text: "Analyzing selected idea...", type: "info" },
        { text: "Designing system architecture...", type: "ai" },
        { text: "Creating component hierarchy...", type: "synthesis" },
        { text: "Generating database schema...", type: "search" },
        { text: "Building Mermaid diagrams...", type: "synthesis" },
        { text: "Ready for review", type: "done" },
      ] : undefined}
    />
  );

  const d = arch as any;

  return (
    <div>
      <div className="anim-fade-up" style={{ marginBottom: "20px" }}>
        <span className="sec-num">[ ARCHITECTURE ]</span>
        <h2 className="d4" style={{ color: "var(--text-1)", marginBottom: "4px" }}>Architecture Blueprint</h2>
        <button onClick={handleGenerate} disabled={generating} className="btn btn-ghost" style={{ fontSize: "11px", padding: "6px 14px", display: "inline-flex", alignItems: "center", gap: "4px" }}>
          <HiOutlineRefresh size={12} /> {generating ? "Generating..." : "Regenerate"}
        </button>
      </div>

      <div className="anim-fade-up-1" style={{ marginBottom: "20px" }}>
        <LiveArchitecture arch={d} />
      </div>

      {d.system_overview && (
        <div className="card" style={{ marginBottom: "20px", borderLeft: "2px solid var(--blue)", background: "linear-gradient(135deg, rgba(61,124,246,0.04) 0%, transparent 100%)" }}>
          <span className="label" style={{ color: "var(--blue-light)", marginBottom: "8px", display: "block" }}>System Overview</span>
          <p style={{ fontSize: "13px", color: "var(--text-2)", lineHeight: 1.7 }}>{d.system_overview}</p>
          {d.architecture_rationale && <p style={{ fontSize: "12px", color: "var(--text-3)", lineHeight: 1.6, marginTop: "8px", fontStyle: "italic" }}>{d.architecture_rationale}</p>}
        </div>
      )}

      {d.components && d.components.length > 0 && (
        <Section title="Components" color="var(--blue)">
          <Grid cols={2} gap="10px">
            {d.components.map((c: any, i: number) => (
              <Card key={i} hover style={{ padding: "16px" }}>
                <h4 style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "4px" }}>{c.name}</h4>
                {c.tech && <Pill color="var(--blue-light)" bg="var(--blue-dim)" style={{ marginBottom: "6px" }}>{c.tech}</Pill>}
                <p style={{ fontSize: "11px", color: "var(--text-2)" }}>{c.purpose || c.description}</p>
              </Card>
            ))}
          </Grid>
        </Section>
      )}

      {d.mermaid_system && <Section title="System Diagram" color="var(--lime)"><_MermaidBlock code={d.mermaid_system} /></Section>}
      {d.mermaid_request_flow && <Section title="Request Flow" color="var(--sky)"><_MermaidBlock code={d.mermaid_request_flow} /></Section>}
      {d.mermaid_data_flow && <Section title="Data Flow" color="var(--info)"><_MermaidBlock code={d.mermaid_data_flow} /></Section>}
      {d.mermaid_deployment && <Section title="Deployment" color="var(--lime)"><_MermaidBlock code={d.mermaid_deployment} /></Section>}

      {d.frontend && d.frontend.framework && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "20px" }}>
          <Card>
            <span className="label" style={{ color: "var(--blue-light)", marginBottom: "8px", display: "block" }}>Frontend</span>
            <p style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "8px" }}>{d.frontend.framework}</p>
            {d.frontend.routing && d.frontend.routing.length > 0 && (
              <div><span className="label" style={{ marginBottom: "4px", display: "block" }}>Routes</span>
                <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                  {d.frontend.routing.map((r: any, i: number) => (
                    <div key={i} style={{ fontSize: "10px", color: "var(--text-2)", fontFamily: "var(--font-mono)" }}>{r.path} → {r.component}</div>
                  ))}
                </div>
              </div>
            )}
            {d.frontend.component_hierarchy && d.frontend.component_hierarchy.length > 0 && (
              <div style={{ marginTop: "8px" }}><span className="label" style={{ marginBottom: "4px", display: "block" }}>Components</span>
                <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
                  {d.frontend.component_hierarchy.map((c: string, i: number) => <Pill key={i}>{c}</Pill>)}
                </div>
              </div>
            )}
          </Card>
          {d.backend && d.backend.framework && (
            <Card>
              <span className="label" style={{ color: "var(--lime)", marginBottom: "8px", display: "block" }}>Backend</span>
              <p style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "8px" }}>{d.backend.framework}</p>
              {d.backend.modules && d.backend.modules.length > 0 && (
                <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
                  {d.backend.modules.map((m: string, i: number) => <Pill key={i}>{m}</Pill>)}
                </div>
              )}
            </Card>
          )}
        </div>
      )}

      {d.database && d.database.entities && d.database.entities.length > 0 && (
        <Section title="Database Design" color="var(--lime)">
          {d.database.mermaid_er && <_MermaidBlock code={d.database.mermaid_er} />}
          {d.database.entities.map((e: any, i: number) => (
            <Card key={i} style={{ padding: "14px", marginBottom: "8px" }}>
              <h4 style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "6px" }}>{e.name}</h4>
              {e.fields && e.fields.length > 0 && (
                <div style={{ fontSize: "10px", fontFamily: "var(--font-mono)" }}>
                  {e.fields.map((f: any, j: number) => (
                    <div key={j} style={{ display: "flex", gap: "8px", padding: "2px 0" }}>
                      <span style={{ color: "var(--blue-light)", minWidth: "100px" }}>{f.name}</span>
                      <span style={{ color: "var(--lime)" }}>{f.type}</span>
                      {f.pk && <span style={{ color: "var(--warning)" }}>PK</span>}
                      {f.unique && <span style={{ color: "var(--info)" }}>UNIQUE</span>}
                    </div>
                  ))}
                </div>
              )}
            </Card>
          ))}
        </Section>
      )}

      {d.api_contracts && d.api_contracts.length > 0 && (
        <Section title="API Contracts" color="var(--blue-light)">
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {d.api_contracts.map((ep: any, i: number) => (
              <Card key={i} style={{ padding: "14px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                  <Pill color={ep.method === "GET" ? "var(--lime)" : ep.method === "POST" ? "var(--blue-light)" : "var(--warning)"} bg="var(--surface-2)">{ep.method}</Pill>
                  <code style={{ fontSize: "12px", color: "var(--text-1)" }}>{ep.path}</code>
                </div>
                {ep.description && <p style={{ fontSize: "11px", color: "var(--text-2)", marginBottom: "4px" }}>{ep.description}</p>}
              </Card>
            ))}
          </div>
        </Section>
      )}

      {d.authentication && d.authentication.provider && (
        <Section title="Authentication" color="var(--info)">
          <Card>
            <Pill color="var(--blue-light)" bg="var(--blue-dim)" style={{ marginBottom: "6px" }}>{d.authentication.provider}</Pill>
            {d.authentication.model && <p style={{ fontSize: "12px", color: "var(--text-2)" }}>{d.authentication.model}</p>}
          </Card>
        </Section>
      )}

      {d.external_services && d.external_services.length > 0 && (
        <Section title="External Services" color="var(--sky)">
          <Grid gap="8px">
            {d.external_services.map((s: any, i: number) => (
              <Card key={i} style={{ padding: "14px" }}>
                <h4 style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "4px" }}>{s.name}</h4>
                <p style={{ fontSize: "11px", color: "var(--text-2)" }}>{s.purpose}</p>
                {s.fallback && <p style={{ fontSize: "10px", color: "var(--text-3)" }}>Fallback: {s.fallback}</p>}
              </Card>
            ))}
          </Grid>
        </Section>
      )}

      {d.tradeoffs && d.tradeoffs.length > 0 && (
        <Section title="Trade-offs" color="var(--warning)">
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {d.tradeoffs.map((t: any, i: number) => (
              <Card key={i} accent="var(--warning)" style={{ padding: "16px" }}>
                <h4 style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "4px" }}>{t.decision}</h4>
                <p style={{ fontSize: "11px", color: "var(--text-2)", marginBottom: "6px" }}>{t.rationale}</p>
                {t.alternatives && <p style={{ fontSize: "10px", color: "var(--text-3)" }}>Alternatives: {t.alternatives.join(", ")}</p>}
                {t.pros && <p style={{ fontSize: "10px", color: "var(--lime)" }}>Pros: {t.pros.join("; ")}</p>}
                {t.cons && <p style={{ fontSize: "10px", color: "var(--error)" }}>Cons: {t.cons.join("; ")}</p>}
              </Card>
            ))}
          </div>
        </Section>
      )}

      {d.review && d.review.weak_points && d.review.weak_points.length > 0 && (
        <Section title="Architecture Review" color="var(--error)">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            <Card accent="var(--error)">
              <span className="label" style={{ color: "var(--error)", marginBottom: "6px", display: "block" }}>Weak Points</span>
              {d.review.weak_points.map((w: string, i: number) => <p key={i} style={{ fontSize: "11px", color: "var(--text-2)", marginBottom: "2px" }}>· {w}</p>)}
            </Card>
            {d.review.failure_modes && d.review.failure_modes.length > 0 && (
              <Card accent="var(--warning)">
                <span className="label" style={{ color: "var(--warning)", marginBottom: "6px", display: "block" }}>Failure Modes</span>
                {d.review.failure_modes.map((f: string, i: number) => <p key={i} style={{ fontSize: "11px", color: "var(--text-2)", marginBottom: "2px" }}>· {f}</p>)}
              </Card>
            )}
          </div>
        </Section>
      )}

      {d.scalability && d.scalability.hackathon_version && (
        <Section title="Scalability" color="var(--lime)">
          <Grid cols={2} gap="12px">
            <Card accent="var(--lime)">
              <span className="label" style={{ color: "var(--lime)", marginBottom: "6px", display: "block" }}>Hackathon Version</span>
              <p style={{ fontSize: "12px", color: "var(--text-2)" }}>{d.scalability.hackathon_version}</p>
            </Card>
            <Card>
              <span className="label" style={{ color: "var(--blue-light)", marginBottom: "6px", display: "block" }}>Production Version</span>
              <p style={{ fontSize: "12px", color: "var(--text-2)" }}>{d.scalability.production_version}</p>
            </Card>
          </Grid>
        </Section>
      )}
    </div>
  );
}
