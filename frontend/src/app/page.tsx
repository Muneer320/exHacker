'use client';

import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
import { ArrowRight, Play, Zap, Brain, Search, Lightbulb, CheckCircle, GitBranch, Mic, Target, ChevronRight, Layers, Star } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';

// ─── Animated Grid Background ────────────────────────────────────────────────
function GridBackground() {
  return (
    <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none' }}>
      {/* Grid */}
      <div
        style={{
          position: 'absolute', inset: 0,
          backgroundImage: 'linear-gradient(rgba(124,58,237,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(124,58,237,0.04) 1px, transparent 1px)',
          backgroundSize: '60px 60px',
        }}
      />
      {/* Radial gradient overlay */}
      <div
        style={{
          position: 'absolute', inset: 0,
          background: 'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(124,58,237,0.12) 0%, transparent 70%)',
        }}
      />
      {/* Floating orbs */}
      {[
        { x: '15%', y: '25%', color: 'rgba(124,58,237,0.15)', size: 300, delay: '0s' },
        { x: '80%', y: '60%', color: 'rgba(6,182,212,0.1)', size: 250, delay: '2s' },
        { x: '60%', y: '15%', color: 'rgba(236,72,153,0.08)', size: 200, delay: '1s' },
      ].map((orb, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: orb.x, top: orb.y,
            width: orb.size, height: orb.size,
            borderRadius: '50%',
            background: `radial-gradient(circle, ${orb.color} 0%, transparent 70%)`,
            filter: 'blur(40px)',
            animation: `float 6s ease-in-out infinite`,
            animationDelay: orb.delay,
          }}
        />
      ))}
    </div>
  );
}

// ─── Workflow Preview Node ────────────────────────────────────────────────────
const WORKFLOW_NODES = [
  { label: 'Challenge', icon: Target, color: '#06B6D4' },
  { label: 'Analysis', icon: Brain, color: '#8B5CF6' },
  { label: 'Research', icon: Search, color: '#F59E0B' },
  { label: 'Ideas', icon: Lightbulb, color: '#EC4899' },
  { label: 'Architecture', icon: GitBranch, color: '#3B82F6' },
  { label: 'Pitch', icon: Mic, color: '#F97316' },
];

