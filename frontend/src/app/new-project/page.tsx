'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, ArrowLeft, Check, Zap, Users, Clock, Code, BookOpen, Trophy } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';

const STEPS = ['Challenge', 'Team', 'Constraints', 'Review'];

const THEMES = ['FinTech', 'HealthTech', 'EdTech', 'ClimaTech', 'LegalTech', 'AgriTech', 'GovTech', 'Open Innovation'];
const SKILLS = ['React', 'Vue', 'Angular', 'Next.js', 'Python', 'Node.js', 'FastAPI', 'Django', 'ML/AI', 'DevOps', 'Design', 'Mobile'];
const DURATIONS = ['24 hours', '36 hours', '48 hours', '72 hours', '1 week'];
const TECH_OPTIONS = ['Next.js', 'React', 'Vue', 'FastAPI', 'Django', 'Node.js', 'PostgreSQL', 'MongoDB', 'Redis', 'Docker', 'AWS', 'OpenAI', 'LangChain', 'Supabase'];

function StepIndicator({ currentStep }: { currentStep: number }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0', marginBottom: '56px' }}>
      {STEPS.map((step, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '14px',
                fontWeight: 600,
                transition: 'all 300ms ease',
                background: i < currentStep ? '#22C55E' : i === currentStep ? '#7C3AED' : 'rgba(255,255,255,0.06)',
                color: i <= currentStep ? '#fff' : 'rgba(255,255,255,0.3)',
                border: i === currentStep ? '2px solid rgba(124,58,237,0.5)' : 'none',
                boxShadow: i === currentStep ? '0 0 20px rgba(124,58,237,0.4)' : 'none',
              }}
            >
              {i < currentStep ? <Check size={16} /> : i + 1}
            </div>
            <span style={{ fontSize: '12px', color: i === currentStep ? '#A855F7' : 'rgba(255,255,255,0.3)', fontWeight: i === currentStep ? 600 : 400 }}>{step}</span>
          </div>
          {i < STEPS.length - 1 && (
            <div
              style={{
                width: '80px',
                height: '1px',
                background: i < currentStep ? '#22C55E' : 'rgba(255,255,255,0.08)',
                margin: '0 8px',
                marginBottom: '24px',
                transition: 'background 300ms ease',
              }}
            />
          )}
        </div>
      ))}
    </div>
  );
}

interface FormData {
  challenge: string;
  theme: string;
  rules: string;
  teamSize: number;
  skills: string[];
  experience: string;
  duration: string;
  availableTools: string;
  preferredTech: string[];
}

