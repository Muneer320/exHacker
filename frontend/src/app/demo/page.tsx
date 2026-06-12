'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { Play, Pause, RotateCcw, SkipForward, ChevronLeft, Zap, Target, Brain, Search, Lightbulb, CheckCircle, GitBranch, Mic, ArrowRight } from 'lucide-react';
import { DEMO_FINANCE_PROJECT } from '@/mock/data';

// ─── Demo Scene Definitions ──────────────────────────────────────────────────
const SCENES = [
  {
    id: 'challenge',
    title: 'Challenge Received',
    narration: 'exHacker begins by understanding the challenge.',
    duration: 5000,
    type: 'challenge',
  },
  {
    id: 'analysis',
    title: 'Problem Analysis',
    narration: 'The Problem Analyst maps stakeholders and pain points.',
    duration: 8000,
    type: 'analysis',
  },
  {
    id: 'research',
    title: 'Research Phase',
    narration: 'The Research Engine finds competitors, APIs, and market insights.',
    duration: 10000,
    type: 'research',
  },
  {
    id: 'ideas',
    title: 'Idea Generation',
    narration: '5 unique ideas generated and scored in real-time.',
    duration: 12000,
    type: 'ideas',
  },
  {
    id: 'selection',
    title: 'Best Idea Selected',
    narration: 'AI selects the highest-scoring idea by innovation and feasibility.',
    duration: 5000,
    type: 'selection',
  },
  {
    id: 'architecture',
    title: 'Architecture Generated',
    narration: 'Full system architecture designed — frontend to AI layer.',
    duration: 10000,
    type: 'architecture',
  },
  {
    id: 'pitch',
    title: 'Pitch Created',
    narration: '30-second and 2-minute pitches with judge Q&A prep.',
    duration: 10000,
    type: 'pitch',
  },
  {
    id: 'dashboard',
    title: 'Project Complete',
    narration: 'Your complete hackathon package is ready.',
    duration: 10000,
    type: 'dashboard',
  },
];

