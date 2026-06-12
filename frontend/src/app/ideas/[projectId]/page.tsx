'use client';

import { use, useState } from 'react';
import { useRouter } from 'next/navigation';
import { CheckCircle, ArrowRight, Star, ChevronDown, ChevronUp, Zap, TrendingUp, Shield, Lightbulb } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import { DEMO_FINANCE_PROJECT } from '@/mock/data';
import { ScoreBar } from '@/components/shared/ui';

function hexToRgb(hex: string) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `${r},${g},${b}`;
}

type Idea = (typeof DEMO_FINANCE_PROJECT.ideas)[0];

function IdeaCard({
  idea,
  selected,
  dimmed,
  onSelect,
}: {
  idea: Idea;
  selected: boolean;
  dimmed: boolean;
  onSelect: () => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const avg = Math.round((idea.scores.innovation + idea.scores.feasibility + idea.scores.differentiation) / 3);
  const borderColor = selected ? '#22C55E' : dimmed ? 'rgba(255,255,255,0.04)' : 'rgba(255,255,255,0.08)';

  return (
    <div
      style={{
        background: '#0B1020',
        borderRadius: '16px',
        border: `1px solid ${borderColor}`,
        transition: 'all 300ms cubic-bezier(0.16,1,0.3,1)',
        opacity: dimmed ? 0.4 : 1,
        transform: selected ? 'scale(1.02)' : 'scale(1)',
        boxShadow: selected ? '0 0 30px rgba(34,197,94,0.2)' : 'none',
        overflow: 'hidden',
      }}
    >
      <div style={{ padding: '24px' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
          <div style={{ flex: 1, marginRight: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#F1F5F9' }}>{idea.title}</h3>
              {selected && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '2px 10px', borderRadius: '99px', background: 'rgba(34,197,94,0.12)', color: '#22C55E', fontSize: '11px', fontWeight: 600, border: '1px solid rgba(34,197,94,0.3)' }}>
                  <CheckCircle size={10} /> Selected
                </span>
              )}
            </div>
            <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.5)', lineHeight: 1.5 }}>{idea.tagline}</p>
          </div>
          {/* Score Bubble */}
          <div
            style={{
              width: '60px', height: '60px', borderRadius: '50%', flexShrink: 0,
              background: selected ? 'rgba(34,197,94,0.15)' : 'rgba(124,58,237,0.12)',
              border: `2px solid ${selected ? 'rgba(34,197,94,0.4)' : 'rgba(124,58,237,0.3)'}`,
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            }}
          >
            <span style={{ fontSize: '20px', fontWeight: 800, color: selected ? '#22C55E' : '#A855F7', lineHeight: 1 }}>{avg}</span>
            <span style={{ fontSize: '9px', color: 'rgba(255,255,255,0.3)', fontWeight: 500 }}>score</span>
          </div>
        </div>

        {/* Scores */}
        <div style={{ marginBottom: '16px' }}>
          <ScoreBar label="Innovation" value={idea.scores.innovation} color="#EC4899" />
          <ScoreBar label="Feasibility" value={idea.scores.feasibility} color="#22C55E" />
          <ScoreBar label="Differentiation" value={idea.scores.differentiation} color="#7C3AED" />
          <ScoreBar label="Complexity (lower=better)" value={100 - idea.scores.complexity} color="#F59E0B" />
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            onClick={onSelect}
            style={{
              flex: 1, padding: '10px 20px', borderRadius: '8px', fontSize: '14px', fontWeight: 600, cursor: 'pointer',
              background: selected ? 'rgba(34,197,94,0.15)' : '#7C3AED',
              color: selected ? '#22C55E' : '#fff',
              border: `1px solid ${selected ? 'rgba(34,197,94,0.3)' : 'transparent'}`,
              transition: 'all 150ms ease',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
            } as React.CSSProperties}
          >
            {selected ? <><CheckCircle size={14} /> Selected</> : <><Star size={14} /> Select Idea</>}
          </button>
          <button
            onClick={() => setExpanded((v) => !v)}
            style={{
              padding: '10px 16px', borderRadius: '8px', fontSize: '13px', cursor: 'pointer',
              border: '1px solid rgba(255,255,255,0.08)', background: 'transparent', color: 'rgba(255,255,255,0.5)',
              display: 'flex', alignItems: 'center', gap: '6px', transition: 'all 150ms ease',
            }}
          >
            Details {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
        </div>
      </div>

      {/* Expanded Detail */}
      {expanded && (
        <div
          style={{
            borderTop: '1px solid rgba(255,255,255,0.06)',
            padding: '20px 24px',
            animation: 'slide-up 200ms ease-out',
          }}
        >
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '16px' }}>
            <div>
              <p style={{ fontSize: '12px', fontWeight: 600, color: '#22C55E', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Strengths</p>
              {idea.strengths.map((s, i) => (
                <p key={i} style={{ fontSize: '13px', color: 'rgba(255,255,255,0.5)', marginBottom: '4px' }}>• {s}</p>
              ))}
            </div>
            <div>
              <p style={{ fontSize: '12px', fontWeight: 600, color: '#EF4444', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Weaknesses</p>
              {idea.weaknesses.map((w, i) => (
                <p key={i} style={{ fontSize: '13px', color: 'rgba(255,255,255,0.5)', marginBottom: '4px' }}>• {w}</p>
              ))}
            </div>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {idea.apis.map((api) => (
              <span key={api} style={{ padding: '4px 10px', borderRadius: '6px', fontSize: '12px', background: 'rgba(59,130,246,0.1)', color: '#3B82F6', border: '1px solid rgba(59,130,246,0.2)' }}>{api}</span>
            ))}
            {idea.competitors.map((c) => (
              <span key={c} style={{ padding: '4px 10px', borderRadius: '6px', fontSize: '12px', background: 'rgba(245,158,11,0.1)', color: '#F59E0B', border: '1px solid rgba(245,158,11,0.2)' }}>{c}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function IdeasPage({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = use(params);
  const router = useRouter();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [confirming, setConfirming] = useState(false);
  const ideas = DEMO_FINANCE_PROJECT.ideas;

  const handleContinue = async () => {
    setConfirming(true);
    await new Promise((r) => setTimeout(r, 1200));
    router.push(`/dashboard/${projectId}`);
  };

  return (
    <div style={{ background: '#050816', minHeight: '100vh', color: '#F1F5F9' }}>
      <Navbar />
      <div style={{ paddingTop: '80px' }}>
        {/* Header */}
        <div
          style={{
            borderBottom: '1px solid rgba(255,255,255,0.06)',
            padding: '28px 32px',
            background: 'rgba(255,255,255,0.01)',
          }}
        >
          <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.35)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '8px' }}>Step 5 of 10 — Idea Selection</p>
                <h1 style={{ fontSize: '28px', fontWeight: 700, letterSpacing: '-0.02em', marginBottom: '8px' }}>Choose Your Winning Idea</h1>
                <p style={{ fontSize: '15px', color: 'rgba(255,255,255,0.45)' }}>
                  5 ideas generated. Ranked by innovation, feasibility, and differentiation.
                </p>
              </div>

              {selectedId && (
                <button
                  onClick={handleContinue}
                  disabled={confirming}
                  style={{
                    display: 'flex', alignItems: 'center', gap: '10px',
                    padding: '14px 28px', borderRadius: '10px', fontSize: '15px', fontWeight: 700, cursor: confirming ? 'default' : 'pointer',
                    border: 'none',
                    background: confirming ? 'rgba(124,58,237,0.4)' : 'linear-gradient(135deg, #7C3AED, #22C55E)',
                    color: '#fff',
                    boxShadow: confirming ? 'none' : '0 0 30px rgba(124,58,237,0.4)',
                    transition: 'all 150ms ease',
                  }}
                >
                  {confirming ? (
                    <><div style={{ width: '16px', height: '16px', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} /> Continuing...</>
                  ) : (
                    <><Zap size={16} /> Continue Workflow <ArrowRight size={16} /></>
                  )}
                </button>
              )}
            </div>

            {/* Stats Row */}
            <div style={{ display: 'flex', gap: '24px', marginTop: '20px', flexWrap: 'wrap' }}>
              {[
                { icon: <Lightbulb size={14} />, label: '5 ideas generated', color: '#EC4899' },
                { icon: <Shield size={14} />, label: 'Grounded with research', color: '#06B6D4' },
                { icon: <TrendingUp size={14} />, label: 'Scored & ranked', color: '#22C55E' },
              ].map((s, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px', color: s.color, fontSize: '13px' }}>
                  {s.icon} {s.label}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Ideas Grid */}
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 32px 80px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
            {ideas.map((idea, i) => (
              <div
                key={idea.id}
                style={{ animation: `slide-up 300ms ease-out ${i * 80}ms both` }}
              >
                <IdeaCard
                  idea={idea}
                  selected={selectedId === idea.id}
                  dimmed={selectedId !== null && selectedId !== idea.id}
                  onSelect={() => setSelectedId(selectedId === idea.id ? null : idea.id)}
                />
              </div>
            ))}
          </div>

          {!selectedId && (
            <p style={{ textAlign: 'center', color: 'rgba(255,255,255,0.25)', fontSize: '14px', marginTop: '32px' }}>
              Select an idea to continue the workflow
            </p>
          )}
        </div>
      </div>
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes slide-up { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </div>
  );
}