export default function NewProjectPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState<FormData>({
    challenge: '',
    theme: '',
    rules: '',
    teamSize: 3,
    skills: [],
    experience: 'Intermediate',
    duration: '48 hours',
    availableTools: 'Any',
    preferredTech: [],
  });

  const toggleSkill = (s: string) => setForm((f) => ({ ...f, skills: f.skills.includes(s) ? f.skills.filter((x) => x !== s) : [...f.skills, s] }));
  const toggleTech = (t: string) => setForm((f) => ({ ...f, preferredTech: f.preferredTech.includes(t) ? f.preferredTech.filter((x) => x !== t) : [...f.preferredTech, t] }));

  const handleLaunch = async () => {
    setLoading(true);
    await new Promise((r) => setTimeout(r, 1800));
    router.push('/workflow/demo-finance-001');
  };

  const canNext = () => {
    if (step === 0) return form.challenge.length > 20;
    if (step === 1) return form.teamSize > 0;
    return true;
  };

  return (
    <div style={{ background: '#050816', minHeight: '100vh', color: '#F1F5F9' }}>
      <Navbar />
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'center',
          padding: '100px 32px 60px',
        }}
      >
        <div style={{ width: '100%', maxWidth: '680px' }}>
          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: '48px' }}>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '5px 14px',
                borderRadius: '99px',
                background: 'rgba(124,58,237,0.1)',
                border: '1px solid rgba(124,58,237,0.2)',
                fontSize: '12px',
                color: '#A855F7',
                marginBottom: '20px',
              }}
            >
              <Zap size={12} />
              Launch Your AI Team
            </div>
            <h1 style={{ fontSize: '36px', fontWeight: 700, letterSpacing: '-0.02em', marginBottom: '12px' }}>
              Tell us about your challenge
            </h1>
            <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: '15px' }}>
              Our AI agents will do the rest. This takes less than 2 minutes.
            </p>
          </div>

          <StepIndicator currentStep={step} />

          {/* Step Cards */}
          <div
            style={{
              background: '#0B1020',
              borderRadius: '20px',
              border: '1px solid rgba(255,255,255,0.08)',
              padding: '40px',
              marginBottom: '24px',
            }}
          >
            {/* ── Step 0: Challenge ── */}
            {step === 0 && (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(6,182,212,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#06B6D4' }}>
                    <Trophy size={18} />
                  </div>
                  <div>
                    <h2 style={{ fontSize: '20px', fontWeight: 600 }}>Hackathon Challenge</h2>
                    <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>Tell us what you're building for</p>
                  </div>
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: 'rgba(255,255,255,0.6)', marginBottom: '8px' }}>
                    Problem Statement *
                  </label>
                  <textarea
                    value={form.challenge}
                    onChange={(e) => setForm((f) => ({ ...f, challenge: e.target.value }))}
                    placeholder="Describe the hackathon challenge or problem you want to solve..."
                    rows={4}
                    style={{
                      width: '100%',
                      background: '#111827',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '10px',
                      padding: '14px 16px',
                      color: '#F1F5F9',
                      fontSize: '15px',
                      resize: 'vertical',
                      outline: 'none',
                      fontFamily: 'Inter, sans-serif',
                      lineHeight: 1.6,
                    }}
                    onFocus={(e) => { e.target.style.borderColor = 'rgba(124,58,237,0.5)'; }}
                    onBlur={(e) => { e.target.style.borderColor = 'rgba(255,255,255,0.1)'; }}
                  />
                  <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.25)', marginTop: '6px', textAlign: 'right' }}>
                    {form.challenge.length} characters {form.challenge.length < 20 && '(min 20)'}
                  </div>
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: 'rgba(255,255,255,0.6)', marginBottom: '10px' }}>
                    Theme / Track
                  </label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {THEMES.map((t) => (
                      <button
                        key={t}
                        onClick={() => setForm((f) => ({ ...f, theme: t }))}
                        style={{
                          padding: '7px 14px',
                          borderRadius: '8px',
                          fontSize: '13px',
                          cursor: 'pointer',
                          border: `1px solid ${form.theme === t ? 'rgba(124,58,237,0.6)' : 'rgba(255,255,255,0.08)'}`,
                          background: form.theme === t ? 'rgba(124,58,237,0.15)' : 'transparent',
                          color: form.theme === t ? '#A855F7' : 'rgba(255,255,255,0.5)',
                          transition: 'all 150ms ease',
                        }}
                      >
                        {t}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: 'rgba(255,255,255,0.6)', marginBottom: '8px' }}>
                    Rules & Constraints (optional)
                  </label>
                  <textarea
                    value={form.rules}
                    onChange={(e) => setForm((f) => ({ ...f, rules: e.target.value }))}
                    placeholder="e.g. Must use open source stack, mobile-first, include AI component..."
                    rows={2}
                    style={{
                      width: '100%',
                      background: '#111827',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '10px',
                      padding: '12px 16px',
                      color: '#F1F5F9',
                      fontSize: '14px',
                      resize: 'none',
                      outline: 'none',
                      fontFamily: 'Inter, sans-serif',
                    }}
                    onFocus={(e) => { e.target.style.borderColor = 'rgba(124,58,237,0.5)'; }}
                    onBlur={(e) => { e.target.style.borderColor = 'rgba(255,255,255,0.1)'; }}
                  />
                </div>
              </div>
            )}

            {/* ── Step 1: Team ── */}
            {step === 1 && (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(139,92,246,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8B5CF6' }}>
                    <Users size={18} />
                  </div>
                  <div>
                    <h2 style={{ fontSize: '20px', fontWeight: 600 }}>Your Team</h2>
                    <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>Help us tailor solutions to your capabilities</p>
                  </div>
                </div>

                <div style={{ marginBottom: '24px' }}>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: 'rgba(255,255,255,0.6)', marginBottom: '12px' }}>
                    Team Size: <span style={{ color: '#A855F7', fontWeight: 700 }}>{form.teamSize} people</span>
                  </label>
                  <input
                    type="range" min={1} max={8} value={form.teamSize}
                    onChange={(e) => setForm((f) => ({ ...f, teamSize: Number(e.target.value) }))}
                    style={{ width: '100%', accentColor: '#7C3AED' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'rgba(255,255,255,0.3)', marginTop: '4px' }}>
                    <span>Solo</span><span>8 People</span>
                  </div>
                </div>

                <div style={{ marginBottom: '24px' }}>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: 'rgba(255,255,255,0.6)', marginBottom: '10px' }}>
                    Team Skills
                  </label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {SKILLS.map((s) => (
                      <button
                        key={s}
                        onClick={() => toggleSkill(s)}
                        style={{
                          padding: '7px 14px', borderRadius: '8px', fontSize: '13px', cursor: 'pointer',
                          border: `1px solid ${form.skills.includes(s) ? 'rgba(139,92,246,0.6)' : 'rgba(255,255,255,0.08)'}`,
                          background: form.skills.includes(s) ? 'rgba(139,92,246,0.15)' : 'transparent',
                          color: form.skills.includes(s) ? '#8B5CF6' : 'rgba(255,255,255,0.5)',
                          transition: 'all 150ms ease',
                        }}
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: 'rgba(255,255,255,0.6)', marginBottom: '10px' }}>
                    Experience Level
                  </label>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    {['Beginner', 'Intermediate', 'Advanced'].map((level) => (
                      <button
                        key={level}
                        onClick={() => setForm((f) => ({ ...f, experience: level }))}
                        style={{
                          flex: 1, padding: '12px', borderRadius: '10px', fontSize: '14px', cursor: 'pointer', fontWeight: 500,
                          border: `1px solid ${form.experience === level ? 'rgba(124,58,237,0.6)' : 'rgba(255,255,255,0.08)'}`,
                          background: form.experience === level ? 'rgba(124,58,237,0.15)' : 'transparent',
                          color: form.experience === level ? '#A855F7' : 'rgba(255,255,255,0.5)',
                          transition: 'all 150ms ease',
                        }}
                      >
                        {level}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ── Step 2: Constraints ── */}
            {step === 2 && (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(245,158,11,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#F59E0B' }}>
                    <Clock size={18} />
                  </div>
                  <div>
                    <h2 style={{ fontSize: '20px', fontWeight: 600 }}>Constraints & Tools</h2>
                    <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>We'll optimize the build plan accordingly</p>
                  </div>
                </div>

                <div style={{ marginBottom: '24px' }}>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: 'rgba(255,255,255,0.6)', marginBottom: '10px' }}>
                    Hackathon Duration
                  </label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {DURATIONS.map((d) => (
                      <button
                        key={d}
                        onClick={() => setForm((f) => ({ ...f, duration: d }))}
                        style={{
                          padding: '8px 18px', borderRadius: '8px', fontSize: '14px', cursor: 'pointer', fontWeight: 500,
                          border: `1px solid ${form.duration === d ? 'rgba(245,158,11,0.6)' : 'rgba(255,255,255,0.08)'}`,
                          background: form.duration === d ? 'rgba(245,158,11,0.12)' : 'transparent',
                          color: form.duration === d ? '#F59E0B' : 'rgba(255,255,255,0.5)',
                          transition: 'all 150ms ease',
                        }}
                      >
                        {d}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: 'rgba(255,255,255,0.6)', marginBottom: '10px' }}>
                    Preferred Technologies
                  </label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {TECH_OPTIONS.map((t) => (
                      <button
                        key={t}
                        onClick={() => toggleTech(t)}
                        style={{
                          padding: '7px 14px', borderRadius: '8px', fontSize: '13px', cursor: 'pointer',
                          border: `1px solid ${form.preferredTech.includes(t) ? 'rgba(59,130,246,0.6)' : 'rgba(255,255,255,0.08)'}`,
                          background: form.preferredTech.includes(t) ? 'rgba(59,130,246,0.15)' : 'transparent',
                          color: form.preferredTech.includes(t) ? '#3B82F6' : 'rgba(255,255,255,0.5)',
                          transition: 'all 150ms ease',
                        }}
                      >
                        {t}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ── Step 3: Review ── */}
            {step === 3 && (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(34,197,94,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#22C55E' }}>
                    <BookOpen size={18} />
                  </div>
                  <div>
                    <h2 style={{ fontSize: '20px', fontWeight: 600 }}>Review & Launch</h2>
                    <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>Confirm your project details</p>
                  </div>
                </div>

                {[
                  { label: 'Challenge', value: form.challenge || 'Not provided' },
                  { label: 'Theme', value: form.theme || 'Not specified' },
                  { label: 'Team Size', value: `${form.teamSize} people` },
                  { label: 'Experience', value: form.experience },
                  { label: 'Duration', value: form.duration },
                  { label: 'Skills', value: form.skills.length ? form.skills.join(', ') : 'Not specified' },
                  { label: 'Tech', value: form.preferredTech.length ? form.preferredTech.join(', ') : 'Any' },
                ].map((row) => (
                  <div
                    key={row.label}
                    style={{
                      display: 'flex',
                      gap: '12px',
                      padding: '14px 0',
                      borderBottom: '1px solid rgba(255,255,255,0.06)',
                    }}
                  >
                    <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)', minWidth: '100px', flexShrink: 0 }}>{row.label}</span>
                    <span style={{ fontSize: '14px', color: '#F1F5F9', lineHeight: 1.5 }}>{row.value}</span>
                  </div>
                ))}

                <div
                  style={{
                    marginTop: '24px',
                    padding: '16px',
                    borderRadius: '12px',
                    background: 'rgba(124,58,237,0.08)',
                    border: '1px solid rgba(124,58,237,0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                  }}
                >
                  <Zap size={20} color="#7C3AED" />
                  <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.6)', lineHeight: 1.5 }}>
                    10 AI agents will analyze your challenge, research competitors, generate and validate ideas, design architecture, and create your pitch — ready in under 5 minutes.
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Navigation */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              onClick={() => setStep((s) => Math.max(0, s - 1))}
              disabled={step === 0}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '12px 24px', borderRadius: '10px', fontSize: '14px', fontWeight: 500, cursor: step === 0 ? 'default' : 'pointer',
                border: '1px solid rgba(255,255,255,0.1)', background: 'transparent',
                color: step === 0 ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.7)',
              }}
            >
              <ArrowLeft size={16} /> Back
            </button>

            {step < 3 ? (
              <button
                onClick={() => setStep((s) => s + 1)}
                disabled={!canNext()}
                style={{
                  display: 'flex', alignItems: 'center', gap: '8px',
                  padding: '12px 28px', borderRadius: '10px', fontSize: '14px', fontWeight: 600, cursor: canNext() ? 'pointer' : 'default',
                  border: 'none', background: canNext() ? '#7C3AED' : 'rgba(124,58,237,0.3)',
                  color: '#fff',
                  transition: 'all 150ms ease',
                  opacity: canNext() ? 1 : 0.5,
                }}
              >
                Continue <ArrowRight size={16} />
              </button>
            ) : (
              <button
                onClick={handleLaunch}
                disabled={loading}
                style={{
                  display: 'flex', alignItems: 'center', gap: '10px',
                  padding: '14px 36px', borderRadius: '10px', fontSize: '15px', fontWeight: 700, cursor: 'pointer',
                  border: 'none',
                  background: loading ? 'rgba(34,197,94,0.3)' : 'linear-gradient(135deg, #7C3AED, #22C55E)',
                  color: '#fff',
                  boxShadow: loading ? 'none' : '0 0 30px rgba(124,58,237,0.4)',
                  transition: 'all 150ms ease',
                }}
              >
                {loading ? (
                  <>
                    <div style={{ width: '16px', height: '16px', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                    Launching AI Team...
                  </>
                ) : (
                  <>
                    <Zap size={18} />
                    Launch AI Team
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
