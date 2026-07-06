'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Zap, Sparkles, GitBranch, Download } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import { createProject } from '@/services/api';

const STEPS = [
  { label: 'Idea', icon: Sparkles, color: 'var(--color-accent-500)' },
  { label: 'Research', icon: Zap, color: 'var(--color-info)' },
  { label: 'Architecture', icon: GitBranch, color: 'var(--color-accent-400)' },
  { label: 'Export', icon: Download, color: 'var(--color-success)' },
];

const EXAMPLES = [
  'A mobile app that helps students budget their money using AI',
  'A habit tracker that uses spaced repetition to build routines',
  'A platform for indie hackers to find beta testers',
];

export default function LandingPage() {
  const router = useRouter();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    setLoading(true);
    setError(null);

    try {
      const res = await createProject({ idea: input.trim() });
      if (res.success) {
        router.push('/projects');
      } else {
        setError(res.error?.message || 'Failed to create project.');
      }
    } catch {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ background: 'var(--color-app-bg)', minHeight: '100vh', color: 'var(--color-text-primary)' }}>
      <Navbar />

      {/* Hero */}
      <section
        style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '120px 24px 80px',
          textAlign: 'center',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Background grid */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            pointerEvents: 'none',
            backgroundImage:
              'linear-gradient(rgba(124,58,237,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(124,58,237,0.03) 1px, transparent 1px)',
            backgroundSize: '60px 60px',
          }}
        />
        <div
          style={{
            position: 'absolute',
            inset: 0,
            pointerEvents: 'none',
            background:
              'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(124,58,237,0.1) 0%, transparent 70%)',
          }}
        />

        <div style={{ position: 'relative', zIndex: 1, maxWidth: '720px' }}>
          {/* Badge */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '4px 12px',
              borderRadius: '99px',
              background: 'rgba(124,58,237,0.1)',
              border: '1px solid rgba(124,58,237,0.2)',
              fontSize: '12px',
              color: 'var(--color-accent-400)',
              fontWeight: 500,
              marginBottom: '24px',
            }}
          >
            <Zap size={12} />
            AI Product Studio
          </div>

          {/* Headline */}
          <h1
            style={{
              fontSize: 'clamp(36px, 6vw, 56px)',
              fontWeight: 800,
              lineHeight: 1.1,
              letterSpacing: '-0.03em',
              marginBottom: '16px',
            }}
          >
            Your idea deserves a
            <br />
            <span
              style={{
                background: 'linear-gradient(135deg, var(--color-accent-500), var(--color-info))',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              real plan.
            </span>
          </h1>

          <p
            style={{
              fontSize: '16px',
              color: 'var(--color-text-secondary)',
              lineHeight: 1.6,
              maxWidth: '480px',
              margin: '0 auto 32px',
            }}
          >
            Turn your idea into a validated, architecturally sound project blueprint —
            complete with competitor research, system design, and an execution plan.
          </p>

          {/* Input */}
          <form onSubmit={handleSubmit} style={{ marginBottom: '16px' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                background: 'var(--color-surface-1)',
                border: `1px solid ${error ? 'var(--color-error)' : 'var(--color-border-default)'}`,
                borderRadius: '12px',
                transition: 'border-color 200ms ease',
                overflow: 'hidden',
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = 'var(--color-border-focus)';
              }}
              onBlur={(e) => {
                if (!error) {
                  e.currentTarget.style.borderColor = 'var(--color-border-default)';
                }
              }}
            >
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="What do you want to build?"
                disabled={loading}
                style={{
                  flex: 1,
                  background: 'transparent',
                  border: 'none',
                  padding: '16px 20px',
                  fontSize: '16px',
                  color: 'var(--color-text-primary)',
                  outline: 'none',
                  fontFamily: 'Inter, sans-serif',
                }}
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '10px 20px',
                  margin: '6px',
                  borderRadius: '8px',
                  border: 'none',
                  background:
                    !input.trim() || loading
                      ? 'rgba(124,58,237,0.3)'
                      : 'var(--color-accent-500)',
                  color: '#fff',
                  fontSize: '14px',
                  fontWeight: 600,
                  cursor: !input.trim() || loading ? 'default' : 'pointer',
                  transition: 'all 150ms ease',
                  whiteSpace: 'nowrap',
                }}
              >
                {loading ? (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span
                      style={{
                        width: '14px',
                        height: '14px',
                        borderRadius: '50%',
                        border: '2px solid rgba(255,255,255,0.3)',
                        borderTopColor: '#fff',
                        animation: 'spin 0.8s linear infinite',
                        display: 'inline-block',
                      }}
                    />
                    Planning...
                  </span>
                ) : (
                  <>
                    Start <ArrowRight size={16} />
                  </>
                )}
              </button>
            </div>
          </form>

          {error && (
            <p style={{ fontSize: '13px', color: 'var(--color-error)', marginBottom: '16px' }}>
              {error}
            </p>
          )}

          {/* Examples */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '8px',
              justifyContent: 'center',
              marginBottom: '48px',
            }}
          >
            <span style={{ fontSize: '13px', color: 'var(--color-text-tertiary)', marginRight: '4px' }}>
              Try:
            </span>
            {EXAMPLES.map((example) => (
              <button
                key={example}
                onClick={() => setInput(example)}
                style={{
                  padding: '6px 12px',
                  borderRadius: '8px',
                  fontSize: '12px',
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid var(--color-border-default)',
                  color: 'var(--color-text-secondary)',
                  cursor: 'pointer',
                  transition: 'all 150ms ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(124,58,237,0.08)';
                  e.currentTarget.style.borderColor = 'rgba(124,58,237,0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255,255,255,0.04)';
                  e.currentTarget.style.borderColor = 'var(--color-border-default)';
                }}
              >
                {example.length > 50 ? example.slice(0, 50) + '...' : example}
              </button>
            ))}
          </div>

          {/* Steps */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0',
            }}
          >
            {STEPS.map((step, i) => {
              const Icon = step.icon;
              return (
                <div
                  key={step.label}
                  style={{ display: 'flex', alignItems: 'center' }}
                >
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px' }}>
                    <div
                      style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '10px',
                        background: 'rgba(255,255,255,0.04)',
                        border: '1px solid var(--color-border-default)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: step.color,
                      }}
                    >
                      <Icon size={16} />
                    </div>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-tertiary)' }}>
                      {step.label}
                    </span>
                  </div>
                  {i < STEPS.length - 1 && (
                    <div
                      style={{
                        width: '32px',
                        height: '1px',
                        background: 'var(--color-border-default)',
                        margin: '0 4px',
                        marginBottom: '24px',
                      }}
                    />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </div>
  );
}
