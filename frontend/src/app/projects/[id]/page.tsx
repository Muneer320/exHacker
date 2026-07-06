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
import { getProject, startResearch, getResearch, Project, ResearchData } from '@/services/api';

type Tab = 'overview' | 'research';

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

  useEffect(() => {
    if (!projectId) return;
    getProject(projectId).then((res) => {
      if (res.success) {
        setProject(res.data.project);
        loadResearch();
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
