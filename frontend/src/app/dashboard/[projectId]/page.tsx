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

      <div>
        <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={14} color="#F59E0B" /> Market Insights
        </h3>
        {(insights || []).map((insight: string, i: number) => (
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
function ExportTab({ state, projectId }: { state?: any; projectId: string }) {
  const [exporting, setExporting] = useState<string | null>(null);
  const [done, setDone] = useState<Set<string>>(new Set());

  const exports = [
    {
      id: 'readme',
      label: 'README.md',
      desc: 'Complete project documentation',
      color: '#22C55E',
      icon: FileText,
      getContent: () => state?.exports?.readme || generateReadme(state),
      filename: 'README.md',
      mimeType: 'text/markdown',
    },
    {
      id: 'prd',
      label: 'Architecture Doc',
      desc: 'System design & component breakdown',
      color: '#3B82F6',
      icon: GitBranch,
      getContent: () => state?.exports?.architecture_doc || generateArchDoc(state),
      filename: 'ARCHITECTURE.md',
      mimeType: 'text/markdown',
    },
    {
      id: 'pitch',
      label: 'Pitch Guide',
      desc: '30s, 2min, 5min pitches + Q&A',
      color: '#EC4899',
      icon: Mic,
      getContent: () => state?.exports?.pitch_doc || generatePitchDoc(state),
      filename: 'PITCH_GUIDE.md',
      mimeType: 'text/markdown',
    },
    {
      id: 'slides',
      label: 'Presentation',
      desc: 'Full slide deck content',
      color: '#A855F7',
      icon: Presentation,
      getContent: () => state?.exports?.presentation_doc || generatePresDoc(state),
      filename: 'PRESENTATION.md',
      mimeType: 'text/markdown',
    },
    {
      id: 'impl',
      label: 'Build Guide',
      desc: 'Implementation tasks & prompts',
      color: '#F59E0B',
      icon: Code2,
      getContent: () => state?.exports?.implementation_guide || generateImplGuide(state),
      filename: 'BUILD_GUIDE.md',
      mimeType: 'text/markdown',
    },
  ];

  const handleExport = async (ex: typeof exports[0]) => {
    setExporting(ex.id);
    try {
      const content = ex.getContent();
      const blob = new Blob([content], { type: ex.mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = ex.filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setDone(prev => new Set([...prev, ex.id]));
    } catch (err) {
      console.error('Export error:', err);
    } finally {
      setTimeout(() => setExporting(null), 600);
    }
  };

  const handleDownloadAll = async () => {
    for (const ex of exports) {
      await handleExport(ex);
      await new Promise(r => setTimeout(r, 200));
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.4)' }}>
          Download your complete hackathon package — ready to submit.
        </p>
        <button
          onClick={handleDownloadAll}
          style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            padding: '10px 20px', borderRadius: '8px',
            background: 'linear-gradient(135deg, #7C3AED, #06B6D4)',
            color: '#fff', fontSize: '13px', fontWeight: 600,
            border: 'none', cursor: 'pointer',
            boxShadow: '0 0 20px rgba(124,58,237,0.3)',
          }}
        >
          <Package size={14} /> Download All
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '16px' }}>
        {exports.map((ex) => {
          const Icon = ex.icon;
          const isDone = done.has(ex.id);
          return (
            <div key={ex.id} style={{
              background: '#111827', borderRadius: '12px',
              border: `1px solid ${isDone ? 'rgba(34,197,94,0.3)' : 'rgba(255,255,255,0.06)'}`,
              padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px',
              transition: 'border-color 300ms ease',
            }}>
              <div>
                <div style={{
                  width: '40px', height: '40px', borderRadius: '10px',
                  background: `rgba(${hexToRgb(ex.color)}, 0.1)`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  marginBottom: '12px',
                }}>
                  <Icon size={18} color={ex.color} />
                </div>
                <p style={{ fontWeight: 600, marginBottom: '4px' }}>{ex.label}</p>
                <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>{ex.desc}</p>
              </div>
              <button
                onClick={() => handleExport(ex)}
                disabled={!!exporting}
                style={{
                  padding: '10px 20px', borderRadius: '8px', fontSize: '13px', fontWeight: 600,
                  cursor: exporting ? 'default' : 'pointer',
                  border: `1px solid rgba(${hexToRgb(isDone ? '#22C55E' : ex.color)}, 0.3)`,
                  background: exporting === ex.id
                    ? `rgba(${hexToRgb(ex.color)}, 0.05)`
                    : isDone
                      ? 'rgba(34,197,94,0.08)'
                      : `rgba(${hexToRgb(ex.color)}, 0.1)`,
                  color: isDone ? '#22C55E' : ex.color,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
                  transition: 'all 150ms ease',
                }}
              >
                {exporting === ex.id ? (
                  <><div style={{ width: '12px', height: '12px', border: `1.5px solid ${ex.color}40`, borderTopColor: ex.color, borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} /> Preparing...</>
                ) : isDone ? (
                  <><CheckCircle size={13} /> Downloaded</>
                ) : (
                  <><Download size={13} /> Download</>
                )}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Content generators for offline/mock state ────────────────────────────────
function generateReadme(state: any) {
  const idea = state?.selected_idea || {};
  const title = idea.title || DEMO_FINANCE_PROJECT.name;
  const desc = idea.description || DEMO_FINANCE_PROJECT.challenge;
  const features = (idea.key_features || []).map((f: string) => `- ${f}`).join('\n')
    || DEMO_FINANCE_PROJECT.ideas[0].strengths.map((s: string) => `- ${s}`).join('\n');
  const ts = state?.tech_stack || {};
  return `# ${title}\n\n> ${desc}\n\n## Features\n${features}\n\n## Tech Stack\n\n| Layer | Technology |\n|-------|------------|\n| Frontend | ${ts.frontend || 'Next.js'} |\n| Backend | ${ts.backend || 'FastAPI'} |\n| Database | ${ts.database || 'SQLite'} |\n\n## Quick Start\n\n\`\`\`bash\n# Clone the repo\ngit clone https://github.com/your-org/${title.toLowerCase().replace(/\s+/g, '-')}\n\n# Install deps\nnpm install\n\n# Start backend\ncd backend && uvicorn app.api.main:app --reload\n\n# Start frontend\nnpm run dev\n\`\`\`\n\n## License\nMIT\n`;
}

function generateArchDoc(state: any) {
  const arch = state?.architecture || {};
  const idea = state?.selected_idea || {};
  const title = idea.title || 'Solution';
  const components = (arch.components || []).map((c: any) =>
    `### ${c.name}\n\n${c.description || ''}\n\n**Responsibilities:**\n${(c.responsibilities || []).map((r: string) => `- ${r}`).join('\n')}`
  ).join('\n\n');
  return `# Architecture — ${title}\n\n## System Design\n\n${arch.system_design || 'Microservices-based architecture with AI agents.'}\n\n## Components\n\n${components || DEMO_FINANCE_PROJECT.architecture.components.map((c: any) => `### ${c.name}\n\n${c.tech}`).join('\n\n')}\n\n## MVP Scope\n\n${(arch.mvp_scope || []).map((s: string) => `- ${s}`).join('\n')}\n`;
}

function generatePitchDoc(state: any) {
  const pitch = state?.pitch || {};
  const idea = state?.selected_idea || {};
  const mock = DEMO_FINANCE_PROJECT.pitch;
  return `# Pitch Guide — ${idea.title || DEMO_FINANCE_PROJECT.name}\n\n## 30-Second Elevator Pitch\n\n${pitch.pitch_30s || mock.thirtySecond}\n\n## 2-Minute Pitch\n\n${pitch.pitch_2m || mock.twoMinute}\n\n${pitch.pitch_5m ? `## 5-Minute Deep Dive\n\n${pitch.pitch_5m}\n\n` : ''}${pitch.demo_script ? `## Demo Script\n\n${pitch.demo_script}\n\n` : ''}## Anticipated Judge Questions\n\n${(pitch.judge_questions || mock.judgeQA || []).map((qa: any) =>
  `**Q: ${qa.question}**\n\nA: ${qa.answer}`).join('\n\n')}\n`;
}

function generatePresDoc(state: any) {
  const pres = state?.presentation || {};
  const idea = state?.selected_idea || {};
  const slides = pres.slide_content || [];
  return `# Presentation — ${idea.title || DEMO_FINANCE_PROJECT.name}\n\n${slides.map((s: any, i: number) =>
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