function WorkflowPreview() {
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % WORKFLOW_NODES.length);
    }, 1400);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ textAlign: 'center' }}>
      <p style={{ fontSize: '12px', fontWeight: 600, letterSpacing: '0.12em', color: 'rgba(255,255,255,0.3)', marginBottom: '32px', textTransform: 'uppercase' }}>
        AI Workflow
      </p>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0',
          flexWrap: 'wrap',
          rowGap: '16px',
        }}
      >
        {WORKFLOW_NODES.map((node, i) => {
          const Icon = node.icon;
          const isActive = i === activeIndex;
          const isDone = i < activeIndex;
          return (
            <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '8px',
                  position: 'relative',
                }}
              >
                <div
                  style={{
                    width: '56px',
                    height: '56px',
                    borderRadius: '16px',
                    background: isActive
                      ? `rgba(${hexToRgb(node.color)}, 0.2)`
                      : isDone
                      ? 'rgba(34,197,94,0.1)'
                      : 'rgba(255,255,255,0.04)',
                    border: `1px solid ${isActive ? node.color : isDone ? 'rgba(34,197,94,0.4)' : 'rgba(255,255,255,0.08)'}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 400ms cubic-bezier(0.16,1,0.3,1)',
                    boxShadow: isActive ? `0 0 20px ${node.color}40, 0 0 60px ${node.color}15` : 'none',
                    transform: isActive ? 'scale(1.08)' : 'scale(1)',
                  }}
                >
                  <Icon size={22} color={isActive ? node.color : isDone ? '#22C55E' : 'rgba(255,255,255,0.3)'} />
                </div>
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 500,
                    color: isActive ? node.color : isDone ? '#22C55E' : 'rgba(255,255,255,0.3)',
                    transition: 'color 400ms ease',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {node.label}
                </span>
              </div>
              {i < WORKFLOW_NODES.length - 1 && (
                <div
                  style={{
                    width: '48px',
                    height: '1px',
                    margin: '0 4px',
                    background: isDone ? '#22C55E' : 'rgba(255,255,255,0.08)',
                    transition: 'background 400ms ease',
                    position: 'relative',
                    top: '-12px',
                  }}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function hexToRgb(hex: string) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `${r},${g},${b}`;
}

// ─── Feature Card ─────────────────────────────────────────────────────────────
function FeatureCard({ icon, title, description, color }: { icon: React.ReactNode; title: string; description: string; color: string }) {
  const [hovered, setHovered] = useState(false);
  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        background: '#0B1020',
        borderRadius: '16px',
        border: `1px solid ${hovered ? 'rgba(255,255,255,0.15)' : 'rgba(255,255,255,0.06)'}`,
        padding: '32px',
        transition: 'all 250ms cubic-bezier(0.16,1,0.3,1)',
        transform: hovered ? 'translateY(-4px)' : 'translateY(0)',
        cursor: 'default',
      }}
    >
      <div
        style={{
          width: '48px',
          height: '48px',
          borderRadius: '12px',
          background: `rgba(${hexToRgb(color)}, 0.12)`,
          border: `1px solid rgba(${hexToRgb(color)}, 0.25)`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '20px',
          color,
          transition: 'all 250ms ease',
          boxShadow: hovered ? `0 0 20px rgba(${hexToRgb(color)}, 0.2)` : 'none',
        }}
      >
        {icon}
      </div>
      <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#F1F5F9', marginBottom: '10px' }}>{title}</h3>
      <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.5)', lineHeight: 1.7 }}>{description}</p>
    </div>
  );
}

// ─── Stats Bar ────────────────────────────────────────────────────────────────
function StatsBar() {
  const stats = [
    { value: '10', label: 'AI Agents' },
    { value: '50+', label: 'Research Sources' },
    { value: '7', label: 'Deliverables' },
    { value: '<5min', label: 'To Full Package' },
  ];
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '0',
        flexWrap: 'wrap',
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: '16px',
        overflow: 'hidden',
      }}
    >
      {stats.map((s, i) => (
        <div
          key={i}
          style={{
            flex: '1 1 160px',
            padding: '24px 32px',
            textAlign: 'center',
            borderRight: i < stats.length - 1 ? '1px solid rgba(255,255,255,0.06)' : 'none',
          }}
        >
          <div
            style={{
              fontSize: '32px',
              fontWeight: 800,
              background: 'linear-gradient(135deg, #A855F7, #06B6D4)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              marginBottom: '4px',
            }}
          >
            {s.value}
          </div>
          <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)', fontWeight: 500 }}>{s.label}</div>
        </div>
      ))}
    </div>
  );
}

// ─── Main Landing Page ────────────────────────────────────────────────────────
export default function LandingPage() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <div style={{ background: '#050816', minHeight: '100vh', color: '#F1F5F9' }}>
      <Navbar />

      {/* Hero Section */}
      <section
        style={{
          position: 'relative',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '120px 32px 80px',
          textAlign: 'center',
          overflow: 'hidden',
        }}
      >
        <GridBackground />

        <div style={{ position: 'relative', zIndex: 1, maxWidth: '900px' }}>
          {/* Badge */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 16px',
              borderRadius: '99px',
              background: 'rgba(124,58,237,0.1)',
              border: '1px solid rgba(124,58,237,0.25)',
              fontSize: '13px',
              color: '#A855F7',
              fontWeight: 500,
              marginBottom: '32px',
              opacity: mounted ? 1 : 0,
              transform: mounted ? 'translateY(0)' : 'translateY(10px)',
              transition: 'all 400ms cubic-bezier(0.16,1,0.3,1)',
            }}
          >
            <Star size={12} fill="#A855F7" />
            AI-Powered Hackathon Intelligence Platform
          </div>

          {/* Headline */}
          <h1
            style={{
              fontSize: 'clamp(48px, 8vw, 80px)',
              fontWeight: 800,
              lineHeight: 1.05,
              letterSpacing: '-0.03em',
              marginBottom: '24px',
              opacity: mounted ? 1 : 0,
              transform: mounted ? 'translateY(0)' : 'translateY(20px)',
              transition: 'all 400ms cubic-bezier(0.16,1,0.3,1)',
            }}
          >
            Build Better Hackathon
            <br />
            <span
              style={{
                background: 'linear-gradient(135deg, #7C3AED 0%, #A855F7 40%, #06B6D4 70%, #22C55E 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              Projects. In Minutes.
            </span>
          </h1>

          {/* Subheadline */}
          <p
            style={{
              fontSize: '18px',
              color: 'rgba(255,255,255,0.55)',
              lineHeight: 1.7,
              maxWidth: '600px',
              margin: '0 auto 40px',
              opacity: mounted ? 1 : 0,
              transform: mounted ? 'translateY(0)' : 'translateY(20px)',
              transition: 'all 400ms cubic-bezier(0.16,1,0.3,1) 100ms',
            }}
          >
            Challenge → Ideas → Validation → Architecture → Pitch → Presentation
            <br />
            <span style={{ fontSize: '15px', color: 'rgba(255,255,255,0.35)' }}>
              10 specialized AI agents. One winning project package.
            </span>
          </p>

          {/* CTAs */}
          <div
            style={{
              display: 'flex',
              gap: '16px',
              justifyContent: 'center',
              flexWrap: 'wrap',
              opacity: mounted ? 1 : 0,
              transform: mounted ? 'translateY(0)' : 'translateY(20px)',
              transition: 'all 400ms cubic-bezier(0.16,1,0.3,1) 200ms',
            }}
          >
            <Link
              href="/new-project"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '14px 32px',
                borderRadius: '10px',
                background: '#7C3AED',
                color: '#fff',
                fontWeight: 600,
                fontSize: '16px',
                textDecoration: 'none',
                transition: 'all 150ms ease-out',
                boxShadow: '0 0 30px rgba(124,58,237,0.4)',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.filter = 'brightness(1.15)'; e.currentTarget.style.transform = 'scale(1.02)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.filter = 'none'; e.currentTarget.style.transform = 'scale(1)'; }}
            >
              Start Building
              <ArrowRight size={18} />
            </Link>
            <Link
              href="/demo"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '14px 32px',
                borderRadius: '10px',
                background: 'transparent',
                color: 'rgba(255,255,255,0.8)',
                fontWeight: 600,
                fontSize: '16px',
                textDecoration: 'none',
                border: '1px solid rgba(255,255,255,0.15)',
                transition: 'all 150ms ease-out',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.25)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.15)'; }}
            >
              <Play size={16} />
              Watch Demo
            </Link>
          </div>
        </div>

        {/* Scroll Hint */}
        <div
          style={{
            position: 'absolute',
            bottom: '32px',
            left: '50%',
            transform: 'translateX(-50%)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '8px',
            color: 'rgba(255,255,255,0.2)',
            fontSize: '12px',
          }}
        >
          <ChevronRight size={16} style={{ transform: 'rotate(90deg)' }} />
        </div>
      </section>

      {/* Workflow Preview Section */}
      <section style={{ padding: '80px 32px', maxWidth: '1200px', margin: '0 auto' }}>
        <div
          style={{
            background: '#0B1020',
            borderRadius: '24px',
            border: '1px solid rgba(255,255,255,0.06)',
            padding: '60px 40px',
          }}
        >
          <WorkflowPreview />
        </div>
      </section>

      {/* Stats */}
      <section style={{ padding: '0 32px 80px', maxWidth: '1200px', margin: '0 auto' }}>
        <StatsBar />
      </section>

      {/* Features Section */}
      <section style={{ padding: '80px 32px', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '56px' }}>
          <h2
            style={{
              fontSize: 'clamp(28px, 4vw, 40px)',
              fontWeight: 700,
              letterSpacing: '-0.02em',
              marginBottom: '16px',
            }}
          >
            Everything you need to win
          </h2>
          <p style={{ fontSize: '16px', color: 'rgba(255,255,255,0.45)', maxWidth: '480px', margin: '0 auto' }}>
            A complete AI team built specifically for hackathon success.
          </p>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '24px',
          }}
        >
          <FeatureCard
            color="#7C3AED"
            icon={<Layers size={22} />}
            title="AI Team of 10 Agents"
            description="Challenge Intelligence, Problem Analyst, Opportunity Planner, Idea Generator, Validator, Architect, Build Accelerator, Presentation Agent, Pitch Coach — all working in sync."
          />
          <FeatureCard
            color="#06B6D4"
            icon={<Search size={22} />}
            title="Grounded Research Engine"
            description="Automatically discovers competitors, relevant APIs, and open source projects using Tavily search. Real data, not hallucinations."
          />
          <FeatureCard
            color="#22C55E"
            icon={<Zap size={22} />}
            title="Complete Build Package"
            description="Architecture diagrams, tech stack recommendations, build roadmap, presentation slides, pitch scripts, and judge Q&A prep. Ship-ready in minutes."
          />
        </div>
      </section>

      {/* Agent Showcase */}
      <section style={{ padding: '80px 32px', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <h2 style={{ fontSize: 'clamp(24px, 3vw, 36px)', fontWeight: 700, letterSpacing: '-0.02em', marginBottom: '12px' }}>
            Meet your AI team
          </h2>
          <p style={{ fontSize: '15px', color: 'rgba(255,255,255,0.4)' }}>10 specialized agents, each an expert in their domain</p>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
          {[
            { name: 'Challenge Intelligence', color: '#06B6D4', icon: Target },
            { name: 'Problem Analyst', color: '#8B5CF6', icon: Brain },
            { name: 'Opportunity Planner', color: '#F59E0B', icon: Search },
            { name: 'Idea Generator', color: '#EC4899', icon: Lightbulb },
            { name: 'Idea Validator', color: '#22C55E', icon: CheckCircle },
            { name: 'Tech Stack Advisor', color: '#3B82F6', icon: Layers },
            { name: 'Solution Architect', color: '#3B82F6', icon: GitBranch },
            { name: 'Build Accelerator', color: '#22C55E', icon: Zap },
            { name: 'Presentation Agent', color: '#A855F7', icon: Star },
            { name: 'Pitch Coach', color: '#F97316', icon: Mic },
          ].map((agent, i) => {
            const Icon = agent.icon;
            return (
              <div
                key={i}
                style={{
                  padding: '16px',
                  borderRadius: '12px',
                  background: '#0B1020',
                  border: '1px solid rgba(255,255,255,0.06)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  transition: 'border-color 250ms ease',
                }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.borderColor = `${agent.color}40`; }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.borderColor = 'rgba(255,255,255,0.06)'; }}
              >
                <div
                  style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '10px',
                    background: `rgba(${hexToRgb(agent.color)}, 0.12)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    color: agent.color,
                  }}
                >
                  <Icon size={16} />
                </div>
                <span style={{ fontSize: '13px', fontWeight: 500, color: 'rgba(255,255,255,0.7)' }}>{agent.name}</span>
              </div>
            );
          })}
        </div>
      </section>

      {/* Final CTA */}
      <section
        style={{
          padding: '100px 32px',
          textAlign: 'center',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'radial-gradient(ellipse 60% 80% at 50% 50%, rgba(124,58,237,0.08) 0%, transparent 70%)',
          }}
        />
        <div style={{ position: 'relative', maxWidth: '600px', margin: '0 auto' }}>
          <h2
            style={{
              fontSize: 'clamp(32px, 5vw, 52px)',
              fontWeight: 800,
              letterSpacing: '-0.03em',
              marginBottom: '20px',
              lineHeight: 1.1,
            }}
          >
            Ready to win your
            <br />
            <span
              style={{
                background: 'linear-gradient(135deg, #7C3AED, #06B6D4)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              next hackathon?
            </span>
          </h2>
          <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: '16px', marginBottom: '40px' }}>
            Start a project in seconds. Let 10 AI agents do the heavy lifting.
          </p>
          <Link
            href="/new-project"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '10px',
              padding: '16px 40px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #7C3AED, #A855F7)',
              color: '#fff',
              fontWeight: 700,
              fontSize: '18px',
              textDecoration: 'none',
              boxShadow: '0 0 40px rgba(124,58,237,0.4)',
              transition: 'all 150ms ease-out',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.03)'; e.currentTarget.style.boxShadow = '0 0 60px rgba(124,58,237,0.6)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.boxShadow = '0 0 40px rgba(124,58,237,0.4)'; }}
          >
            Launch AI Team
            <ArrowRight size={20} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer
        style={{
          borderTop: '1px solid rgba(255,255,255,0.06)',
          padding: '32px',
          textAlign: 'center',
          color: 'rgba(255,255,255,0.25)',
          fontSize: '13px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}>
          <Zap size={14} color="#7C3AED" />
          <span>exHacker — AI Hackathon Intelligence Platform</span>
        </div>
      </footer>
    </div>
  );
}
