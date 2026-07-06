'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  ArrowLeft,
  Zap,
  ExternalLink,
  Star,
  Compass,
  Database,
  GitFork,
  Lightbulb,
} from 'lucide-react';
import { getProject, startResearch, getResearch, generateDirections, getDirections, selectDirection, generateBlueprint, Project, ResearchData, Direction, BlueprintData } from '@/services/api';

type Tab = 'overview' | 'research' | 'directions' | 'blueprint';

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [researchData, setResearchData] = useState<ResearchData | null>(null);
  const [researchLoading, setResearchLoading] = useState(false);
  const [directions, setDirections] = useState<Direction[]>([]);
  const [directionsLoading, setDirectionsLoading] = useState(false);
  const [selectedDirId, setSelectedDirId] = useState<string | null>(null);
  const [blueprint, setBlueprint] = useState<BlueprintData | null>(null);
  const [blueprintLoading, setBlueprintLoading] = useState(false);

  useEffect(() => {
    if (!projectId) return;
    getProject(projectId).then((res) => {
      if (res.success) {
        setProject(res.data.project);
        loadResearch();
        loadDirections();
      } else {
        setError(res.error?.message || 'Project not found.');
      }
      setLoading(false);
    });
  }, [projectId]);

  const loadResearch = useCallback(async () => {
    const res = await getResearch(projectId);
    if (res.success) {
      setResearchData(res.data);
    }
  }, [projectId]);

  const handleStartResearch = async () => {
    setResearchLoading(true);
    const res = await startResearch(projectId);
    if (res.success) {
      setResearchData(res.data);
    }
    setResearchLoading(false);
  };

  const handleGenerateDirections = async () => {
    setDirectionsLoading(true);
    const res = await generateDirections(projectId);
    if (res.success) {
      setDirections(res.data.directions);
      const sel = res.data.directions.find(d => d.is_selected);
      if (sel) setSelectedDirId(sel.id);
    }
    setDirectionsLoading(false);
  };

  const handleSelectDirection = async (dirId: string) => {
    setSelectedDirId(dirId);
    const res = await selectDirection(projectId, dirId);
    if (res.success) {
      setDirections(prev => prev.map(d => ({ ...d, is_selected: d.id === dirId })));
    }
  };

  const handleGenerateBlueprint = async () => {
    setBlueprintLoading(true);
    const res = await generateBlueprint(projectId);
    if (res.success) {
      setBlueprint(res.data.blueprint);
    }
    setBlueprintLoading(false);
  };

  // Load directions on mount
  const loadDirections = useCallback(async () => {
    const res = await getDirections(projectId);
    if (res.success) {
      setDirections(res.data.directions);
      const sel = res.data.directions.find(d => d.is_selected);
      if (sel) setSelectedDirId(sel.id);
    }
  }, [projectId]);

  if (loading) {
    return (
      <div style={{ background: 'var(--color-app-bg)', minHeight: '100vh', color: 'var(--color-text-primary)', padding: '80px 24px' }}>
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          <div style={{ height: '32px', width: '200px', background: 'var(--color-surface-1)', borderRadius: '8px', marginBottom: '24px', animation: 'pulse-ring 2s ease-in-out infinite' }} />
          <div style={{ height: '200px', background: 'var(--color-surface-1)', borderRadius: '12px', animation: 'pulse-ring 2s ease-in-out infinite' }} />
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div style={{ background: 'var(--color-app-bg)', minHeight: '100vh', color: 'var(--color-text-primary)', padding: '80px 24px' }}>
        <div style={{ maxWidth: '900px', margin: '0 auto', textAlign: 'center', padding: '80px 24px' }}>
          <p style={{ fontSize: '32px', marginBottom: '16px' }}>🔍</p>
          <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>Project not found</h2>
          <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '24px' }}>{error}</p>
          <button onClick={() => router.push('/projects')} style={{ padding: '10px 20px', borderRadius: '8px', border: '1px solid var(--color-border-default)', background: 'transparent', color: 'var(--color-text-secondary)', fontSize: '13px', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <ArrowLeft size={14} /> Back to Projects
          </button>
        </div>
      </div>
    );
  }

  const statusColor = (s: string) => {
    switch (s) {
      case 'draft': return 'var(--color-text-tertiary)';
      case 'processing': return 'var(--color-info)';
      case 'ready': return 'var(--color-success)';
      case 'archived': return 'var(--color-text-disabled)';
      default: return 'var(--color-text-tertiary)';
    }
  };

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Overview', icon: <Compass size={14} /> },
    { id: 'research', label: 'Research', icon: <Lightbulb size={14} /> },
    { id: 'directions', label: 'Directions', icon: <Zap size={14} /> },
    { id: 'blueprint', label: 'Blueprint', icon: <Compass size={14} /> },
  ];

  return (
    <div style={{ background: 'var(--color-app-bg)', minHeight: '100vh', color: 'var(--color-text-primary)' }}>
      {/* Top bar */}
      <div style={{ borderBottom: '1px solid var(--color-border-default)', padding: '12px 24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button onClick={() => router.push('/projects')} style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '6px 10px', borderRadius: '6px', border: 'none', background: 'transparent', color: 'var(--color-text-secondary)', fontSize: '13px', cursor: 'pointer' }}>
          <ArrowLeft size={14} /> Projects
        </button>
        <div style={{ width: '1px', height: '20px', background: 'var(--color-border-default)' }} />
        <Zap size={14} color="var(--color-accent-400)" />
        <span style={{ fontWeight: 600, fontSize: '14px' }}>{project.name}</span>
        <span style={{ padding: '2px 8px', borderRadius: '99px', fontSize: '11px', fontWeight: 500, background: `${statusColor(project.status)}15`, color: statusColor(project.status), textTransform: 'capitalize' }}>
          {project.status}
        </span>
      </div>

      {/* Tab bar */}
      <div style={{ borderBottom: '1px solid var(--color-border-default)', padding: '0 24px', display: 'flex', gap: '0' }}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              display: 'flex', alignItems: 'center', gap: '6px', padding: '12px 16px',
              fontSize: '13px', fontWeight: 500, cursor: 'pointer',
              border: 'none', background: 'transparent',
              color: activeTab === tab.id ? 'var(--color-accent-400)' : 'var(--color-text-secondary)',
              borderBottom: activeTab === tab.id ? '2px solid var(--color-accent-500)' : '2px solid transparent',
              transition: 'all 150ms ease',
            }}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '32px 24px' }}>
        {activeTab === 'overview' && (
          <>
            {/* Idea card */}
            <div style={{ padding: '24px', borderRadius: '12px', background: 'var(--color-surface-1)', border: '1px solid var(--color-border-default)', marginBottom: '24px' }}>
              <p style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>Original Idea</p>
              <p style={{ fontSize: '15px', color: 'var(--color-text-primary)', lineHeight: 1.6 }}>{project.idea}</p>
            </div>

            {/* Research summary if available */}
            {researchData && researchData.summary.total_results > 0 && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
                {[
                  { label: 'Competitors', count: researchData.summary.competitors_found, color: 'var(--color-accent-400)' },
                  { label: 'APIs', count: researchData.summary.apis_found, color: 'var(--color-info)' },
                  { label: 'Open Source', count: researchData.summary.oss_found, color: 'var(--color-success)' },
                ].map((item) => (
                  <div key={item.label} style={{ padding: '16px', borderRadius: '10px', background: 'var(--color-surface-1)', border: '1px solid var(--color-border-default)' }}>
                    <p style={{ fontSize: '24px', fontWeight: 700, color: item.color, marginBottom: '4px' }}>{item.count}</p>
                    <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>{item.label}</p>
                  </div>
                ))}
              </div>
            )}

            {!researchData && project.status === 'draft' && (
              <div style={{ textAlign: 'center', padding: '64px 24px', border: '1px dashed var(--color-border-default)', borderRadius: '16px' }}>
                <p style={{ fontSize: '28px', marginBottom: '12px' }}>🚀</p>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>Research waiting</h3>
                <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '24px' }}>Run research to discover competitors, APIs, and open-source projects.</p>
                <button onClick={handleStartResearch} disabled={researchLoading} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '10px 20px', borderRadius: '8px', border: 'none', background: researchLoading ? 'rgba(124,58,237,0.3)' : 'var(--color-accent-500)', color: '#fff', fontSize: '13px', fontWeight: 600, cursor: researchLoading ? 'default' : 'pointer' }}>
                  {researchLoading ? 'Researching...' : 'Run Research'}
                </button>
              </div>
            )}
          </>
        )}

        {activeTab === 'research' && (
          <ResearchTab
            data={researchData}
            loading={researchLoading}
            onStartResearch={handleStartResearch}
          />
        )}
        {activeTab === 'directions' && (
          <DirectionsTab
            directions={directions}
            loading={directionsLoading}
            selectedId={selectedDirId}
            onGenerate={handleGenerateDirections}
            onSelect={handleSelectDirection}
          />
        )}
        {activeTab === 'blueprint' && (
          <BlueprintTab
            blueprint={blueprint}
            loading={blueprintLoading}
            onGenerate={handleGenerateBlueprint}
          />
        )}
      </div>
    </div>
  );
}

