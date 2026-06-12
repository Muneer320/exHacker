'use client';

import { use, useState, useEffect } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
  Download, Star, Calendar, BarChart2, GitBranch, Layers, Monitor, Mic, Search,
  CheckCircle, ExternalLink, Copy, ChevronRight, Play, Zap
} from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import { DEMO_FINANCE_PROJECT } from '@/mock/data';
import { ScoreBar } from '@/components/shared/ui';
import { getWorkflowState } from '@/services/api';

function hexToRgb(hex: string) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `${r},${g},${b}`;
}

const TABS = [
  { id: 'overview', label: 'Overview', icon: BarChart2 },
  { id: 'architecture', label: 'Architecture', icon: GitBranch },
  { id: 'tech', label: 'Tech Stack', icon: Layers },
  { id: 'build', label: 'Build Plan', icon: Calendar },
  { id: 'presentation', label: 'Presentation', icon: Monitor },
  { id: 'pitch', label: 'Pitch', icon: Mic },
  { id: 'research', label: 'Research', icon: Search },
  { id: 'export', label: 'Export', icon: Download },
];

// ── Overview Tab ────────────────────────────────────────────────────────────
function OverviewTab({ state }: { state?: any }) {
  const p = DEMO_FINANCE_PROJECT;
  const selectedIdea = state?.selected_idea || p.ideas.find((i) => i.id === p.selectedIdea)!;

  const problemText = state?.problem_analysis?.refined_problem_statement || 'Students lack financial literacy tools designed for their reality — dorm budgets, part-time income, career planning.';
  const taglineText = selectedIdea?.description || selectedIdea?.tagline || 'AI-powered financial coaching personalized for students.';
  const usersText = selectedIdea?.target_users?.join(', ') || 'University students, recent graduates, young professionals entering the workforce.';

  // Map scores
  const innovationVal = Math.round(selectedIdea?.scores?.innovation || selectedIdea?.innovation_score * 10 || p.ideas[0].scores.innovation);
  const feasibilityVal = Math.round(selectedIdea?.scores?.feasibility || state?.validation_reports?.find((r: any) => r.idea_id === selectedIdea.id)?.feasibility_score * 10 || p.ideas[0].scores.feasibility);
  const diffVal = Math.round(selectedIdea?.scores?.differentiation || state?.validation_reports?.find((r: any) => r.idea_id === selectedIdea.id)?.final_score * 10 || p.ideas[0].scores.differentiation);
  
  const strengths = state?.validation_reports?.find((r: any) => r.idea_id === selectedIdea.id)?.strengths || selectedIdea?.strengths || p.ideas[0].strengths;

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {[
          { label: 'Problem', content: problemText, color: '#EF4444' },
          { label: 'Solution', content: taglineText, color: '#22C55E' },
          { label: 'Target Users', content: usersText, color: '#06B6D4' },
        ].map((card) => (
          <div key={card.label} style={{ background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)', padding: '20px' }}>
            <p style={{ fontSize: '11px', fontWeight: 600, color: card.color, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '10px' }}>{card.label}</p>
            <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.7)', lineHeight: 1.6 }}>{card.content}</p>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '24px' }}>
        {[
          { label: 'Innovation', value: innovationVal, color: '#EC4899' },
          { label: 'Feasibility', value: feasibilityVal, color: '#22C55E' },
          { label: 'Differentiation', value: diffVal, color: '#7C3AED' },
          { label: 'Overall Score', value: Math.round(state?.validation_reports?.find((r: any) => r.idea_id === selectedIdea.id)?.final_score * 10 || p.overallScore), color: '#F59E0B' },
        ].map((m) => (
          <div key={m.label} style={{ background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)', padding: '20px', textAlign: 'center' }}>
            <div style={{ fontSize: '36px', fontWeight: 800, color: m.color, marginBottom: '4px' }}>{m.value}</div>
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)' }}>{m.label}</div>
          </div>
        ))}
      </div>

      <div style={{ background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)', padding: '24px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '16px' }}>Why this idea wins</h3>
        {strengths.map((s: string, i: number) => (
          <div key={i} style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
            <CheckCircle size={16} color="#22C55E" style={{ flexShrink: 0, marginTop: '2px' }} />
            <span style={{ fontSize: '14px', color: 'rgba(255,255,255,0.65)' }}>{s}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Architecture Tab ─────────────────────────────────────────────────────────
function ArchitectureTab({ state }: { state?: any }) {
  const { architecture } = DEMO_FINANCE_PROJECT;
  const mermaidDiagram = state?.architecture?.mermaid_diagram || state?.architecture?.mermaidDiagram || architecture.mermaidDiagram;
  
  const componentsList = state?.architecture?.components 
    ? state.architecture.components.map((c: any) => ({
        name: c.name,
        type: c.type || 'backend',
        tech: c.responsibilities?.join(', ') || c.tech || 'Integrated Service'
      }))
    : architecture.components;

  return (
    <div>
      <div style={{ background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)', padding: '28px', marginBottom: '20px', fontFamily: '"Fira Code", monospace', fontSize: '13px', lineHeight: 1.7 }}>
        <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.3)', marginBottom: '16px', fontFamily: 'Inter, sans-serif' }}>SYSTEM ARCHITECTURE DIAGRAM</p>
        <pre style={{ color: '#22C55E', whiteSpace: 'pre-wrap', overflow: 'auto' }}>
          {mermaidDiagram}
        </pre>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
        {componentsList.map((c: any, i: number) => {
          const colorMap: Record<string, string> = { frontend: '#3B82F6', backend: '#7C3AED', database: '#F59E0B', ai: '#22C55E', external: '#06B6D4' };
          const color = colorMap[c.type] || '#7C3AED';
          return (
            <div key={i} style={{ background: '#111827', borderRadius: '12px', border: `1px solid rgba(${hexToRgb(color)}, 0.2)`, padding: '16px' }}>
              <p style={{ fontSize: '10px', fontWeight: 600, color, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px' }}>{c.type}</p>
              <p style={{ fontSize: '14px', fontWeight: 600, marginBottom: '6px' }}>{c.name}</p>
              <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)' }}>{c.tech}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Tech Stack Tab ───────────────────────────────────────────────────────────
function TechStackTab({ state }: { state?: any }) {
  const { techStack } = DEMO_FINANCE_PROJECT;

  const getTechItems = (type: string) => {
    if (state?.tech_stack) {
      const ts = state.tech_stack;
      const mapping: Record<string, string[]> = {
        Frontend: [ts.frontend],
        Backend: [ts.backend],
        Database: [ts.database],
        AI: ts.ai_stack || [],
        Infrastructure: ts.deployment || []
      };
      
      const items = mapping[type] || [];
      return items.map((name: string, i: number) => ({
        name,
        reason: ts.reasoning?.[i] || `Chosen for project stack performance & simplicity.`
      }));
    }
    
    const secMap: Record<string, typeof techStack.frontend> = {
      Frontend: techStack.frontend,
      Backend: techStack.backend,
      Database: techStack.database,
      AI: techStack.ai,
      Infrastructure: techStack.infrastructure
    };
    return secMap[type] || [];
  };

  const sections = [
    { label: 'Frontend', color: '#3B82F6' },
    { label: 'Backend', color: '#7C3AED' },
    { label: 'Database', color: '#F59E0B' },
    { label: 'AI', color: '#22C55E' },
    { label: 'Infrastructure', color: '#06B6D4' },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
      {sections.map((sec) => (
        <div key={sec.label} style={{ background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)', padding: '20px' }}>
          <p style={{ fontSize: '12px', fontWeight: 600, color: sec.color, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '16px' }}>{sec.label}</p>
          {getTechItems(sec.label).map((item) => (
            <div key={item.name} style={{ marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '2px', background: sec.color, flexShrink: 0 }} />
                <span style={{ fontSize: '14px', fontWeight: 600 }}>{item.name}</span>
              </div>
              <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)', paddingLeft: '16px' }}>{item.reason}</p>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

// ── Build Plan Tab ───────────────────────────────────────────────────────────
function BuildPlanTab({ state }: { state?: any }) {
  const { buildPlan } = DEMO_FINANCE_PROJECT;
  const milestones = state?.build_package?.milestones || buildPlan.milestones;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '16px' }}>
      {milestones.map((m: any, i: number) => (
        <div
          key={i}
          style={{
            background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)',
            padding: '20px', animation: `slide-up 300ms ease-out ${i * 100}ms both`,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'rgba(124,58,237,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#A855F7', fontSize: '14px', fontWeight: 700, flexShrink: 0 }}>
              {i + 1}
            </div>
            <div>
              <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)' }}>{m.day || m.timeline || `Day ${i + 1}`}</p>
              <p style={{ fontSize: '15px', fontWeight: 600 }}>{m.title}</p>
            </div>
          </div>
          {(m.tasks || []).map((task: string, j: number) => (
            <div key={j} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <div style={{ width: '4px', height: '4px', borderRadius: '50%', background: '#7C3AED', flexShrink: 0 }} />
              <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.55)' }}>{task}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

// ── Presentation Tab ─────────────────────────────────────────────────────────
function PresentationTab({ state }: { state?: any }) {
  const slides = state?.presentation?.slides?.map((slide: any) => slide.title) || [
    'Title & Hook', 'Problem Statement', 'Market Opportunity', 'Our Solution',
    'Live Demo', 'Technical Architecture', 'AI Intelligence', 'Business Model',
    'Team & Traction', 'Roadmap', 'Competitive Advantage', 'Call to Action',
  ];
  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
        {slides.map((slide: string, i: number) => (
          <div
            key={i}
            style={{
              background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)',
              padding: '0', overflow: 'hidden', cursor: 'pointer', transition: 'border-color 200ms ease',
              animation: `slide-up 250ms ease-out ${i * 40}ms both`,
            }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.borderColor = 'rgba(124,58,237,0.4)'; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.borderColor = 'rgba(255,255,255,0.06)'; }}
          >
            {/* Slide Thumbnail */}
            <div
              style={{
                height: '100px',
                background: `linear-gradient(135deg, rgba(124,58,237,0.15), rgba(6,182,212,0.08))`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                borderBottom: '1px solid rgba(255,255,255,0.06)',
              }}
            >
              <span style={{ fontSize: '28px', fontWeight: 800, color: 'rgba(255,255,255,0.1)' }}>{i + 1}</span>
            </div>
            <div style={{ padding: '12px' }}>
              <p style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', marginBottom: '4px' }}>Slide {i + 1}</p>
              <p style={{ fontSize: '13px', fontWeight: 500, color: 'rgba(255,255,255,0.75)' }}>{slide}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Pitch Tab ────────────────────────────────────────────────────────────────
function PitchTab({ state }: { state?: any }) {
  const { pitch } = DEMO_FINANCE_PROJECT;
  const [expanded, setExpanded] = useState<string | null>('30s');

  const thirtySecond = state?.pitch?.thirty_second || pitch.thirtySecond;
  const twoMinute = state?.pitch?.two_minute || pitch.twoMinute;
  const judgeQA = state?.pitch?.judge_qa || pitch.judgeQA;

  return (
    <div>
      {[
        { id: '30s', label: '30-Second Pitch', duration: '0:30', color: '#22C55E', content: thirtySecond },
        { id: '2m', label: '2-Minute Pitch', duration: '2:00', color: '#7C3AED', content: twoMinute },
      ].map((p) => (
        <div
          key={p.id}
          style={{
            background: '#111827', borderRadius: '12px', border: `1px solid rgba(${hexToRgb(p.color)}, 0.2)`,
            marginBottom: '16px', overflow: 'hidden',
          }}
        >
          <button
            onClick={() => setExpanded(expanded === p.id ? null : p.id)}
            style={{
              width: '100%', padding: '20px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              background: 'transparent', border: 'none', cursor: 'pointer', color: '#F1F5F9',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ padding: '4px 10px', borderRadius: '6px', fontSize: '12px', fontWeight: 600, background: `rgba(${hexToRgb(p.color)}, 0.12)`, color: p.color }}>{p.duration}</span>
              <span style={{ fontSize: '16px', fontWeight: 600 }}>{p.label}</span>
            </div>
            <ChevronRight size={16} color="rgba(255,255,255,0.3)" style={{ transform: expanded === p.id ? 'rotate(90deg)' : 'none', transition: 'transform 200ms ease' }} />
          </button>
          {expanded === p.id && (
            <div style={{ padding: '0 24px 24px', animation: 'slide-up 200ms ease-out' }}>
              <div style={{ background: '#0B1020', borderRadius: '10px', padding: '20px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <p style={{ fontSize: '15px', color: 'rgba(255,255,255,0.8)', lineHeight: 1.8, whiteSpace: 'pre-wrap' }}>{p.content}</p>
              </div>
            </div>
          )}
        </div>
      ))}

      <div style={{ background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)', padding: '24px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Mic size={16} color="#F97316" /> Judge Q&A Prep
        </h3>
        {judgeQA.map((qa: any, i: number) => (
          <div key={i} style={{ marginBottom: '16px', paddingBottom: '16px', borderBottom: i < judgeQA.length - 1 ? '1px solid rgba(255,255,255,0.06)' : 'none' }}>
            <p style={{ fontSize: '14px', fontWeight: 600, color: '#F59E0B', marginBottom: '6px' }}>Q: {qa.question}</p>
            <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.6)', lineHeight: 1.6 }}>{qa.answer}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Research Tab ─────────────────────────────────────────────────────────────
function ResearchTab({ state }: { state?: any }) {
  const { research } = DEMO_FINANCE_PROJECT;

  const report = state?.validation_reports?.find((r: any) => r.idea_id === state.selected_idea?.id);

  const competitors = report?.competitors || research.competitors;
  const apis = report?.apis || research.apis;

  const formattedCompetitors = competitors.map((c: any) => ({
    name: c.name,
    description: c.description,
    strengths: c.strengths || ['Competitive feature set'],
    weaknesses: c.weaknesses || ['Integration friction']
  }));

  const formattedApis = apis.map((api: any) => ({
    name: api.name,
    purpose: api.purpose || api.description || 'Developer API resource',
    pricing: api.pricing || 'Free/Developer tier',
    docsUrl: api.docsUrl || 'https://google.com'
  }));

  const insights = state?.challenge_intelligence?.opportunities || research.insights;

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '2px', background: '#EF4444', display: 'inline-block' }} /> Competitors
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '12px' }}>
          {formattedCompetitors.map((c: any, i: number) => (
            <div key={i} style={{ background: '#111827', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)', padding: '16px' }}>
              <p style={{ fontWeight: 600, marginBottom: '4px' }}>{c.name}</p>
              <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.45)', marginBottom: '10px' }}>{c.description}</p>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {c.strengths.map((s: string) => <span key={s} style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', background: 'rgba(34,197,94,0.08)', color: '#22C55E' }}>{s}</span>)}
                {c.weaknesses.map((w: string) => <span key={w} style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', background: 'rgba(239,68,68,0.08)', color: '#EF4444' }}>{w}</span>)}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '2px', background: '#3B82F6', display: 'inline-block' }} /> APIs
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '12px' }}>
          {formattedApis.map((api: any, i: number) => (
            <div key={i} style={{ background: '#111827', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)', padding: '16px' }}>
              <p style={{ fontWeight: 600, marginBottom: '4px' }}>{api.name}</p>
              <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)', marginBottom: '8px' }}>{api.purpose}</p>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', background: 'rgba(59,130,246,0.08)', color: '#3B82F6' }}>{api.pricing}</span>
                <a href={api.docsUrl} target="_blank" rel="noopener noreferrer" style={{ color: 'rgba(255,255,255,0.3)', display: 'flex' }}>
                  <ExternalLink size={12} />
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '12px' }}>Market Insights</h3>
        {insights.map((insight: string, i: number) => (
          <div key={i} style={{ display: 'flex', gap: '12px', padding: '14px', background: '#111827', borderRadius: '10px', marginBottom: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
            <Star size={14} color="#F59E0B" style={{ flexShrink: 0, marginTop: '2px' }} />
            <span style={{ fontSize: '14px', color: 'rgba(255,255,255,0.65)' }}>{insight}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Export Tab ───────────────────────────────────────────────────────────────
function ExportTab() {
  const [exporting, setExporting] = useState<string | null>(null);
  const exports = [
    { id: 'readme', label: 'README.md', desc: 'Full project documentation', color: '#22C55E', icon: '📄' },
    { id: 'prd', label: 'PRD Document', desc: 'Product requirements document', color: '#3B82F6', icon: '📋' },
    { id: 'arch', label: 'Architecture', desc: 'System design diagrams', color: '#7C3AED', icon: '🏗️' },
    { id: 'pitch', label: 'Pitch Deck', desc: '12-slide presentation', color: '#EC4899', icon: '📊' },
    { id: 'package', label: 'Full Package', desc: 'Everything in one ZIP', color: '#F59E0B', icon: '📦' },
  ];

  const handleExport = async (id: string) => {
    setExporting(id);
    await new Promise((r) => setTimeout(r, 1500));
    setExporting(null);
  };

  return (
    <div>
      <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.4)', marginBottom: '24px' }}>
        Download your complete hackathon package — ready to submit.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '16px' }}>
        {exports.map((ex) => (
          <div
            key={ex.id}
            style={{
              background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)',
              padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px',
            }}
          >
            <div>
              <div style={{ fontSize: '28px', marginBottom: '10px' }}>{ex.icon}</div>
              <p style={{ fontWeight: 600, marginBottom: '4px' }}>{ex.label}</p>
              <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>{ex.desc}</p>
            </div>
            <button
              onClick={() => handleExport(ex.id)}
              disabled={!!exporting}
              style={{
                padding: '10px 20px', borderRadius: '8px', fontSize: '13px', fontWeight: 600, cursor: 'pointer',
                border: `1px solid rgba(${hexToRgb(ex.color)}, 0.3)`,
                background: exporting === ex.id ? `rgba(${hexToRgb(ex.color)}, 0.05)` : `rgba(${hexToRgb(ex.color)}, 0.1)`,
                color: ex.color,
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
                transition: 'all 150ms ease',
              }}
            >
              {exporting === ex.id ? (
                <><div style={{ width: '12px', height: '12px', border: `1.5px solid ${ex.color}40`, borderTopColor: ex.color, borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} /> Preparing...</>
              ) : (
                <><Download size={13} /> Export</>
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Main Dashboard ────────────────────────────────────────────────────────────
export default function DashboardPage({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = use(params);
  const searchParams = useSearchParams();
  const wId = searchParams.get('wId');

  const [activeTab, setActiveTab] = useState('overview');
  const [projectState, setProjectState] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!wId || projectId === 'demo-finance-001') {
      return;
    }

    const fetchState = async () => {
      setLoading(true);
      try {
        const stateRes = await getWorkflowState(wId);
        if (stateRes.success && stateRes.data.state) {
          setProjectState(stateRes.data.state);
        }
      } catch (err) {
        console.error('[exHacker API] Error loading dashboard state:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchState();
  }, [wId, projectId]);

  const selectedIdea = projectState?.selected_idea;
  const finalReport = projectState?.validation_reports?.find((r: any) => r.idea_id === selectedIdea?.id);
  
  const projectName = projectState?.project?.name || DEMO_FINANCE_PROJECT.name;
  const overallScoreVal = finalReport 
    ? Math.round(finalReport.final_score * 10) 
    : DEMO_FINANCE_PROJECT.overallScore;

  const tabContent: Record<string, React.ReactNode> = {
    overview: <OverviewTab state={projectState} />,
    architecture: <ArchitectureTab state={projectState} />,
    tech: <TechStackTab state={projectState} />,
    build: <BuildPlanTab state={projectState} />,
    presentation: <PresentationTab state={projectState} />,
    pitch: <PitchTab state={projectState} />,
    research: <ResearchTab state={projectState} />,
    export: <ExportTab />,
  };

  return (
    <div style={{ background: '#050816', minHeight: '100vh', color: '#F1F5F9' }}>
      <Navbar />
      <div style={{ paddingTop: '80px' }}>
        {/* Header */}
        <div
          style={{
            background: 'linear-gradient(135deg, rgba(124,58,237,0.06) 0%, rgba(6,182,212,0.04) 100%)',
            borderBottom: '1px solid rgba(255,255,255,0.06)',
            padding: '32px 32px 0',
          }}
        >
          <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                  <h1 style={{ fontSize: '28px', fontWeight: 700, letterSpacing: '-0.02em' }}>{projectName}</h1>
                  <div
                    style={{
                      padding: '4px 14px', borderRadius: '99px',
                      background: 'rgba(34,197,94,0.1)', color: '#22C55E', fontSize: '12px', fontWeight: 600,
                      border: '1px solid rgba(34,197,94,0.25)',
                    }}
                  >
                    Complete
                  </div>
                </div>
                <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: '14px' }}>
                  Generated {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                </p>
              </div>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
                {/* Score */}
                <div
                  style={{
                    padding: '12px 20px', borderRadius: '12px',
                    background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)',
                    display: 'flex', alignItems: 'center', gap: '10px',
                  }}
                >
                  <Star size={18} color="#F59E0B" fill="#F59E0B" />
                  <div>
                    <p style={{ fontSize: '22px', fontWeight: 800, color: '#F59E0B', lineHeight: 1 }}>{overallScoreVal}</p>
                    <p style={{ fontSize: '11px', color: 'rgba(255,255,255,0.4)' }}>Overall Score</p>
                  </div>
                </div>

                <Link
                  href="/demo"
                  style={{
                    display: 'flex', alignItems: 'center', gap: '6px',
                    padding: '10px 20px', borderRadius: '10px', background: 'rgba(124,58,237,0.15)',
                    color: '#A855F7', fontSize: '14px', fontWeight: 600, textDecoration: 'none',
                    border: '1px solid rgba(124,58,237,0.3)',
                  }}
                >
                  <Play size={14} /> Present
                </Link>
                <button
                  style={{
                    display: 'flex', alignItems: 'center', gap: '6px',
                    padding: '10px 20px', borderRadius: '10px', background: '#7C3AED',
                    color: '#fff', fontSize: '14px', fontWeight: 600, border: 'none', cursor: 'pointer',
                  }}
                  onClick={() => setActiveTab('export')}
                >
                  <Download size={14} /> Export
                </button>
              </div>
            </div>

            {/* Tabs */}
            <div style={{ display: 'flex', gap: '0', overflowX: 'auto' }}>
              {TABS.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: '7px',
                      padding: '12px 18px', fontSize: '13px', fontWeight: isActive ? 600 : 400, cursor: 'pointer',
                      border: 'none', borderBottom: `2px solid ${isActive ? '#7C3AED' : 'transparent'}`,
                      background: 'transparent',
                      color: isActive ? '#A855F7' : 'rgba(255,255,255,0.4)',
                      transition: 'all 150ms ease',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    <Icon size={14} />
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Tab Content */}
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 32px 80px' }}>
          <div key={activeTab} style={{ animation: 'fade-in 200ms ease-out' }}>
            {tabContent[activeTab]}
          </div>
        </div>
      </div>
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes slide-up { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
      `}</style>
    </div>
  );
}
