"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { Card, Section, Pill, SeverityBadge, Grid, LoadingState } from "@/components/shared/ui";
import MermaidViewer from "@/components/diagrams/MermaidViewer";
import GuidedSection from "@/components/shared/GuidedSection";

// Simple Mermaid viewer component
function MermaidBlock({ code }: { code: string }) {
  if (!code || code === "") return null;
  return <MermaidViewer code={code} />;
}

export default function ArchitecturePage() {
  const params = useParams();
  const projectId = params.id as string;
  const [arch, setArch] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!projectId) return;
    setLoading(true);
    fetch(`/api/v1/projects/${projectId}/architecture`).then(r => r.json()).then(d => { if (d?.data) setArch(d.data); }).catch(() => {}).finally(() => setLoading(false));
  }, [projectId]);

  if (loading) return <LoadingState label="Loading architecture..." />;
  if (!arch) return <LoadingState label="Generate architecture first..." />;

  return (
    <div>
      <div className="anim-fade-up" style={{ marginBottom: "20px" }}>
        <span className="sec-num">[ ARCHITECTURE ]</span>
        <h2 className="d4" style={{ color: "var(--text-1)", marginBottom: "4px" }}>Architecture Blueprint</h2>
      </div>

      {/* System Overview */}
      {arch.system_overview && (
        <div className="anim-fade-up-1 card" style={{ marginBottom: "20px", borderLeft: "2px solid var(--blue)", background: "linear-gradient(135deg, rgba(61,124,246,0.04) 0%, transparent 100%)" }}>
          <span className="label" style={{ color: "var(--blue-light)", marginBottom: "8px", display: "block" }}>System Overview</span>
          <p style={{ fontSize: "13px", color: "var(--text-2)", lineHeight: 1.7 }}>{arch.system_overview}</p>
          {arch.architecture_rationale && <p style={{ fontSize: "12px", color: "var(--text-3)", lineHeight: 1.6, marginTop: "8px", fontStyle: "italic" }}>{arch.architecture_rationale}</p>}
        </div>
      )}

      {/* Components */}
      {arch.components?.length > 0 && (
        <Section title="Components" icon="🏗️" color="var(--blue)">
          <Grid cols={2} gap="10px">
            {arch.components.map((c: any, i: number) => (
              <Card key={i} hover style={{ padding: "16px" }}>
                <h4 style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "4px" }}>{c.name}</h4>
                {c.tech && <Pill color="var(--blue-light)" bg="var(--blue-dim)" style={{ marginBottom: "6px" }}>{c.tech}</Pill>}
                <p style={{ fontSize: "11px", color: "var(--text-2)" }}>{c.purpose || c.description}</p>
              </Card>
            ))}
          </Grid>
        </Section>
      )}

      {/* Mermaid Diagrams */}
      {arch.mermaid_system && <Section title="System Diagram" icon="📊" color="var(--lime)"><MermaidBlock code={arch.mermaid_system} /></Section>}
      {arch.mermaid_request_flow && <Section title="Request Flow" icon="🔄" color="var(--sky)"><MermaidBlock code={arch.mermaid_request_flow} /></Section>}
      {arch.mermaid_data_flow && <Section title="Data Flow" icon="📡" color="var(--info)"><MermaidBlock code={arch.mermaid_data_flow} /></Section>}
      {arch.mermaid_deployment && <Section title="Deployment" icon="🚀" color="var(--lime)"><MermaidBlock code={arch.mermaid_deployment} /></Section>}

      {/* Frontend + Backend */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "20px" }}>
        {arch.frontend?.framework && (
          <Card>
            <span className="label" style={{ color: "var(--blue-light)", marginBottom: "8px", display: "block" }}>Frontend</span>
            <p style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "8px" }}>{arch.frontend.framework}</p>
            {arch.frontend.routing?.length > 0 && (
              <div><span className="label" style={{ marginBottom: "4px", display: "block" }}>Routes</span>
                <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                  {arch.frontend.routing.map((r: any, i: number) => (
                    <div key={i} style={{ fontSize: "10px", color: "var(--text-2)", fontFamily: "var(--font-mono)" }}>{r.path} → {r.component}</div>
                  ))}
                </div>
              </div>
            )}
            {arch.frontend.component_hierarchy?.length > 0 && (
              <div style={{ marginTop: "8px" }}><span className="label" style={{ marginBottom: "4px", display: "block" }}>Components</span>
                <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
                  {arch.frontend.component_hierarchy.map((c: string, i: number) => <Pill key={i}>{c}</Pill>)}
                </div>
              </div>
            )}
          </Card>
        )}
        {arch.backend?.framework && (
          <Card>
            <span className="label" style={{ color: "var(--lime)", marginBottom: "8px", display: "block" }}>Backend</span>
            <p style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "8px" }}>{arch.backend.framework}</p>
            {arch.backend.modules?.length > 0 && (
              <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
                {arch.backend.modules.map((m: string, i: number) => <Pill key={i}>{m}</Pill>)}
              </div>
            )}
          </Card>
        )}
      </div>

      {/* Database */}
      {arch.database?.entities?.length > 0 && (
        <Section title="Database Design" icon="🗄️" color="var(--lime)">
          {arch.database.mermaid_er && <MermaidBlock code={arch.database.mermaid_er} />}
          {arch.database.entities.map((e: any, i: number) => (
            <Card key={i} style={{ padding: "14px", marginBottom: "8px" }}>
              <h4 style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "6px" }}>{e.name}</h4>
              {e.fields?.length > 0 && (
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

      {/* API Contracts */}
      {arch.api_contracts?.length > 0 && (
        <Section title="API Contracts" icon="🔌" color="var(--blue-light)">
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {arch.api_contracts.map((ep: any, i: number) => (
              <Card key={i} style={{ padding: "14px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                  <Pill color={ep.method === "GET" ? "var(--lime)" : ep.method === "POST" ? "var(--blue-light)" : "var(--warning)"} bg="var(--surface-2)">
                    {ep.method}
                  </Pill>
                  <code style={{ fontSize: "12px", color: "var(--text-1)" }}>{ep.path}</code>
                </div>
                {ep.description && <p style={{ fontSize: "11px", color: "var(--text-2)", marginBottom: "4px" }}>{ep.description}</p>}
              </Card>
            ))}
          </div>
        </Section>
      )}

      {/* Authentication */}
      {arch.authentication?.provider && (
        <Section title="Authentication" icon="🔐" color="var(--info)">
          <Card>
            <Pill color="var(--blue-light)" bg="var(--blue-dim)" style={{ marginBottom: "6px" }}>{arch.authentication.provider}</Pill>
            {arch.authentication.model && <p style={{ fontSize: "12px", color: "var(--text-2)" }}>{arch.authentication.model}</p>}
          </Card>
        </Section>
      )}

      {/* External Services */}
      {arch.external_services?.length > 0 && (
        <Section title="External Services" icon="🔗" color="var(--sky)">
          <Grid gap="8px">
            {arch.external_services.map((s: any, i: number) => (
              <Card key={i} style={{ padding: "14px" }}>
                <h4 style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "4px" }}>{s.name}</h4>
                <p style={{ fontSize: "11px", color: "var(--text-2)" }}>{s.purpose}</p>
                {s.fallback && <p style={{ fontSize: "10px", color: "var(--text-3)" }}>Fallback: {s.fallback}</p>}
              </Card>
            ))}
          </Grid>
        </Section>
      )}

      {/* Trade-offs */}
      {arch.tradeoffs?.length > 0 && (
        <Section title="Trade-offs" icon="⚖️" color="var(--warning)">
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {arch.tradeoffs.map((t: any, i: number) => (
              <Card key={i} accent="var(--warning)" style={{ padding: "16px" }}>
                <h4 style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-1)", marginBottom: "4px" }}>{t.decision}</h4>
                <p style={{ fontSize: "11px", color: "var(--text-2)", marginBottom: "6px" }}>{t.rationale}</p>
                {t.alternatives?.length > 0 && <p style={{ fontSize: "10px", color: "var(--text-3)" }}>Alternatives: {t.alternatives.join(", ")}</p>}
                {t.pros?.length > 0 && <p style={{ fontSize: "10px", color: "var(--lime)" }}>Pros: {t.pros.join("; ")}</p>}
                {t.cons?.length > 0 && <p style={{ fontSize: "10px", color: "var(--error)" }}>Cons: {t.cons.join("; ")}</p>}
              </Card>
            ))}
          </div>
        </Section>
      )}

      {/* Architecture Review */}
      {arch.review?.weak_points?.length > 0 && (
        <Section title="Architecture Review" icon="🔍" color="var(--error)">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            <Card accent="var(--error)">
              <span className="label" style={{ color: "var(--error)", marginBottom: "6px", display: "block" }}>Weak Points</span>
              {(arch.review.weak_points as string[]).map((w: string, i: number) => <p key={i} style={{ fontSize: "11px", color: "var(--text-2)", marginBottom: "2px" }}>· {w}</p>)}
            </Card>
            {arch.review.failure_modes?.length > 0 && (
              <Card accent="var(--warning)">
                <span className="label" style={{ color: "var(--warning)", marginBottom: "6px", display: "block" }}>Failure Modes</span>
                {(arch.review.failure_modes as string[]).map((f: string, i: number) => <p key={i} style={{ fontSize: "11px", color: "var(--text-2)", marginBottom: "2px" }}>· {f}</p>)}
              </Card>
            )}
          </div>
        </Section>
      )}

      {/* Scalability */}
      {arch.scalability?.hackathon_version && (
        <Section title="Scalability" icon="📈" color="var(--lime)">
          <Grid cols={2} gap="12px">
            <Card accent="var(--lime)">
              <span className="label" style={{ color: "var(--lime)", marginBottom: "6px", display: "block" }}>Hackathon Version</span>
              <p style={{ fontSize: "12px", color: "var(--text-2)" }}>{arch.scalability.hackathon_version}</p>
            </Card>
            <Card>
              <span className="label" style={{ color: "var(--blue-light)", marginBottom: "6px", display: "block" }}>Production Version</span>
              <p style={{ fontSize: "12px", color: "var(--text-2)" }}>{arch.scalability.production_version}</p>
            </Card>
          </Grid>
        </Section>
      )}
    </div>
  );
}