// ─── Research Tab ───────────────────────────────────────────────────────────

function ResearchTab({
  data,
  loading,
  onStartResearch,
}: {
  data: ResearchData | null;
  loading: boolean;
  onStartResearch: () => void;
}) {
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '64px 24px' }}>
        <div style={{ width: '40px', height: '40px', borderRadius: '50%', border: '3px solid rgba(124,58,237,0.2)', borderTopColor: 'var(--color-accent-500)', animation: 'spin 0.8s linear infinite', margin: '0 auto 16px' }} />
        <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>Researching competitors, APIs, and open source projects...</p>
      </div>
    );
  }

  if (!data || data.summary.total_results === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '64px 24px', border: '1px dashed var(--color-border-default)', borderRadius: '16px' }}>
        <p style={{ fontSize: '28px', marginBottom: '12px' }}>🔍</p>
        <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>No research yet</h3>
        <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '24px' }}>
          Search for competitors, APIs, and open-source projects related to your idea.
        </p>
        <button onClick={onStartResearch} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '10px 20px', borderRadius: '8px', border: 'none', background: 'var(--color-accent-500)', color: '#fff', fontSize: '13px', fontWeight: 600, cursor: 'pointer' }}>
          Run Research
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Summary bar */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <SummaryBadge label="Competitors" count={data.summary.competitors_found} color="var(--color-accent-400)" />
        <SummaryBadge label="APIs" count={data.summary.apis_found} color="var(--color-info)" />
        <SummaryBadge label="Open Source" count={data.summary.oss_found} color="var(--color-success)" />
        <SummaryBadge label="Insights" count={data.summary.insights_found} color="var(--color-warning)" />
      </div>

      {data.competitors.length > 0 && (
        <Section title="Competitors" icon={<Star size={14} />} color="var(--color-accent-400)">
          {data.competitors.map((c, i) => (
            <ResultCard key={i} result={c} />
          ))}
        </Section>
      )}

      {data.apis.length > 0 && (
        <Section title="APIs & Integrations" icon={<Database size={14} />} color="var(--color-info)">
          {data.apis.map((c, i) => (
            <ResultCard key={i} result={c} />
          ))}
        </Section>
      )}

      {data.oss_projects.length > 0 && (
        <Section title="Open Source Projects" icon={<GitFork size={14} />} color="var(--color-success)">
          {data.oss_projects.map((c, i) => (
            <ResultCard key={i} result={c} />
          ))}
        </Section>
      )}
    </div>
  );
}