// ─── Scene Renderers ──────────────────────────────────────────────────────────
function ChallengeScene() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
      <div
        style={{
          maxWidth: '640px',
          padding: '48px',
          background: 'rgba(6,182,212,0.06)',
          borderRadius: '24px',
          border: '1px solid rgba(6,182,212,0.25)',
          textAlign: 'center',
          animation: 'scene-in 600ms cubic-bezier(0.16,1,0.3,1)',
          boxShadow: '0 0 60px rgba(6,182,212,0.1)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '24px' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '18px', background: 'rgba(6,182,212,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Target size={32} color="#06B6D4" />
          </div>
        </div>
        <p style={{ fontSize: '13px', fontWeight: 600, color: '#06B6D4', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: '16px' }}>Challenge Received</p>
        <p style={{ fontSize: '22px', fontWeight: 700, color: '#F1F5F9', lineHeight: 1.4 }}>
          {DEMO_FINANCE_PROJECT.challenge}
        </p>
        <p style={{ marginTop: '20px', fontSize: '14px', color: 'rgba(255,255,255,0.4)' }}>Theme: {DEMO_FINANCE_PROJECT.theme}</p>
      </div>
    </div>
  );
}

function AnalysisScene({ elapsed, duration }: { elapsed: number; duration: number }) {
  const items = [
    { label: 'Stakeholders', value: 'Students, Parents, Financial Institutions', icon: '👥' },
    { label: 'Pain Points', value: 'Low financial awareness, No budgeting habits', icon: '⚡' },
    { label: 'Constraints', value: 'Limited income, Student time constraints', icon: '🔒' },
    { label: 'Success Metrics', value: 'User retention, Habit formation rate', icon: '📊' },
  ];
  const visibleCount = Math.min(Math.floor((elapsed / duration) * (items.length + 1)), items.length);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', animation: 'scene-in 400ms ease-out' }}>
        <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: 'rgba(139,92,246,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Brain size={24} color="#8B5CF6" />
        </div>
        <div>
          <p style={{ fontSize: '22px', fontWeight: 700 }}>Problem Analyst</p>
          <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.4)' }}>Analyzing challenge structure...</p>
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', maxWidth: '600px', width: '100%' }}>
        {items.map((item, i) => (
          <div
            key={i}
            style={{
              background: '#0B1020', borderRadius: '12px', border: '1px solid rgba(139,92,246,0.2)',
              padding: '16px',
              opacity: i < visibleCount ? 1 : 0,
              transform: i < visibleCount ? 'translateY(0)' : 'translateY(12px)',
              transition: 'all 400ms cubic-bezier(0.16,1,0.3,1)',
            }}
          >
            <p style={{ fontSize: '20px', marginBottom: '8px' }}>{item.icon}</p>
            <p style={{ fontSize: '12px', fontWeight: 600, color: '#8B5CF6', marginBottom: '4px' }}>{item.label}</p>
            <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.55)' }}>{item.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function ResearchScene({ elapsed, duration }: { elapsed: number; duration: number }) {
  const { research } = DEMO_FINANCE_PROJECT;
  const allItems = [
    ...research.competitors.map((c) => ({ type: 'competitor', label: c.name, sub: c.description, color: '#EF4444' })),
    ...research.apis.map((a) => ({ type: 'api', label: a.name, sub: a.purpose, color: '#3B82F6' })),
    ...research.ossProjects.map((o) => ({ type: 'oss', label: o.name, sub: o.relevance, color: '#22C55E' })),
  ];
  const visibleCount = Math.min(Math.floor((elapsed / duration) * (allItems.length + 1)), allItems.length);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: 'rgba(245,158,11,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Search size={24} color="#F59E0B" />
        </div>
        <div>
          <p style={{ fontSize: '22px', fontWeight: 700 }}>Research Engine</p>
          <p style={{ fontSize: '14px', color: '#F59E0B' }}>
            {visibleCount} / {allItems.length} sources found
          </p>
        </div>
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', justifyContent: 'center', maxWidth: '700px' }}>
        {allItems.map((item, i) => (
          <div
            key={i}
            style={{
              padding: '10px 16px', borderRadius: '10px',
              background: `rgba(${item.color === '#EF4444' ? '239,68,68' : item.color === '#3B82F6' ? '59,130,246' : '34,197,94'}, 0.1)`,
              border: `1px solid ${item.color}30`,
              opacity: i < visibleCount ? 1 : 0,
              transform: i < visibleCount ? 'scale(1)' : 'scale(0.8)',
              transition: 'all 350ms cubic-bezier(0.16,1,0.3,1)',
            }}
          >
            <p style={{ fontSize: '12px', fontWeight: 600, color: item.color, marginBottom: '2px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{item.type}</p>
            <p style={{ fontSize: '14px', fontWeight: 600 }}>{item.label}</p>
            <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)' }}>{item.sub}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function IdeasScene({ elapsed, duration }: { elapsed: number; duration: number }) {
  const ideas = DEMO_FINANCE_PROJECT.ideas;
  const visibleCount = Math.min(Math.floor((elapsed / duration) * (ideas.length + 1)), ideas.length);
  const colors = ['#EC4899', '#7C3AED', '#22C55E', '#3B82F6', '#F59E0B'];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
        <Lightbulb size={28} color="#EC4899" />
        <p style={{ fontSize: '22px', fontWeight: 700 }}>Idea Generation — {visibleCount} / {ideas.length}</p>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', width: '100%', maxWidth: '640px' }}>
        {ideas.map((idea, i) => {
          const avg = Math.round((idea.scores.innovation + idea.scores.feasibility + idea.scores.differentiation) / 3);
          return (
            <div
              key={i}
              style={{
                background: '#0B1020', borderRadius: '12px', border: `1px solid rgba(${colors[i] === '#EC4899' ? '236,72,153' : colors[i] === '#7C3AED' ? '124,58,237' : colors[i] === '#22C55E' ? '34,197,94' : colors[i] === '#3B82F6' ? '59,130,246' : '245,158,11'}, 0.25)`,
                padding: '16px 20px',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                opacity: i < visibleCount ? 1 : 0,
                transform: i < visibleCount ? 'translateX(0)' : 'translateX(-20px)',
                transition: 'all 400ms cubic-bezier(0.16,1,0.3,1)',
              }}
            >
              <div>
                <p style={{ fontWeight: 600, marginBottom: '4px' }}>{idea.title}</p>
                <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>{idea.tagline}</p>
              </div>
              <div style={{ textAlign: 'right', flexShrink: 0, marginLeft: '16px' }}>
                <p style={{ fontSize: '24px', fontWeight: 800, color: colors[i], lineHeight: 1 }}>{avg}</p>
                <p style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)' }}>score</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function SelectionScene() {
  const idea = DEMO_FINANCE_PROJECT.ideas[0];
  const reasons = ['Highest innovation score (92)', 'Strong feasibility (88)', 'Maximum differentiation (90)'];
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
      <div style={{ maxWidth: '560px', textAlign: 'center', animation: 'scene-in 600ms ease-out' }}>
        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'inline-flex', padding: '8px 20px', borderRadius: '99px', background: 'rgba(34,197,94,0.12)', color: '#22C55E', fontSize: '14px', fontWeight: 600, border: '1px solid rgba(34,197,94,0.3)', gap: '8px', alignItems: 'center' }}>
            <CheckCircle size={14} /> Best Idea Selected
          </div>
        </div>
        <div style={{ background: '#0B1020', borderRadius: '20px', border: '2px solid rgba(34,197,94,0.4)', padding: '32px', boxShadow: '0 0 40px rgba(34,197,94,0.15)', marginBottom: '20px' }}>
          <p style={{ fontSize: '28px', fontWeight: 800, marginBottom: '12px' }}>{idea.title}</p>
          <p style={{ fontSize: '16px', color: 'rgba(255,255,255,0.55)' }}>{idea.tagline}</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
          {reasons.map((r, i) => (
            <span key={i} style={{ padding: '6px 14px', borderRadius: '8px', fontSize: '13px', background: 'rgba(34,197,94,0.08)', color: '#22C55E', border: '1px solid rgba(34,197,94,0.2)' }}>
              ✓ {r}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

function ArchitectureScene({ elapsed, duration }: { elapsed: number; duration: number }) {
  const components = [
    { name: 'Next.js Frontend', emoji: '🖥️', color: '#3B82F6', delay: 0 },
    { name: 'FastAPI Backend', emoji: '⚙️', color: '#7C3AED', delay: 1 },
    { name: 'PostgreSQL', emoji: '💾', color: '#F59E0B', delay: 2 },
    { name: 'Groq LLM', emoji: '🤖', color: '#22C55E', delay: 3 },
    { name: 'Tavily Search', emoji: '🔍', color: '#06B6D4', delay: 4 },
  ];
  const visibleCount = Math.min(Math.floor((elapsed / duration) * (components.length + 1)), components.length);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <GitBranch size={28} color="#3B82F6" />
        <p style={{ fontSize: '22px', fontWeight: 700 }}>Architecture Building...</p>
      </div>
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'center' }}>
        {components.map((c, i) => (
          <div
            key={i}
            style={{
              background: '#0B1020', borderRadius: '16px', border: `1px solid rgba(${c.color === '#3B82F6' ? '59,130,246' : c.color === '#7C3AED' ? '124,58,237' : c.color === '#F59E0B' ? '245,158,11' : c.color === '#22C55E' ? '34,197,94' : '6,182,212'}, 0.3)`,
              padding: '20px 24px', textAlign: 'center', minWidth: '140px',
              opacity: i < visibleCount ? 1 : 0,
              transform: i < visibleCount ? 'translateY(0)' : 'translateY(20px)',
              transition: 'all 400ms cubic-bezier(0.16,1,0.3,1)',
            }}
          >
            <p style={{ fontSize: '28px', marginBottom: '8px' }}>{c.emoji}</p>
            <p style={{ fontSize: '14px', fontWeight: 600 }}>{c.name}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function PitchScene({ elapsed, duration }: { elapsed: number; duration: number }) {
  const { pitch } = DEMO_FINANCE_PROJECT;
  const showTwoMin = elapsed > duration * 0.4;
  const showQA = elapsed > duration * 0.75;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
        <Mic size={28} color="#F97316" />
        <p style={{ fontSize: '22px', fontWeight: 700 }}>Pitch Generation</p>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', width: '100%', maxWidth: '640px' }}>
        <div style={{ background: '#0B1020', borderRadius: '12px', border: '1px solid rgba(34,197,94,0.3)', padding: '20px' }}>
          <p style={{ fontSize: '12px', fontWeight: 600, color: '#22C55E', marginBottom: '10px' }}>30-SECOND PITCH</p>
          <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.7)', lineHeight: 1.6 }}>
            {pitch.thirtySecond.slice(0, 200)}...
          </p>
        </div>
        <div style={{ background: '#0B1020', borderRadius: '12px', border: `1px solid rgba(124,58,237,${showTwoMin ? '0.3' : '0.06'})`, padding: '20px', opacity: showTwoMin ? 1 : 0.3, transition: 'all 400ms ease' }}>
          <p style={{ fontSize: '12px', fontWeight: 600, color: '#7C3AED', marginBottom: '10px' }}>2-MINUTE PITCH</p>
          <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.5)' }}>
            {showTwoMin ? `${pitch.twoMinute.slice(0, 150)}...` : 'Generating...'}
          </p>
        </div>
        <div style={{ background: '#0B1020', borderRadius: '12px', border: `1px solid rgba(249,115,22,${showQA ? '0.3' : '0.06'})`, padding: '20px', opacity: showQA ? 1 : 0.3, transition: 'all 400ms ease' }}>
          <p style={{ fontSize: '12px', fontWeight: 600, color: '#F97316', marginBottom: '10px' }}>JUDGE Q&A — {pitch.judgeQA.length} questions prepared</p>
          <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.5)' }}>
            {showQA ? pitch.judgeQA.map((q) => q.question).join(' • ') : 'Generating...'}
          </p>
        </div>
      </div>
    </div>
  );
}

function DashboardScene() {
  const p = DEMO_FINANCE_PROJECT;
  const idea = p.ideas[0];
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
      <div style={{ maxWidth: '700px', width: '100%', animation: 'scene-in 600ms ease-out' }}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <p style={{ fontSize: '14px', color: '#22C55E', fontWeight: 600, marginBottom: '8px' }}>🎉 Project Package Complete</p>
          <p style={{ fontSize: '28px', fontWeight: 800 }}>{p.name}</p>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginBottom: '16px' }}>
          {[
            { label: 'Score', value: `${p.overallScore}/100`, color: '#F59E0B' },
            { label: 'Innovation', value: `${idea.scores.innovation}`, color: '#EC4899' },
            { label: 'Feasibility', value: `${idea.scores.feasibility}`, color: '#22C55E' },
            { label: 'Agents', value: '10', color: '#7C3AED' },
          ].map((m) => (
            <div key={m.label} style={{ background: '#0B1020', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)', padding: '14px', textAlign: 'center' }}>
              <p style={{ fontSize: '24px', fontWeight: 800, color: m.color }}>{m.value}</p>
              <p style={{ fontSize: '11px', color: 'rgba(255,255,255,0.4)' }}>{m.label}</p>
            </div>
          ))}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
          {['Architecture', 'Pitch Deck', 'Research', 'Build Plan', 'Presentation', 'Export Ready'].map((item) => (
            <div key={item} style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#0B1020', borderRadius: '10px', border: '1px solid rgba(34,197,94,0.2)', padding: '12px' }}>
              <CheckCircle size={14} color="#22C55E" />
              <span style={{ fontSize: '13px', fontWeight: 500 }}>{item}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Controls ─────────────────────────────────────────────────────────────────
function DemoControls({
  playing, sceneIndex, totalScenes, progress,
  onPlay, onPause, onRestart, onSkip, onPrev,
}: {
  playing: boolean; sceneIndex: number; totalScenes: number; progress: number;
  onPlay: () => void; onPause: () => void; onRestart: () => void; onSkip: () => void; onPrev: () => void;
}) {
  return (
    <div
      style={{
        position: 'absolute', bottom: '32px', left: '50%', transform: 'translateX(-50%)',
        background: 'rgba(11,16,32,0.95)', backdropFilter: 'blur(20px)',
        borderRadius: '16px', border: '1px solid rgba(255,255,255,0.1)',
        padding: '16px 24px', display: 'flex', alignItems: 'center', gap: '16px',
        zIndex: 10,
      }}
    >
      {/* Scene dots */}
      <div style={{ display: 'flex', gap: '6px' }}>
        {Array.from({ length: totalScenes }).map((_, i) => (
          <div key={i} style={{ width: '6px', height: '6px', borderRadius: '50%', background: i === sceneIndex ? '#7C3AED' : i < sceneIndex ? '#22C55E' : 'rgba(255,255,255,0.15)', transition: 'all 200ms ease' }} />
        ))}
      </div>

      <div style={{ width: '1px', height: '20px', background: 'rgba(255,255,255,0.1)' }} />

      {/* Buttons */}
      <button onClick={onPrev} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.5)', display: 'flex', alignItems: 'center' }}>
        <ChevronLeft size={18} />
      </button>
      <button
        onClick={playing ? onPause : onPlay}
        style={{
          width: '40px', height: '40px', borderRadius: '10px', background: '#7C3AED', border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff',
        }}
      >
        {playing ? <Pause size={16} /> : <Play size={16} />}
      </button>
      <button onClick={onSkip} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.5)', display: 'flex', alignItems: 'center' }}>
        <SkipForward size={16} />
      </button>

      <div style={{ width: '1px', height: '20px', background: 'rgba(255,255,255,0.1)' }} />

      <button onClick={onRestart} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.5)', display: 'flex', alignItems: 'center' }}>
        <RotateCcw size={14} />
      </button>

      {/* Progress bar */}
      <div style={{ width: '120px', height: '3px', borderRadius: '99px', background: 'rgba(255,255,255,0.1)' }}>
        <div style={{ height: '100%', width: `${progress}%`, borderRadius: '99px', background: '#7C3AED', transition: 'width 200ms linear' }} />
      </div>
      <span style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)', whiteSpace: 'nowrap' }}>
        {sceneIndex + 1} / {totalScenes}
      </span>
    </div>
  );
}

// ─── Main Demo Page ────────────────────────────────────────────────────────────
export default function DemoPage() {
  const [sceneIndex, setSceneIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | undefined>(undefined);
  const scene = SCENES[sceneIndex];
  const progress = Math.min((elapsed / scene.duration) * 100, 100);

  useEffect(() => {
    if (playing) {
      timerRef.current = setInterval(() => {
        setElapsed((e) => {
          if (e >= scene.duration) {
            if (sceneIndex < SCENES.length - 1) {
              setSceneIndex((s) => s + 1);
              return 0;
            } else {
              setPlaying(false);
              return scene.duration;
            }
          }
          return e + 100;
        });
      }, 100);
    }
    return () => clearInterval(timerRef.current);
  }, [playing, scene.duration, sceneIndex]);

  const handleSceneChange = (newIndex: number) => {
    setSceneIndex(Math.max(0, Math.min(newIndex, SCENES.length - 1)));
    setElapsed(0);
  };

  useEffect(() => { handleSceneChange(0); }, []);

  // Keyboard controls
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.code === 'Space') { e.preventDefault(); setPlaying((p) => !p); }
      if (e.code === 'ArrowRight') handleSceneChange(sceneIndex + 1);
      if (e.code === 'ArrowLeft') handleSceneChange(sceneIndex - 1);
      if (e.code === 'KeyR') { handleSceneChange(0); setPlaying(false); }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [sceneIndex]);

  const renderScene = () => {
    const props = { elapsed, duration: scene.duration };
    switch (scene.type) {
      case 'challenge': return <ChallengeScene />;
      case 'analysis': return <AnalysisScene {...props} />;
      case 'research': return <ResearchScene {...props} />;
      case 'ideas': return <IdeasScene {...props} />;
      case 'selection': return <SelectionScene />;
      case 'architecture': return <ArchitectureScene {...props} />;
      case 'pitch': return <PitchScene {...props} />;
      case 'dashboard': return <DashboardScene />;
      default: return null;
    }
  };

  return (
    <div
      style={{
        background: '#050816', minHeight: '100vh', color: '#F1F5F9',
        display: 'flex', flexDirection: 'column',
      }}
    >
      {/* Demo Navbar */}
      <div
        style={{
          position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
          height: '56px',
          background: 'rgba(5,8,22,0.9)', backdropFilter: 'blur(16px)',
          borderBottom: '1px solid rgba(255,255,255,0.06)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0 24px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '28px', height: '28px', borderRadius: '7px', background: 'linear-gradient(135deg,#7C3AED,#06B6D4)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Zap size={14} color="#fff" />
          </div>
          <span style={{ fontWeight: 700, fontSize: '16px' }}>exHacker</span>
          <span style={{ padding: '2px 10px', borderRadius: '99px', fontSize: '11px', background: 'rgba(124,58,237,0.12)', color: '#A855F7', border: '1px solid rgba(124,58,237,0.25)' }}>Demo Mode</span>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Link href="/" style={{ padding: '6px 14px', borderRadius: '8px', fontSize: '13px', color: 'rgba(255,255,255,0.5)', textDecoration: 'none', border: '1px solid rgba(255,255,255,0.08)' }}>Exit</Link>
          <Link href="/new-project" style={{ padding: '6px 16px', borderRadius: '8px', fontSize: '13px', background: '#7C3AED', color: '#fff', textDecoration: 'none', fontWeight: 600 }}>Start Real Project</Link>
        </div>
      </div>

      {/* Scene Container */}
      <div style={{ flex: 1, paddingTop: '56px', position: 'relative' }}>
        {/* Top Progress Bar */}
        <div style={{ position: 'absolute', top: '56px', left: 0, right: 0, height: '2px', background: 'rgba(255,255,255,0.06)', zIndex: 5 }}>
          <div style={{ height: '100%', width: `${((sceneIndex + progress / 100) / SCENES.length) * 100}%`, background: 'linear-gradient(90deg,#7C3AED,#06B6D4)', transition: 'width 200ms linear' }} />
        </div>

        {/* Narration Overlay */}
        <div
          style={{
            position: 'absolute', top: '80px', left: '50%', transform: 'translateX(-50%)',
            background: 'rgba(11,16,32,0.9)', backdropFilter: 'blur(12px)',
            borderRadius: '10px', border: '1px solid rgba(255,255,255,0.08)',
            padding: '10px 20px', zIndex: 5, whiteSpace: 'nowrap',
          }}
        >
          <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.6)' }}>
            <span style={{ color: '#A855F7', fontWeight: 600 }}>{scene.title}</span>
            {' — '}
            {scene.narration}
          </p>
        </div>

        {/* Scene */}
        <div
          key={sceneIndex}
          style={{
            height: 'calc(100vh - 56px)',
            padding: '100px 32px 120px',
            animation: 'scene-in 500ms cubic-bezier(0.16,1,0.3,1)',
          }}
        >
          {renderScene()}
        </div>

        {/* Not playing overlay */}
        {!playing && elapsed === 0 && sceneIndex === 0 && (
          <div
            style={{
              position: 'absolute', inset: '56px 0 0 0',
              background: 'rgba(5,8,22,0.7)', backdropFilter: 'blur(4px)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              zIndex: 4, flexDirection: 'column', gap: '24px',
            }}
            onClick={() => setPlaying(true)}
          >
            <div
              style={{
                width: '80px', height: '80px', borderRadius: '50%',
                background: '#7C3AED', display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer', boxShadow: '0 0 40px rgba(124,58,237,0.5)',
                animation: 'glow-pulse 2s ease-in-out infinite',
              }}
            >
              <Play size={32} color="#fff" />
            </div>
            <p style={{ fontSize: '16px', color: 'rgba(255,255,255,0.6)' }}>Click to start • <kbd style={{ padding: '2px 6px', borderRadius: '4px', background: 'rgba(255,255,255,0.08)', fontSize: '12px' }}>Space</kbd> to pause</p>
          </div>
        )}

        {/* Controls */}
        <DemoControls
          playing={playing} sceneIndex={sceneIndex} totalScenes={SCENES.length} progress={progress}
          onPlay={() => setPlaying(true)} onPause={() => setPlaying(false)}
          onRestart={() => { handleSceneChange(0); setPlaying(true); }}
          onSkip={() => handleSceneChange(sceneIndex + 1)}
          onPrev={() => handleSceneChange(sceneIndex - 1)}
        />
      </div>

      <style>{`
        @keyframes scene-in { from { opacity: 0; transform: translateY(16px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
        @keyframes glow-pulse { 0%,100% { box-shadow: 0 0 40px rgba(124,58,237,0.5); } 50% { box-shadow: 0 0 80px rgba(124,58,237,0.8); } }
        kbd { font-family: 'Inter', sans-serif; }
      `}</style>
    </div>
  );
}
