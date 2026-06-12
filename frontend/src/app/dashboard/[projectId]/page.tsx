'use client';

import { use, useState, useEffect } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
  Download, Star, Calendar, BarChart2, GitBranch, Layers, Monitor, Mic, Search,
  CheckCircle, ExternalLink, Play, Zap, FileText, Package, Presentation,
  Code2, Trophy, TrendingUp, Target, Sparkles, AlertCircle, RefreshCw,
  ChevronRight, ChevronDown, Copy, Database
} from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import { DEMO_FINANCE_PROJECT } from '@/mock/data';
import { ScoreBar } from '@/components/shared/ui';
import { getWorkflowState } from '@/services/api';
import dynamic from 'next/dynamic';

const MermaidDiagram = dynamic(() => import('@/components/shared/MermaidDiagram'), { ssr: false });

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

  const problemText = state?.problem_analysis?.refined_problem_statement
    || 'Students lack financial literacy tools designed for their reality — dorm budgets, part-time income, career planning.';
  const taglineText = selectedIdea?.description || selectedIdea?.tagline
    || 'AI-powered financial coaching personalized for students.';
  const usersText = (selectedIdea?.target_users || []).join(', ')
    || 'University students, recent graduates, young professionals entering the workforce.';

  const validReport = state?.validation_reports?.find((r: any) => r.idea_id === selectedIdea?.id);

  const innovationVal = Math.round(
    (validReport?.innovation_score ?? selectedIdea?.innovation_score ?? 0) * 10 ||
    selectedIdea?.scores?.innovation || p.ideas[0].scores.innovation
  );
  const feasibilityVal = Math.round(
    (validReport?.feasibility_score ?? 0) * 10 || selectedIdea?.scores?.feasibility || p.ideas[0].scores.feasibility
  );
  const diffVal = Math.round(
    (validReport?.final_score ?? 0) * 10 || selectedIdea?.scores?.differentiation || p.ideas[0].scores.differentiation
  );
  const overallVal = validReport
    ? Math.round(validReport.final_score * 10)
    : p.overallScore;

  const strengths = validReport?.strengths || selectedIdea?.strengths || p.ideas[0].strengths;

  const cards = [
    { label: 'Problem', content: problemText, color: '#EF4444', icon: AlertCircle },
    { label: 'Solution', content: taglineText, color: '#22C55E', icon: CheckCircle },
    { label: 'Target Users', content: usersText, color: '#06B6D4', icon: Target },
  ];

  const metrics = [
    { label: 'Innovation', value: innovationVal, color: '#EC4899' },
    { label: 'Feasibility', value: feasibilityVal, color: '#22C55E' },
    { label: 'Differentiation', value: diffVal, color: '#7C3AED' },
    { label: 'Overall Score', value: overallVal, color: '#F59E0B' },
  ];

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} style={{ background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)', padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                <Icon size={13} color={card.color} />
                <p style={{ fontSize: '11px', fontWeight: 600, color: card.color, textTransform: 'uppercase', letterSpacing: '0.1em' }}>{card.label}</p>
              </div>
              <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.7)', lineHeight: 1.6 }}>{card.content}</p>
            </div>
          );
        })}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '24px' }}>
        {metrics.map((m) => (
          <div key={m.label} style={{ background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)', padding: '20px', textAlign: 'center' }}>
            <div style={{ fontSize: '36px', fontWeight: 800, color: m.color, marginBottom: '4px' }}>{m.value}</div>
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)' }}>{m.label}</div>
          </div>
        ))}
      </div>

      {strengths && strengths.length > 0 && (
        <div style={{ background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)', padding: '24px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Trophy size={16} color="#F59E0B" /> Why this idea wins
          </h3>
          {strengths.map((s: string, i: number) => (
            <div key={i} style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
              <CheckCircle size={16} color="#22C55E" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span style={{ fontSize: '14px', color: 'rgba(255,255,255,0.65)' }}>{s}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Architecture Tab ─────────────────────────────────────────────────────────
function ArchitectureTab({ state }: { state?: any }) {
  const { architecture } = DEMO_FINANCE_PROJECT;

  // Backend uses `system_design` as a text field; mermaid_diagram is separate or embedded
  const mermaidDiagram = state?.architecture?.mermaid_diagram
    || state?.architecture?.mermaidDiagram
    || architecture.mermaidDiagram;

  const componentsList = state?.architecture?.components
    ? state.architecture.components.map((c: any) => ({
        name: c.name,
        type: c.type || 'backend',
        tech: Array.isArray(c.responsibilities)
          ? c.responsibilities.slice(0, 2).join(', ')
          : (c.tech || c.description || 'Integrated Service'),
      }))
    : architecture.components;

  const colorMap: Record<string, string> = {
    frontend: '#3B82F6', backend: '#7C3AED', database: '#F59E0B',
    ai: '#22C55E', external: '#06B6D4', service: '#EC4899',
  };

  return (
    <div>
      <div style={{
        background: '#0B1020',
        borderRadius: '12px',
        border: '1px solid rgba(255,255,255,0.06)',
        padding: '28px',
        marginBottom: '20px',
      }}>
        <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.3)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <GitBranch size={12} color="rgba(255,255,255,0.3)" />
          SYSTEM ARCHITECTURE DIAGRAM
        </p>
        <MermaidDiagram diagram={mermaidDiagram} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
        {componentsList.map((c: any, i: number) => {
          const color = colorMap[c.type?.toLowerCase()] || '#7C3AED';
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
      const mapping: Record<string, string | string[]> = {
        Frontend: ts.frontend,
        Backend: ts.backend,
        Database: ts.database,
        AI: ts.ai_stack || [],
        Infrastructure: ts.deployment || [],
      };

      const raw = mapping[type];
      const items = Array.isArray(raw) ? raw : (raw ? [raw] : []);
      const reasoning = ts.reasoning || [];
      return items.map((name: string, i: number) => ({
        name,
        reason: reasoning[i] || 'Chosen for performance and developer experience.',
      }));
    }

    const secMap: Record<string, any[]> = {
      Frontend: techStack.frontend,
      Backend: techStack.backend,
      Database: techStack.database,
      AI: techStack.ai,
      Infrastructure: techStack.infrastructure,
    };
    return secMap[type] || [];
  };

  const sections = [
    { label: 'Frontend', color: '#3B82F6', icon: Monitor },
    { label: 'Backend', color: '#7C3AED', icon: Code2 },
    { label: 'Database', color: '#F59E0B', icon: Database },
    { label: 'AI', color: '#22C55E', icon: Zap },
    { label: 'Infrastructure', color: '#06B6D4', icon: Package },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
      {sections.map((sec) => {
        const Icon = sec.icon;
        return (
          <div key={sec.label} style={{ background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)', padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Icon size={14} color={sec.color} />
              <p style={{ fontSize: '12px', fontWeight: 600, color: sec.color, textTransform: 'uppercase', letterSpacing: '0.1em' }}>{sec.label}</p>
            </div>
            {getTechItems(sec.label).map((item: any) => (
              <div key={item.name} style={{ marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '2px', background: sec.color, flexShrink: 0 }} />
                  <span style={{ fontSize: '14px', fontWeight: 600 }}>{item.name}</span>
                </div>
                <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)', paddingLeft: '16px' }}>{item.reason}</p>
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
}

// ── Build Plan Tab ───────────────────────────────────────────────────────────
function BuildPlanTab({ state }: { state?: any }) {
  const { buildPlan } = DEMO_FINANCE_PROJECT;

  // Backend stores build_package as { frontend_tasks, backend_tasks, database_tasks, etc }
  // Convert flat task lists to milestones-like view
  const getMilestones = () => {
    if (state?.build_package) {
      const bp = state.build_package;
      const domains = [
        { title: 'Frontend', day: 'Phase 1', tasks: bp.frontend_tasks || [], color: '#3B82F6' },
        { title: 'Backend', day: 'Phase 2', tasks: bp.backend_tasks || [], color: '#7C3AED' },
        { title: 'Database', day: 'Phase 3', tasks: bp.database_tasks || [], color: '#F59E0B' },
        { title: 'Testing', day: 'Phase 4', tasks: bp.testing_tasks || [], color: '#22C55E' },
        { title: 'Deployment', day: 'Phase 5', tasks: bp.deployment_tasks || [], color: '#06B6D4' },
      ].filter(d => d.tasks.length > 0);
      return domains;
    }
    return buildPlan.milestones.map((m, i) => ({ ...m, color: ['#3B82F6','#7C3AED','#F59E0B','#22C55E'][i % 4] }));
  };

  const milestones = getMilestones();

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '16px' }}>
      {milestones.map((m: any, i: number) => (
        <div key={i} style={{
          background: '#111827', borderRadius: '12px',
          border: `1px solid rgba(${hexToRgb(m.color || '#7C3AED')}, 0.2)`,
          padding: '20px',
          animation: `slide-up 300ms ease-out ${i * 100}ms both`,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{
              width: '36px', height: '36px', borderRadius: '10px',
              background: `rgba(${hexToRgb(m.color || '#7C3AED')}, 0.12)`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: m.color || '#A855F7', fontSize: '14px', fontWeight: 700, flexShrink: 0,
            }}>
              {i + 1}
            </div>
            <div>
              <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)' }}>{m.day || m.timeline || `Phase ${i + 1}`}</p>
              <p style={{ fontSize: '15px', fontWeight: 600 }}>{m.title}</p>
            </div>
          </div>
          {(m.tasks || []).map((task: string, j: number) => (
            <div key={j} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', marginBottom: '8px' }}>
              <div style={{ width: '4px', height: '4px', borderRadius: '50%', background: m.color || '#7C3AED', flexShrink: 0, marginTop: '7px' }} />
              <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.55)', lineHeight: 1.5 }}>{task}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

// ── Presentation Tab ─────────────────────────────────────────────────────────
function PresentationTab({ state }: { state?: any }) {
  // Backend stores presentation.slide_content as array of {title, content, visual_notes}
  const slideContent = state?.presentation?.slide_content || state?.presentation?.slides || [];
  const slideOrder = state?.presentation?.slide_order || [];

  const slides = slideContent.length > 0
    ? slideContent.map((s: any) => ({ title: s.title, content: s.content || [] }))
    : slideOrder.length > 0
      ? slideOrder.map((title: string) => ({ title, content: [] }))
      : [
          'Title & Hook', 'Problem Statement', 'Market Opportunity', 'Our Solution',
          'Live Demo', 'Technical Architecture', 'AI Intelligence', 'Business Model',
          'Team & Traction', 'Roadmap', 'Competitive Advantage', 'Call to Action',
        ].map(title => ({ title, content: [] }));

  const [selected, setSelected] = useState<number | null>(null);

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
        {slides.map((slide: any, i: number) => (
          <div
            key={i}
            onClick={() => setSelected(selected === i ? null : i)}
            style={{
              background: selected === i ? 'rgba(124,58,237,0.08)' : '#111827',
              borderRadius: '12px',
              border: `1px solid ${selected === i ? 'rgba(124,58,237,0.4)' : 'rgba(255,255,255,0.06)'}`,
              padding: '0', overflow: 'hidden', cursor: 'pointer',
              transition: 'all 200ms ease',
              animation: `slide-up 250ms ease-out ${i * 40}ms both`,
            }}
          >
            <div style={{
              height: '80px',
              background: `linear-gradient(135deg, rgba(124,58,237,0.15), rgba(6,182,212,0.08))`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              borderBottom: '1px solid rgba(255,255,255,0.06)',
              position: 'relative',
            }}>
              <span style={{ fontSize: '28px', fontWeight: 800, color: 'rgba(255,255,255,0.1)' }}>{i + 1}</span>
              {selected === i && (
                <div style={{
                  position: 'absolute', top: '8px', right: '8px',
                  padding: '2px 6px', borderRadius: '4px',
                  background: 'rgba(124,58,237,0.3)', fontSize: '10px', color: '#A855F7',
                }}>
                  <Monitor size={10} style={{ display: 'inline', marginRight: '3px' }} />
                  Open
                </div>
              )}
            </div>
            <div style={{ padding: '12px' }}>
              <p style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', marginBottom: '4px' }}>Slide {i + 1}</p>
              <p style={{ fontSize: '13px', fontWeight: 500, color: 'rgba(255,255,255,0.75)' }}>{slide.title}</p>
            </div>
            {selected === i && slide.content && slide.content.length > 0 && (
              <div style={{ padding: '0 12px 12px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                {slide.content.map((point: string, j: number) => (
                  <div key={j} style={{ display: 'flex', gap: '6px', marginBottom: '4px', marginTop: j === 0 ? '10px' : '0' }}>
                    <ChevronRight size={12} color="#A855F7" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span style={{ fontSize: '12px', color: 'rgba(255,255,255,0.55)' }}>{point}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {state?.presentation?.demo_story && (
        <div style={{ marginTop: '24px', background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)', padding: '24px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Play size={14} color="#A855F7" /> Demo Story
          </h3>
          <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.6)', lineHeight: 1.7 }}>{state.presentation.demo_story}</p>
        </div>
      )}
    </div>
  );
}

// ── Pitch Tab ────────────────────────────────────────────────────────────────
function PitchTab({ state }: { state?: any }) {
  const { pitch } = DEMO_FINANCE_PROJECT;
  const [expanded, setExpanded] = useState<string | null>('30s');

  // Backend PitchPackage: pitch_30s, pitch_2m, pitch_5m, judge_questions, demo_script
  const thirtySecond = state?.pitch?.pitch_30s || state?.pitch?.thirty_second || pitch.thirtySecond;
  const twoMinute = state?.pitch?.pitch_2m || state?.pitch?.two_minute || pitch.twoMinute;
  const fiveMinute = state?.pitch?.pitch_5m || null;
  const judgeQA = state?.pitch?.judge_questions || state?.pitch?.judge_qa || pitch.judgeQA;
  const demoScript = state?.pitch?.demo_script || null;

  const pitches = [
    { id: '30s', label: '30-Second Pitch', duration: '0:30', color: '#22C55E', content: thirtySecond },
    { id: '2m', label: '2-Minute Pitch', duration: '2:00', color: '#7C3AED', content: twoMinute },
    ...(fiveMinute ? [{ id: '5m', label: '5-Minute Pitch', duration: '5:00', color: '#3B82F6', content: fiveMinute }] : []),
  ];

  return (
    <div>
      {pitches.map((p) => (
        <div key={p.id} style={{
          background: '#111827', borderRadius: '12px',
          border: `1px solid rgba(${hexToRgb(p.color)}, 0.2)`,
          marginBottom: '16px', overflow: 'hidden',
        }}>
          <button
            onClick={() => setExpanded(expanded === p.id ? null : p.id)}
            style={{
              width: '100%', padding: '20px 24px',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              background: 'transparent', border: 'none', cursor: 'pointer', color: '#F1F5F9',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ padding: '4px 10px', borderRadius: '6px', fontSize: '12px', fontWeight: 600, background: `rgba(${hexToRgb(p.color)}, 0.12)`, color: p.color }}>
                {p.duration}
              </span>
              <span style={{ fontSize: '16px', fontWeight: 600 }}>{p.label}</span>
            </div>
            <ChevronDown size={16} color="rgba(255,255,255,0.3)" style={{ transform: expanded === p.id ? 'rotate(180deg)' : 'none', transition: 'transform 200ms ease' }} />
          </button>
          {expanded === p.id && (
            <div style={{ padding: '0 24px 24px', animation: 'slide-up 200ms ease-out' }}>
              <div style={{ background: '#0B1020', borderRadius: '10px', padding: '20px', border: '1px solid rgba(255,255,255,0.06)', position: 'relative' }}>
                <button
                  onClick={() => navigator.clipboard?.writeText(p.content || '')}
                  title="Copy to clipboard"
                  style={{
                    position: 'absolute', top: '12px', right: '12px',
                    padding: '6px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: '6px', cursor: 'pointer', color: 'rgba(255,255,255,0.4)', display: 'flex',
                  }}
                >
                  <Copy size={12} />
                </button>
                <p style={{ fontSize: '15px', color: 'rgba(255,255,255,0.8)', lineHeight: 1.8, whiteSpace: 'pre-wrap', paddingRight: '32px' }}>
                  {p.content}
                </p>
              </div>
            </div>
          )}
        </div>
      ))}

      {demoScript && (
        <div style={{ background: '#111827', borderRadius: '12px', border: '1px solid rgba(6,182,212,0.2)', padding: '24px', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Play size={14} color="#06B6D4" /> Demo Script
          </h3>
          <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.65)', lineHeight: 1.7 }}>{demoScript}</p>
        </div>
      )}

      <div style={{ background: '#111827', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)', padding: '24px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Mic size={16} color="#F97316" /> Judge Q&A Prep
        </h3>
        {(judgeQA || []).map((qa: any, i: number) => (
          <div key={i} style={{ marginBottom: '16px', paddingBottom: '16px', borderBottom: i < (judgeQA?.length || 1) - 1 ? '1px solid rgba(255,255,255,0.06)' : 'none' }}>
            <p style={{ fontSize: '14px', fontWeight: 600, color: '#F59E0B', marginBottom: '6px' }}>
              Q: {qa.question}
            </p>
            <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.6)', lineHeight: 1.6 }}>
              {qa.answer}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Research Tab ─────────────────────────────────────────────────────────────
function ResearchTab({ state }: { state?: any }) {
  const { research } = DEMO_FINANCE_PROJECT;

  const report = state?.validation_reports?.find((r: any) => r.idea_id === state?.selected_idea?.id);
  const competitors = report?.competitors || research.competitors;
  const apis = report?.apis || research.apis;
  const insights = state?.challenge_intelligence?.opportunities || research.insights;

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <TrendingUp size={15} color="#EF4444" /> Competitors
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '12px' }}>
          {(competitors || []).map((c: any, i: number) => (
            <div key={i} style={{ background: '#111827', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)', padding: '16px' }}>
              <p style={{ fontWeight: 600, marginBottom: '4px' }}>{c.name}</p>
              <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.45)', marginBottom: '10px' }}>{c.description}</p>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {(c.strengths || []).map((s: string) => (
                  <span key={s} style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', background: 'rgba(34,197,94,0.08)', color: '#22C55E' }}>{s}</span>
                ))}
                {(c.weaknesses || []).map((w: string) => (
                  <span key={w} style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', background: 'rgba(239,68,68,0.08)', color: '#EF4444' }}>{w}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Code2 size={15} color="#3B82F6" /> APIs & Integrations
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '12px' }}>
          {(apis || []).map((api: any, i: number) => (
            <div key={i} style={{ background: '#111827', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)', padding: '16px' }}>
              <p style={{ fontWeight: 600, marginBottom: '4px' }}>{api.name}</p>
              <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)', marginBottom: '8px' }}>{api.description || api.purpose}</p>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', background: 'rgba(59,130,246,0.08)', color: '#3B82F6' }}>
                  {api.pricing || 'API'}
                </span>
                {(api.url || api.docsUrl) && (
                  <a href={api.url || api.docsUrl} target="_blank" rel="noopener noreferrer" style={{ color: 'rgba(255,255,255,0.3)', display: 'flex' }}>
                    <ExternalLink size={12} />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {insights && insights.length > 0 && (
        <div>
          <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Zap size={15} color="#7C3AED" /> Market Insights
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
            {(insights || []).map((insight: string, i: number) => (
              <div key={i} style={{ background: '#111827', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)', padding: '16px' }}>
                <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.65)', lineHeight: 1.6 }}>{insight}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Detailed compilation document generators ──────────────────────────────
function generatePRD(state: any) {
  const p = DEMO_FINANCE_PROJECT;
  const idea = state?.selected_idea || {};
  const title = idea.title || p.name;
  const desc = idea.description || idea.tagline || p.ideas[0].tagline;
  const metrics = (state?.problem_analysis?.success_metrics || ['User retention', 'Habit formation rate']).map((m: string) => `- ${m}`).join('\n');
  const userGroups = (idea.target_users || ['University students', 'Recent graduates', 'Young professionals']).map((u: string) => `- ${u}`).join('\n');

  return `# Product Requirements Document (PRD) — ${title}

## 1. Executive Summary
The goal of **${title}** is to address the following core challenge:
> ${state?.project?.challenge_statements?.[0] || p.challenge}

This product is designed as an AI-powered solution providing high-value personalized assistance to users.
Key tagline: *${desc}*

## 2. Product Goals & Success Metrics
Our primary objective is to build a highly engaging MVP within the hackathon timeline. Success will be measured by the following metrics:
${metrics}

## 3. Target Audience & Personas
### Primary Audience
The application targets:
${userGroups}

### User Persona: Alex, the High-Stress Student
- **Demographics:** 20 years old, Sophomore in Computer Science.
- **Pain Points:** Hard to manage part-time wages alongside academic deadlines; finds financial jargon intimidating.
- **Goal:** Wants a simple, automated system that gives micro-actions to stay on track.

## 4. Functional Specifications & Features
### P0 Features (Core MVP)
1. **Interactive AI Dashboard:** Real-time feedback on user inputs.
2. **Personalized Coaching Layer:** Actionable insights tailored to user profile.
3. **Core Workflow Automation:** Step-by-step guidance.

### P1 Features (Nice to Have)
1. **Integrations Panel:** External data connections.
2. **Sharing/Export Capability:** Export reports for offline review.

## 5. Non-Functional Requirements
- **Performance:** App load time under 1.5 seconds. API responses under 500ms.
- **Security:** Fully secure JWT authentication and encrypted data transit.
- **Design:** Modern dark-mode interface with accessible contrast levels.
`;
}

function generateREADME(state: any) {
  const idea = state?.selected_idea || {};
  const title = idea.title || DEMO_FINANCE_PROJECT.name;
  const desc = idea.description || idea.tagline || DEMO_FINANCE_PROJECT.ideas[0].tagline;
  const ts = state?.tech_stack || {};
  
  return `# ${title}

${desc}

## 🚀 Key Features
- **AI Engine:** Customized agent intelligence powered by LLMs.
- **Responsive Web Dashboard:** Modern dashboard styled with curated color systems.
- **Data Flow Integration:** End-to-end telemetry and logs persistence.

## 🛠️ Tech Stack
- **Frontend:** ${ts.frontend || 'Next.js 15 (App Router)'}
- **Backend:** ${ts.backend || 'FastAPI (Python)'}
- **Database:** ${ts.database || 'PostgreSQL'}
- **AI Stack:** ${(ts.ai_stack || ['Gemini Pro', 'Groq LLaMA 3']).join(', ')}
- **Deployment:** ${(ts.deployment || ['Docker', 'Vercel']).join(', ')}

## ⚙️ Getting Started

### Prerequisites
- Node.js v20+
- Python 3.10+
- Docker (optional)

### Backend Setup
\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate # or venv\\Scripts\\activate on Windows
pip install -r requirements.txt
cp .env.example .env # Set your API keys
uvicorn app.api.main:app --reload
\`\`\`

### Frontend Setup
\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

## 📝 License
Distributed under the MIT License. See \`LICENSE\` for more information.
`;
}

function generateARCHITECTURE(state: any) {
  const arch = state?.architecture || {};
  const idea = state?.selected_idea || {};
  const title = idea.title || 'Solution';
  
  const componentsList = (arch.components || DEMO_FINANCE_PROJECT.architecture.components).map((c: any) => 
    `### ${c.name}\n- **Type:** ${c.type || 'Service'}\n- **Description:** ${c.description || c.tech || 'Core architecture module'}`
  ).join('\n\n');

  const mermaidDiag = arch.mermaid_diagram || arch.mermaidDiagram || DEMO_FINANCE_PROJECT.architecture.mermaidDiagram;

  return `# System Architecture Document — ${title}

## 1. System Overview
This application uses a modern decoupled architecture consisting of a client-side single-page application and a RESTful API server integrated with an AI agent pipeline.

## 2. Mermaid Dataflow Diagram
\`\`\`mermaid
${mermaidDiag}
\`\`\`

## 3. Core Component Catalog
${componentsList}

## 4. Core Integration & Third-Party APIs
We leverage the following third-party systems:
- **Large Language Models:** Fast inference engines for prompt completion.
- **Market Search APIs:** Real-time competitor and open source library research.
`;
}

function generateSCHEMA(state: any) {
  const ts = state?.tech_stack || {};
  const database = ts.database || 'PostgreSQL';

  return `# Database Schema Specification

This document details the database schema, tables, indexes, and relationships for the project.

## Database Engine
- Recommended: ${database}

## Entity Relationship Summary
\`\`\`mermaid
erDiagram
  USERS ||--o{ PROJECTS : owns
  PROJECTS ||--o{ WORKFLOWS : runs
  WORKFLOWS ||--o{ LOGS : emits
\`\`\`

## Table Schemas

### 1. \`users\`
Stores user credentials and authentication details.
| Column | Type | Constraints | Description |
|---|---|---|---|
| \`id\` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| \`email\` | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| \`password_hash\` | VARCHAR(255) | NOT NULL | Hashed password |
| \`created_at\` | TIMESTAMPTZ | DEFAULT NOW() | Record creation time |

### 2. \`projects\`
Stores details about projects.
| Column | Type | Constraints | Description |
|---|---|---|---|
| \`id\` | UUID | PRIMARY KEY | Unique project ID |
| \`name\` | VARCHAR(255) | NOT NULL | Project name |
| \`challenge\` | TEXT | NOT NULL | User input challenge |
| \`created_at\` | TIMESTAMPTZ | DEFAULT NOW() | Record creation time |

### 3. \`workflows\`
Tracks execution states and agent progression.
| Column | Type | Constraints | Description |
|---|---|---|---|
| \`id\` | UUID | PRIMARY KEY | Unique workflow ID |
| \`project_id\` | UUID | FOREIGN KEY references \`projects(id)\` | Connected project |
| \`stage\` | VARCHAR(64) | NOT NULL | Current pipeline stage |
| \`progress\` | INT | DEFAULT 0 | Percentage completed |
| \`state_data\` | JSONB | NOT NULL | Serialized agent results |
`;
}

function generateENDPOINTS(state: any) {
  return `# API Endpoints Specification

This document details the HTTP REST endpoints exposed by the backend API.

## Base URL
- Local: \`http://localhost:8000/api/v1\`
- Production: \`https://api.exhacker-app.com/api/v1\`

## 1. Authentication Endpoints

### POST \`/auth/register\`
Creates a new user profile.
- **Request Body:**
  \`\`\`json
  {
    "email": "user@example.com",
    "password": "strongpassword123"
  }
  \`\`\`
- **Response (201 Created):**
  \`\`\`json
  {
    "id": "e4444555-d111-2222-3333-a1234567890b",
    "email": "user@example.com",
    "created_at": "2026-06-12T10:00:00Z"
  }
  \`\`\`

### POST \`/auth/login\`
Exchange credentials for a JSON Web Token (JWT).
- **Response (200 OK):**
  \`\`\`json
  {
    "access_token": "access_token_token",
    "token_type": "bearer"
  }
  \`\`\`

## 2. Project Endpoints

### GET \`/projects\`
Retrieve all projects owned by the authenticated user.
- **Response (200 OK):**
  \`\`\`json
  [
    {
      "id": "p0001",
      "name": "Finance App",
      "created_at": "2026-06-12T10:00:00Z"
    }
  ]
  \`\`\`
`;
}

function generateDEPLOYMENT(state: any) {
  return `# Deployment & Operations Guide

## 1. Dockerization
To simplify environment deployments, build the project containers.

### Dockerfile (Backend)
\`\`\`dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
\`\`\`

### Docker Compose
\`\`\`yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/db
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
\`\`\`

## 2. Hosting Platforms
- **Frontend:** Deploy to Vercel or Netlify via direct git hooks.
- **Backend:** Host on Render, AWS ECS, or DigitalOcean App Platform.
`;
}

function generateTESTING(state: any) {
  return `# Testing Strategy & Test Suites

## 1. Testing Pyramid
- **Unit Tests (70%):** Mocking external APIs and LLMs.
- **Integration Tests (20%):** Validating routes and DB operations.
- **E2E Tests (10%):** Cypress or Playwright verifying frontend wizard and dashboard tabs.

## 2. Example Backend Test (Pytest)
\`\`\`python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_read_projects():
    async with AsyncClient(base_url="http://test") as ac:
        response = await ac.get("/api/v1/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
\`\`\`
`;
}

function generateCONTRIBUTING(state: any) {
  return `# Contributing Guidelines

## Code Style
- **Frontend:** ESLint, Prettier, TypeScript strict mode.
- **Backend:** PEP 8, Ruff / Black for linting and formatting.

## Workflow Actions
1. Fork the repository.
2. Create a feature branch (\`git checkout -b feature/amazing-feature\`).
3. Commit your changes (\`git commit -m 'feat: add amazing feature'\`).
4. Push to the branch (\`git push origin feature/amazing-feature\`).
5. Open a Pull Request.
`;
}

function generateBUSINESSMODEL(state: any) {
  return `# Business Model Canvas & Value Proposition

## 1. Value Proposition
A rapid hackathon product validation tool that helps developers and startup founders turn raw ideas into structured specifications, slide structures, pitches, and architecture maps in under 5 minutes.

## 2. Target Market
- Hackathon organizers & competitors.
- Tech Incubators & Accelerators.
- Indie hackers and solo founders.

## 3. Revenue Models
- **Free Tier:** 1 project generation per month.
- **Pro Tier ($15/mo):** Unlimited projects, custom skill profiles, PDF exports.
- **Enterprise:** Customized team settings for corporate hackathons.
`;
}

function generateSECURITY(state: any) {
  return `# Security Compliance & Best Practices

## 1. Threat Mitigation
- **Prompt Injection:** Sanitize inputs before forwarding to LLM endpoints.
- **Token Security:** Store JWT access tokens in HttpOnly cookies to prevent XSS.
- **Rate Limiting:** Protect backend endpoints against denial of service using slowapi rate limiters.

## 2. Data Protection
- HTTPS encryption in transit.
- AES-256 database encryption at rest.
- Strict environment variable segregation.
`;
}

// ── Export Tab Component ─────────────────────────────────────────────────────
function ExportTab({ state, projectId }: { state?: any; projectId: string }) {
  const [selectedFiles, setSelectedFiles] = useState<Record<string, boolean>>({
    readme: true,
    prd: true,
    architecture: true,
    schema: true,
    endpoints: true,
    deployment: false,
    testing: false,
    contributing: false,
    business_model: false,
    security: false,
  });

  const [generating, setGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [activeStepText, setActiveStepText] = useState('');
  const [isGenerated, setIsGenerated] = useState(false);
  const [activePreviewDoc, setActivePreviewDoc] = useState<string>('readme');
  const [downloading, setDownloading] = useState<string | null>(null);

  const documentList = [
    { id: 'readme', label: 'README.md', group: 'core', desc: 'Main documentation landing file', icon: FileText, color: '#22C55E', generator: generateREADME, filename: 'README.md' },
    { id: 'prd', label: 'PRD.md', group: 'core', desc: 'Product Requirements Document', icon: Target, color: '#3B82F6', generator: generatePRD, filename: 'PRD.md' },
    { id: 'architecture', label: 'ARCHITECTURE.md', group: 'core', desc: 'System design and Mermaid dataflow', icon: GitBranch, color: '#7C3AED', generator: generateARCHITECTURE, filename: 'ARCHITECTURE.md' },
    { id: 'schema', label: 'SCHEMA.md', group: 'core', desc: 'Database tables and entity relationships', icon: Database, color: '#EC4899', generator: generateSCHEMA, filename: 'SCHEMA.md' },
    { id: 'endpoints', label: 'ENDPOINTS.md', group: 'core', desc: 'REST API endpoints and payload schemas', icon: Code2, color: '#F59E0B', generator: generateENDPOINTS, filename: 'ENDPOINTS.md' },
    { id: 'deployment', label: 'DEPLOYMENT.md', group: 'recommended', desc: 'Docker, CI/CD, and hosting configuration', icon: Package, color: '#06B6D4', generator: generateDEPLOYMENT, filename: 'DEPLOYMENT.md' },
    { id: 'testing', label: 'TESTING.md', group: 'recommended', desc: 'Testing strategy and example scripts', icon: Code2, color: '#10B981', generator: generateTESTING, filename: 'TESTING.md' },
    { id: 'contributing', label: 'CONTRIBUTING.md', group: 'recommended', desc: 'Coding standards and PR guidelines', icon: FileText, color: '#8B5CF6', generator: generateCONTRIBUTING, filename: 'CONTRIBUTING.md' },
    { id: 'business_model', label: 'BUSINESS_MODEL.md', group: 'recommended', desc: 'Business Model Canvas & monetization plans', icon: Trophy, color: '#EAB308', generator: generateBUSINESSMODEL, filename: 'BUSINESS_MODEL.md' },
    { id: 'security', label: 'SECURITY.md', group: 'recommended', desc: 'Security guidelines and mitigations', icon: AlertCircle, color: '#EF4444', generator: generateSECURITY, filename: 'SECURITY.md' },
  ];

  const handleGenerate = () => {
    // Check if at least one file is selected
    const selectedKeys = Object.keys(selectedFiles).filter(k => selectedFiles[k]);
    if (selectedKeys.length === 0) {
      alert('Please select at least one document to generate.');
      return;
    }

    setGenerating(true);
    setGenerationProgress(0);

    const steps = [
      'Initializing Document Assembler...',
      'Compiling Core product definitions...',
      'Mapping Database Relations & Schema tables...',
      'Drafting REST Endpoints & payload schema specifications...',
      'Integrating Deployment modules & testing configuration...',
      'Optimizing Document layout...',
      'Finalizing markdown package...',
    ];

    let currentStepIdx = 0;
    const interval = setInterval(() => {
      if (currentStepIdx < steps.length) {
        setActiveStepText(steps[currentStepIdx]);
        setGenerationProgress((p) => Math.min(p + 15, 95));
        currentStepIdx++;
      } else {
        clearInterval(interval);
        setGenerationProgress(100);
        setTimeout(() => {
          setGenerating(false);
          setIsGenerated(true);
          // Set first selected document as active preview
          const firstSelected = selectedKeys[0] || 'readme';
          setActivePreviewDoc(firstSelected);
        }, 500);
      }
    }, 400);
  };

  const handleDownloadFile = async (docId: string) => {
    const doc = documentList.find(d => d.id === docId);
    if (!doc) return;
    setDownloading(docId);
    
    try {
      const content = doc.generator(state);
      const blob = new Blob([content], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = doc.filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('[exHacker Export] Error downloading file:', err);
    } finally {
      setTimeout(() => setDownloading(null), 400);
    }
  };

  const handleDownloadAllSelected = async () => {
    const selectedKeys = Object.keys(selectedFiles).filter(k => selectedFiles[k]);
    for (const key of selectedKeys) {
      await handleDownloadFile(key);
      await new Promise(r => setTimeout(r, 250));
    }
  };

  const toggleAllGroup = (groupName: string, selectVal: boolean) => {
    const updated = { ...selectedFiles };
    documentList.forEach(d => {
      if (d.group === groupName) {
        updated[d.id] = selectVal;
      }
    });
    setSelectedFiles(updated);
  };

  const selectedKeys = Object.keys(selectedFiles).filter(k => selectedFiles[k]);

  if (generating) {
    return (
      <div style={{
        background: '#0B1020', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '16px',
        padding: '60px 40px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'
      }}>
        <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'rgba(124,58,237,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '24px', border: '1.5px dashed #7C3AED', animation: 'spin 4s linear infinite' }}>
          <Sparkles size={36} color="#7C3AED" />
        </div>
        <h3 style={{ fontSize: '20px', fontWeight: 700, color: '#F1F5F9', marginBottom: '8px' }}>Generating Package Documents</h3>
        <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)', marginBottom: '24px', fontFamily: 'monospace' }}>{activeStepText}</p>
        
        <div style={{ width: '100%', maxWidth: '400px', height: '6px', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', marginBottom: '12px', overflow: 'hidden' }}>
          <div style={{ width: `${generationProgress}%`, height: '100%', background: 'linear-gradient(90deg, #7C3AED, #06B6D4)', borderRadius: '3px', transition: 'width 250ms ease' }} />
        </div>
        <span style={{ fontSize: '13px', fontWeight: 600, color: '#A855F7' }}>{generationProgress}% complete</span>
      </div>
    );
  }

  if (isGenerated) {
    const activeDoc = documentList.find(d => d.id === activePreviewDoc)!;
    const contentPreview = activeDoc ? activeDoc.generator(state) : '';

    return (
      <div style={{ animation: 'fade-in 300ms ease-out' }}>
        {/* Header summary info */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#F1F5F9' }}>Compilation Results</h3>
            <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>Generated {selectedKeys.length} files. Click below to preview and download.</p>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={() => setIsGenerated(false)}
              style={{
                padding: '10px 18px', borderRadius: '8px', fontSize: '13px', fontWeight: 600,
                background: 'transparent', border: '1px solid rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.6)', cursor: 'pointer',
              }}
            >
              Back to Checklist
            </button>
            <button
              onClick={handleDownloadAllSelected}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '10px 20px', borderRadius: '8px',
                background: 'linear-gradient(135deg, #22C55E, #10B981)',
                color: '#fff', fontSize: '13px', fontWeight: 600,
                border: 'none', cursor: 'pointer',
                boxShadow: '0 0 15px rgba(34,197,94,0.3)',
              }}
            >
              <Package size={14} /> Download Selected ({selectedKeys.length})
            </button>
          </div>
        </div>

        {/* Split Panel */}
        <div style={{ display: 'flex', gap: '20px', alignItems: 'stretch' }}>
          {/* Left Navigation: List of generated docs */}
          <div style={{ width: '280px', flexShrink: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {documentList.map(doc => {
              if (!selectedFiles[doc.id]) return null;
              const isActive = activePreviewDoc === doc.id;
              const DocIcon = doc.icon;
              return (
                <div
                  key={doc.id}
                  onClick={() => setActivePreviewDoc(doc.id)}
                  style={{
                    background: isActive ? 'rgba(124,58,237,0.1)' : '#111827',
                    border: `1px solid ${isActive ? 'rgba(124,58,237,0.35)' : 'rgba(255,255,255,0.06)'}`,
                    borderRadius: '10px',
                    padding: '12px 16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                    transition: 'all 150ms ease',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ width: '28px', height: '28px', borderRadius: '6px', background: `rgba(${hexToRgb(doc.color)}, 0.12)`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: doc.color }}>
                      <DocIcon size={14} />
                    </div>
                    <div>
                      <span style={{ fontSize: '13px', fontWeight: 600, color: isActive ? '#fff' : 'rgba(255,255,255,0.7)' }}>{doc.label}</span>
                      <span style={{ display: 'block', fontSize: '10px', color: 'rgba(255,255,255,0.35)' }}>{doc.group === 'core' ? 'Core file' : 'Doc asset'}</span>
                    </div>
                  </div>
                  <ChevronRight size={14} color={isActive ? '#A855F7' : 'rgba(255,255,255,0.2)'} />
                </div>
              );
            })}
          </div>

          {/* Right Preview Box */}
          <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', background: '#0B1020', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '12px', overflow: 'hidden' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 20px', borderBottom: '1px solid rgba(255,255,255,0.06)', background: 'rgba(255,255,255,0.01)' }}>
              <div>
                <span style={{ fontSize: '14px', fontWeight: 700, color: '#fff' }}>{activeDoc.label}</span>
                <span style={{ marginLeft: '12px', fontSize: '11px', color: 'rgba(255,255,255,0.3)' }}>{(contentPreview.length / 1024).toFixed(2)} KB • Markdown</span>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={() => navigator.clipboard?.writeText(contentPreview)}
                  style={{
                    padding: '6px 12px', borderRadius: '6px', fontSize: '12px', fontWeight: 500,
                    background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)', color: 'rgba(255,255,255,0.6)',
                    cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px',
                  }}
                >
                  <Copy size={12} /> Copy
                </button>
                <button
                  onClick={() => handleDownloadFile(activePreviewDoc)}
                  disabled={downloading === activePreviewDoc}
                  style={{
                    padding: '6px 12px', borderRadius: '6px', fontSize: '12px', fontWeight: 600,
                    background: 'rgba(59,130,246,0.12)', border: '1px solid rgba(59,130,246,0.25)', color: '#3B82F6',
                    cursor: downloading === activePreviewDoc ? 'default' : 'pointer', display: 'flex', alignItems: 'center', gap: '4px',
                  }}
                >
                  {downloading === activePreviewDoc ? (
                    <div style={{ width: '12px', height: '12px', border: '1.5px solid rgba(59,130,246,0.4)', borderTopColor: '#3B82F6', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                  ) : (
                    <><Download size={12} /> Download</>
                  )}
                </button>
              </div>
            </div>
            
            {/* Terminal Prebox */}
            <div style={{ padding: '24px', flex: 1, maxHeight: '480px', overflowY: 'auto' }}>
              <pre style={{
                margin: 0,
                fontFamily: '"Fira Code", "JetBrains Mono", monospace',
                fontSize: '13px',
                lineHeight: 1.7,
                color: 'rgba(255,255,255,0.7)',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}>{contentPreview}</pre>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ animation: 'fade-in 200ms ease-out' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.4)' }}>
          Select the documents you wish to compile in detailed markdown.
        </p>
        <button
          onClick={handleGenerate}
          style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            padding: '12px 24px', borderRadius: '8px',
            background: 'linear-gradient(135deg, #7C3AED, #06B6D4)',
            color: '#fff', fontSize: '14px', fontWeight: 700,
            border: 'none', cursor: 'pointer',
            boxShadow: '0 0 20px rgba(124,58,237,0.3)',
          }}
        >
          <Sparkles size={14} /> Generate Selected ({selectedKeys.length})
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }}>
        {/* Core Documents checklist */}
        <div style={{ background: '#111827', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.06)', padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '12px' }}>
            <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#3B82F6', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Core Specs (P0)</h4>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button onClick={() => toggleAllGroup('core', true)} style={{ background: 'transparent', border: 'none', color: '#A855F7', fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}>Select All</button>
              <span style={{ color: 'rgba(255,255,255,0.1)' }}>|</span>
              <button onClick={() => toggleAllGroup('core', false)} style={{ background: 'transparent', border: 'none', color: 'rgba(255,255,255,0.35)', fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}>Clear</button>
            </div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {documentList.filter(d => d.group === 'core').map(doc => {
              const DocIcon = doc.icon;
              return (
                <label key={doc.id} style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={!!selectedFiles[doc.id]}
                    onChange={(e) => setSelectedFiles(f => ({ ...f, [doc.id]: e.target.checked }))}
                    style={{ marginTop: '4px', accentColor: '#7C3AED' }}
                  />
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ color: doc.color, display: 'flex' }}><DocIcon size={12} /></span>
                      <span style={{ fontSize: '14px', fontWeight: 600, color: '#F1F5F9' }}>{doc.label}</span>
                    </div>
                    <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)', marginTop: '2px' }}>{doc.desc}</p>
                  </div>
                </label>
              );
            })}
          </div>
        </div>

        {/* Recommended Documents checklist */}
        <div style={{ background: '#111827', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.06)', padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '12px' }}>
            <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#10B981', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Recommended (P1)</h4>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button onClick={() => toggleAllGroup('recommended', true)} style={{ background: 'transparent', border: 'none', color: '#A855F7', fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}>Select All</button>
              <span style={{ color: 'rgba(255,255,255,0.1)' }}>|</span>
              <button onClick={() => toggleAllGroup('recommended', false)} style={{ background: 'transparent', border: 'none', color: 'rgba(255,255,255,0.35)', fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}>Clear</button>
            </div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {documentList.filter(d => d.group === 'recommended').map(doc => {
              const DocIcon = doc.icon;
              return (
                <label key={doc.id} style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={!!selectedFiles[doc.id]}
                    onChange={(e) => setSelectedFiles(f => ({ ...f, [doc.id]: e.target.checked }))}
                    style={{ marginTop: '4px', accentColor: '#7C3AED' }}
                  />
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ color: doc.color, display: 'flex' }}><DocIcon size={12} /></span>
                      <span style={{ fontSize: '14px', fontWeight: 600, color: '#F1F5F9' }}>{doc.label}</span>
                    </div>
                    <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)', marginTop: '2px' }}>{doc.desc}</p>
                  </div>
                </label>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

function generateSlides(state: any) {
  const slides = state?.presentation?.slide_content || [];
  return `# Presentation Slides Document\n\n${slides.map((s: any, i: number) =>
  `## Slide ${i + 1}: ${s.title}\n\n${(s.content || []).map((c: string) => `- ${c}`).join('\n')}\n\n${s.visual_notes ? `> Visual: ${s.visual_notes}` : ''}`
).join('\n\n') || ['Title & Hook', 'Problem', 'Solution', 'Demo', 'Architecture', 'Business Model', 'Team', 'CTA'].map((t, i) => `## Slide ${i + 1}: ${t}\n\n*Content for this slide*`).join('\n\n')}\n`;
}

function generateImplGuide(state: any) {
  const bp = state?.build_package || {};
  const idea = state?.selected_idea || {};
  return `# Build Guide — ${idea.title || DEMO_FINANCE_PROJECT.name}\n\n## Frontend Tasks\n\n${(bp.frontend_tasks || []).map((t: string) => `- [ ] ${t}`).join('\n')}\n\n## Backend Tasks\n\n${(bp.backend_tasks || []).map((t: string) => `- [ ] ${t}`).join('\n')}\n\n## Database Tasks\n\n${(bp.database_tasks || []).map((t: string) => `- [ ] ${t}`).join('\n')}\n\n## Testing\n\n${(bp.testing_tasks || []).map((t: string) => `- [ ] ${t}`).join('\n')}\n\n## Deployment\n\n${(bp.deployment_tasks || []).map((t: string) => `- [ ] ${t}`).join('\n')}\n`;
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
    if (!wId || projectId === 'demo-finance-001') return;

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

  const isLiveData = !!(projectState && projectId !== 'demo-finance-001');

  const tabContent: Record<string, React.ReactNode> = {
    overview: <OverviewTab state={projectState} />,
    architecture: <ArchitectureTab state={projectState} />,
    tech: <TechStackTab state={projectState} />,
    build: <BuildPlanTab state={projectState} />,
    presentation: <PresentationTab state={projectState} />,
    pitch: <PitchTab state={projectState} />,
    research: <ResearchTab state={projectState} />,
    export: <ExportTab state={projectState} projectId={projectId} />,
  };

  return (
    <div style={{ background: '#050816', minHeight: '100vh', color: '#F1F5F9' }}>
      <Navbar />
      <div style={{ paddingTop: '80px' }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(124,58,237,0.06) 0%, rgba(6,182,212,0.04) 100%)',
          borderBottom: '1px solid rgba(255,255,255,0.06)',
          padding: '32px 32px 0',
        }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                  <h1 style={{ fontSize: '28px', fontWeight: 700, letterSpacing: '-0.02em' }}>{projectName}</h1>
                  {loading ? (
                    <div style={{ padding: '4px 14px', borderRadius: '99px', background: 'rgba(59,130,246,0.1)', color: '#3B82F6', fontSize: '12px', fontWeight: 600, border: '1px solid rgba(59,130,246,0.25)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <RefreshCw size={10} style={{ animation: 'spin 1s linear infinite' }} />
                      Loading...
                    </div>
                  ) : (
                    <div style={{ padding: '4px 14px', borderRadius: '99px', background: 'rgba(34,197,94,0.1)', color: '#22C55E', fontSize: '12px', fontWeight: 600, border: '1px solid rgba(34,197,94,0.25)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <CheckCircle size={10} />
                      {isLiveData ? 'Live Results' : 'Demo Mode'}
                    </div>
                  )}
                </div>
                <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: '14px' }}>
                  Generated {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                  {isLiveData && <span style={{ marginLeft: '8px', color: '#22C55E', fontWeight: 500 }}>— AI Generated</span>}
                </p>
              </div>

              <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
                {/* Score */}
                <div style={{
                  padding: '12px 20px', borderRadius: '12px',
                  background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)',
                  display: 'flex', alignItems: 'center', gap: '10px',
                }}>
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
                    padding: '10px 20px', borderRadius: '10px',
                    background: 'rgba(124,58,237,0.15)',
                    color: '#A855F7', fontSize: '14px', fontWeight: 600,
                    textDecoration: 'none', border: '1px solid rgba(124,58,237,0.3)',
                  }}
                >
                  <Play size={14} /> Present
                </Link>
                <button
                  style={{
                    display: 'flex', alignItems: 'center', gap: '6px',
                    padding: '10px 20px', borderRadius: '10px',
                    background: '#7C3AED', color: '#fff',
                    fontSize: '14px', fontWeight: 600, border: 'none', cursor: 'pointer',
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
                      padding: '12px 18px', fontSize: '13px',
                      fontWeight: isActive ? 600 : 400, cursor: 'pointer',
                      border: 'none',
                      borderBottom: `2px solid ${isActive ? '#7C3AED' : 'transparent'}`,
                      background: 'transparent',
                      color: isActive ? '#A855F7' : 'rgba(255,255,255,0.4)',
                      transition: 'all 150ms ease', whiteSpace: 'nowrap',
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