function SummaryBadge({ label, count, color }: { label: string; count: number; color: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 14px', borderRadius: '8px', background: 'var(--color-surface-1)', border: '1px solid var(--color-border-default)' }}>
      <span style={{ fontSize: '18px', fontWeight: 700, color }}>{count}</span>
      <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>{label}</span>
    </div>
  );
}

// ─── Directions Tab ─────────────────────────────────────────────────────────

function DirectionsTab({
  directions,
  loading,
  selectedId,
  onGenerate,
  onSelect,
}: {
  directions: Direction[];
  loading: boolean;
  selectedId: string | null;
  onGenerate: () => void;
  onSelect: (id: string) => void;
}) {
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '64px 24px' }}>
        <div style={{ width: '40px', height: '40px', borderRadius: '50%', border: '3px solid rgba(124,58,237,0.2)', borderTopColor: 'var(--color-accent-500)', animation: 'spin 0.8s linear infinite', margin: '0 auto 16px' }} />
        <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>Generating product directions...</p>
      </div>
    );
  }

  if (directions.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '64px 24px', border: '1px dashed var(--color-border-default)', borderRadius: '16px' }}>
        <p style={{ fontSize: '28px', marginBottom: '12px' }}>🎯</p>
        <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>No directions yet</h3>
        <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '24px' }}>
          Generate product directions based on your research data.
        </p>
        <button onClick={onGenerate} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '10px 20px', borderRadius: '8px', border: 'none', background: 'var(--color-accent-500)', color: '#fff', fontSize: '13px', fontWeight: 600, cursor: 'pointer' }}>
          Generate Directions
        </button>
      </div>
    );
  }

  const hasSelected = !!selectedId;

  return (
    <div>
      {!hasSelected && (
        <div style={{ marginBottom: '20px' }}>
          <button onClick={onGenerate} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '8px 16px', borderRadius: '8px', border: '1px solid var(--color-border-default)', background: 'transparent', color: 'var(--color-text-secondary)', fontSize: '13px', cursor: 'pointer' }}>
            Regenerate
          </button>
        </div>
      )}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {directions.map((d) => (
          <DirectionCard key={d.id} direction={d} isSelected={d.is_selected} onSelect={() => onSelect(d.id)} />
        ))}
      </div>
    </div>
  );
}

function DirectionCard({ direction, isSelected, onSelect }: { direction: Direction; isSelected: boolean; onSelect: () => void }) {
  return (
    <div style={{
      padding: '20px', borderRadius: '12px', background: 'var(--color-surface-1)',
      border: `1px solid ${isSelected ? 'var(--color-accent-500)' : 'var(--color-border-default)'}`,
      transition: 'border-color 150ms ease', opacity: isSelected ? 1 : undefined,
      position: 'relative',
    }}>
      {isSelected && <div style={{ position: 'absolute', top: '12px', right: '12px', background: 'var(--color-accent-500)', color: '#fff', fontSize: '10px', fontWeight: 700, padding: '2px 8px', borderRadius: '99px' }}>SELECTED</div>}
      <div style={{ marginBottom: '12px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '4px' }}>{direction.title}</h3>
        <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', fontStyle: 'italic' }}>{direction.tagline}</p>
      </div>
      {direction.description && (
        <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', lineHeight: 1.5, marginBottom: '12px' }}>{direction.description}</p>
      )}
      <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
        <ScoreBadge label="Innovation" value={direction.innovation_score ?? 0} color="var(--color-accent-400)" />
        <ScoreBadge label="Feasibility" value={direction.feasibility_score ?? 0} color="var(--color-info)" />
        <div style={{ flex: 1 }} />
        {!isSelected && (
          <button onClick={onSelect} style={{ padding: '6px 14px', borderRadius: '8px', border: '1px solid var(--color-accent-500)', background: 'transparent', color: 'var(--color-accent-400)', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}>
            Select Direction
          </button>
        )}
      </div>
    </div>
  );
}

function ScoreBadge({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
      <span style={{ width: '28px', height: '4px', borderRadius: '2px', background: `${color}30`, position: 'relative', overflow: 'hidden', display: 'inline-block' }}>
        <span style={{ position: 'absolute', left: 0, top: 0, height: '100%', width: `${value}%`, background: color, borderRadius: '2px' }} />
      </span>
      <span style={{ fontSize: '12px', color: 'var(--color-text-tertiary)' }}>{label}: {value}</span>
    </div>
  );
}

// ─── Blueprint Tab ──────────────────────────────────────────────────────────

function BlueprintTab({
  blueprint,
  loading,
  onGenerate,
}: {
  blueprint: BlueprintData | null;
  loading: boolean;
  onGenerate: () => void;
}) {
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '64px 24px' }}>
        <div style={{ width: '40px', height: '40px', borderRadius: '50%', border: '3px solid rgba(124,58,237,0.2)', borderTopColor: 'var(--color-accent-500)', animation: 'spin 0.8s linear infinite', margin: '0 auto 16px' }} />
        <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>Generating blueprint...</p>
      </div>
    );
  }

  if (!blueprint) {
    return (
      <div style={{ textAlign: 'center', padding: '64px 24px', border: '1px dashed var(--color-border-default)', borderRadius: '16px' }}>
        <p style={{ fontSize: '28px', marginBottom: '12px' }}>🏗️</p>
        <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>No blueprint yet</h3>
        <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '24px' }}>
          Generate a complete project blueprint with architecture, tech stack, data model, and plan.
        </p>
        <button onClick={onGenerate} style={{ padding: '10px 20px', borderRadius: '8px', border: 'none', background: 'var(--color-accent-500)', color: '#fff', fontSize: '13px', fontWeight: 600, cursor: 'pointer' }}>
          Generate Blueprint
        </button>
      </div>
    );
  }

  const arch = blueprint.architecture as Record<string, unknown> | null;
  const comps = (arch?.components as Array<Record<string, unknown>>) || [];
  const dm = blueprint.data_model as Record<string, unknown> | null;
  const entities = (dm?.entities as Array<Record<string, unknown>>) || [];
  const api = blueprint.api_contracts as Record<string, unknown> | null;
  const endpoints = (api?.endpoints as Array<Record<string, unknown>>) || [];
  const pl = blueprint.plan as Record<string, unknown> | null;
  const phases = (pl?.phases as Array<Record<string, unknown>>) || [];

  return (
    <div>
      {/* Summary cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '12px', marginBottom: '24px' }}>
        <SummaryCard label="Components" value={blueprint.summary.components} color="var(--color-accent-400)" />
        <SummaryCard label="Entities" value={blueprint.summary.entities} color="var(--color-info)" />
        <SummaryCard label="Endpoints" value={blueprint.summary.endpoints} color="var(--color-success)" />
        <SummaryCard label="Tasks" value={blueprint.summary.tasks} color="var(--color-warning)" />
        <SummaryCard label="Est. Hours" value={blueprint.summary.estimated_hours} color="var(--color-accent-200)" />
      </div>

      {/* Architecture Components */}
      {comps.length > 0 && (
        <Section title="Architecture Components" icon={<GitFork size={14} />} color="var(--color-accent-400)">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
            {comps.map((c: Record<string, unknown>, i: number) => (
              <div key={i} style={{ padding: '16px', borderRadius: '10px', background: 'var(--color-surface-1)', border: '1px solid var(--color-border-default)' }}>
                <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '4px' }}>{c.name as string}</h4>
                <p style={{ fontSize: '12px', color: 'var(--color-text-tertiary)', marginBottom: '8px' }}>{c.tech as string}</p>
                <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>{c.description as string}</p>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Data Model */}
      {entities.length > 0 && (
        <Section title="Data Model" icon={<Database size={14} />} color="var(--color-info)">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {entities.map((e: Record<string, unknown>, i: number) => (
              <div key={i} style={{ padding: '14px 16px', borderRadius: '10px', background: 'var(--color-surface-1)', border: '1px solid var(--color-border-default)' }}>
                <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '4px', textTransform: 'capitalize' }}>{e.name as string}</h4>
                <div style={{ fontSize: '12px', color: 'var(--color-text-tertiary)' }}>
                  {(e.fields as Array<Record<string, string>>)?.map((f, j) => (
                    <span key={j} style={{ marginRight: '12px' }}>{f.name}: {f.type}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* API Contracts */}
      {endpoints.length > 0 && (
        <Section title="API Endpoints" icon={<GitFork size={14} />} color="var(--color-success)">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {endpoints.slice(0, 8).map((ep: Record<string, unknown>, i: number) => (
              <div key={i} style={{ display: 'flex', gap: '8px', padding: '8px 12px', borderRadius: '6px', background: 'var(--color-surface-1)', border: '1px solid var(--color-border-default)' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-accent-400)', minWidth: '48px' }}>{ep.method as string}</span>
                <span style={{ fontSize: '12px', color: 'var(--color-text-primary)', fontFamily: 'monospace' }}>{ep.path as string}</span>
                <span style={{ fontSize: '12px', color: 'var(--color-text-tertiary)' }}>{ep.description as string}</span>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Plan */}
      {phases.length > 0 && (
        <Section title="Implementation Plan" icon={<Star size={14} />} color="var(--color-warning)">
          {phases.slice(0, 3).map((phase: Record<string, unknown>, i: number) => (
            <div key={i} style={{ marginBottom: '12px', padding: '14px 16px', borderRadius: '10px', background: 'var(--color-surface-1)', border: '1px solid var(--color-border-default)' }}>
              <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>Phase {i + 1}: {phase.name as string}</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {(phase.tasks as Array<Record<string, unknown>>)?.slice(0, 3).map((t: Record<string, unknown>, j: number) => (
                  <div key={j} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                    <span>{t.title as string}</span>
                    <span style={{ color: 'var(--color-text-tertiary)' }}>{t.estimated_hours as number}h</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </Section>
      )}
    </div>
  );
}

function SummaryCard({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div style={{ padding: '16px', borderRadius: '10px', background: 'var(--color-surface-1)', border: '1px solid var(--color-border-default)', textAlign: 'center' }}>
      <p style={{ fontSize: '28px', fontWeight: 700, color, marginBottom: '2px' }}>{value}</p>
      <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>{label}</p>
    </div>
  );
}
function Section({ title, icon, color, children }: { title: string; icon: React.ReactNode; color: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
        <span style={{ color }}>{icon}</span>
        <h3 style={{ fontSize: '15px', fontWeight: 600 }}>{title}</h3>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {children}
      </div>
    </div>
  );
}

function ResultCard({ result }: { result: { title: string; url: string | null; snippet: string | null; relevance_score: number | null } }) {
  return (
    <div style={{ padding: '14px 16px', borderRadius: '10px', background: 'var(--color-surface-1)', border: '1px solid var(--color-border-default)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '4px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flex: 1 }}>
          {result.url ? (
            <a href={result.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '14px', fontWeight: 600, color: 'var(--color-text-primary)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}>
              {result.title} <ExternalLink size={10} color="var(--color-text-tertiary)" />
            </a>
          ) : (
            <span style={{ fontSize: '14px', fontWeight: 600 }}>{result.title}</span>
          )}
        </div>
        {result.relevance_score && (
          <span style={{ fontSize: '11px', color: 'var(--color-text-tertiary)', whiteSpace: 'nowrap', marginLeft: '12px' }}>
            {(result.relevance_score * 100).toFixed(0)}% match
          </span>
        )}
      </div>
      {result.snippet && (
        <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
          {result.snippet}
        </p>
      )}
    </div>
  );
}
