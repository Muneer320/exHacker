'use client';

import { use, useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
  Target, Brain, Search, Lightbulb, CheckCircle, GitBranch, Zap, Monitor, Mic,
  Star, Clock, ArrowRight, ChevronRight, Activity, Database, Sparkles, PartyPopper, HourglassIcon,
  TrendingUp, Globe, Layers, Calendar
} from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import { DEMO_FINANCE_PROJECT, WORKFLOW_STAGES } from '@/mock/data';
import { getWorkflowStatus, getWorkflowState } from '@/services/api';

// Agent icon map
const ICON_MAP: Record<string, React.ElementType> = {
  Target, Brain, Search, Lightbulb, CheckCircle, GitBranch, Zap, Monitor, Mic,
  Star, Database, Activity, Sparkles, TrendingUp, Globe, Layers, Calendar, Presentation: Monitor
};

const AGENT_COLORS: Record<string, string> = {
  challenge_intelligence: '#06B6D4',
  problem_analysis: '#8B5CF6',
  opportunity_discovery: '#F59E0B',
  idea_generation: '#EC4899',
  idea_validation: '#22C55E',
  idea_selection: '#F59E0B',
  architecture: '#3B82F6',
  build_plan: '#22C55E',
  presentation: '#A855F7',
  pitch: '#F97316',
};

const STAGE_ICONS: Record<string, React.ElementType> = {
  challenge_intelligence: Target,
  problem_analysis: Brain,
  opportunity_discovery: Search,
  idea_generation: Lightbulb,
  idea_validation: CheckCircle,
  idea_selection: Star,
  architecture: GitBranch,
  build_plan: Zap,
  presentation: Monitor,
  pitch: Mic,
};

const STAGE_TASKS: Record<string, string[]> = {
  challenge_intelligence: ['Parsing challenge statement...', 'Extracting key requirements...', 'Identifying success metrics...', 'Analyzing constraints...'],
  problem_analysis: ['Mapping stakeholders...', 'Identifying pain points...', 'Extracting opportunities...', 'Defining success criteria...'],
  opportunity_discovery: ['Searching competitors...', 'Finding relevant APIs...', 'Scanning open source...', 'Generating market insights...'],
  idea_generation: ['Brainstorming concepts...', 'Generating idea variants...', 'Scoring differentiation...', 'Finalizing 5 ideas...'],
  idea_validation: ['Validating feasibility...', 'Grounding with research...', 'Scoring innovation...', 'Ranking ideas...'],
  idea_selection: ['Awaiting your selection...'],
  architecture: ['Designing system components...', 'Creating data flow...', 'Writing Mermaid diagram...', 'Selecting tech stack...'],
  build_plan: ['Creating milestones...', 'Estimating timelines...', 'Prioritizing tasks...', 'Generating roadmap...'],
  presentation: ['Creating slide structure...', 'Writing narratives...', 'Generating content...', 'Finalizing deck...'],
  pitch: ['Writing 30-second pitch...', 'Drafting 2-minute pitch...', 'Anticipating judge Q&A...', 'Refining language...'],
};

function TimelinePanel({ stages, currentStageIndex }: { stages: typeof WORKFLOW_STAGES; currentStageIndex: number }) {
  return (
    <div
      style={{
        width: '240px',
        flexShrink: 0,
        background: '#0B1020',
        borderRadius: '16px',
        border: '1px solid rgba(255,255,255,0.06)',
        padding: '20px 16px',
        height: 'fit-content',
        position: 'sticky',
        top: '80px',
      }}
    >
      <p style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '0.1em', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', marginBottom: '20px' }}>
        Workflow
      </p>
      {stages.map((stage, i) => {
        const Icon = STAGE_ICONS[stage.id] || Target;
        const color = AGENT_COLORS[stage.id] || '#7C3AED';
        const isActive = i === currentStageIndex;
        const isDone = i < currentStageIndex;
        return (
          <div key={stage.id} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', marginBottom: '4px' }}>
            {/* Connector line + dot column */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '20px', flexShrink: 0 }}>
              <div
                style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '6px',
                  background: isActive ? `rgba(${hexToRgb(color)}, 0.2)` : isDone ? 'rgba(34,197,94,0.12)' : 'rgba(255,255,255,0.04)',
                  border: `1px solid ${isActive ? color : isDone ? 'rgba(34,197,94,0.4)' : 'rgba(255,255,255,0.08)'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  transition: 'all 300ms ease',
                  boxShadow: isActive ? `0 0 10px ${color}40` : 'none',
                }}
              >
                <Icon size={10} color={isActive ? color : isDone ? '#22C55E' : 'rgba(255,255,255,0.25)'} />
              </div>
              {i < stages.length - 1 && (
                <div style={{ width: '1px', height: '24px', background: isDone ? 'rgba(34,197,94,0.3)' : 'rgba(255,255,255,0.06)', margin: '2px 0' }} />
              )}
            </div>
            <div style={{ paddingBottom: i < stages.length - 1 ? '24px' : '0', paddingTop: '2px' }}>
              <span
                style={{
                  fontSize: '12px',
                  fontWeight: isActive ? 600 : 400,
                  color: isActive ? color : isDone ? '#22C55E' : 'rgba(255,255,255,0.3)',
                  transition: 'color 300ms ease',
                  display: 'block',
                }}
              >
                {stage.name}
              </span>
              {isActive && (
                <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}>
                  <span style={{ width: '5px', height: '5px', borderRadius: '50%', background: color, display: 'inline-block', animation: 'pulse-ring 1.5s ease-in-out infinite' }} />
                  Active
                </span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function AgentActivityFeed({ messages }: { messages: string[] }) {
  const feedRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (feedRef.current) feedRef.current.scrollTop = feedRef.current.scrollHeight;
  }, [messages]);

  return (
    <div
      ref={feedRef}
      style={{
        background: '#111827',
        borderRadius: '10px',
        border: '1px solid rgba(255,255,255,0.06)',
        padding: '16px',
        height: '160px',
        overflowY: 'auto',
        fontFamily: '"Fira Code", "JetBrains Mono", monospace',
        fontSize: '13px',
      }}
    >
      {messages.map((msg, i) => (
        <div
          key={i}
          style={{
            display: 'flex',
            gap: '10px',
            marginBottom: '8px',
            animation: 'slide-in-right 200ms ease-out both',
          }}
        >
          <span style={{ color: 'rgba(255,255,255,0.2)', flexShrink: 0 }}>{String(i + 1).padStart(2, '0')}</span>
          <span style={{ color: i === messages.length - 1 ? '#22C55E' : 'rgba(255,255,255,0.5)' }}>
            {msg}
            {i === messages.length - 1 && <span style={{ animation: 'blink 1s step-end infinite' }}> ▋</span>}
          </span>
        </div>
      ))}
    </div>
  );
}

function StatePreview({ stageIndex, liveState }: { stageIndex: number; liveState: any }) {
  const project = DEMO_FINANCE_PROJECT;
  
  const getPanelData = () => {
    if (liveState) {
      switch (stageIndex) {
        case 0:
          return {
            title: 'Challenge',
            content: liveState.project?.challenge_statements?.[0] || 'No challenge statement provided'
          };
        case 1:
          return {
            title: 'Problem Analysis',
            content: liveState.problem_analysis 
              ? `Refined Problem:\n${liveState.problem_analysis.refined_problem_statement}\n\nSuccess Metrics:\n${(liveState.problem_analysis.success_metrics || []).join('\n')}`
              : 'Analyzing problem...'
          };
        case 2:
          return {
            title: 'Research Complete',
            content: liveState.validation_reports
              ? `Research findings incorporated for validation.`
              : 'Searching competitors, APIs, and libraries...'
          };
        case 3:
          return {
            title: 'Ideas Generated',
            content: liveState.generated_ideas
              ? (liveState.generated_ideas || []).map((idea: any) => `• ${idea.title}`).join('\n')
              : 'Generating ideas...'
          };
        case 4:
          return {
            title: 'Validation Complete',
            content: liveState.generated_ideas
              ? (liveState.generated_ideas || []).map((idea: any) => `${idea.title}: ${Math.round(idea.innovation_score * 10)}/100`).join('\n')
              : 'Validating concepts...'
          };
        case 5:
          return {
            title: 'Selected Idea',
            content: liveState.selected_idea
              ? `✓ ${liveState.selected_idea.title}\n\n${liveState.selected_idea.description}`
              : 'Awaiting human selection checkpoint...'
          };
        case 6:
          return {
            title: 'Architecture',
            content: liveState.architecture
              ? `System design packages generated.`
              : 'Recommending tech stack and component design...'
          };
        case 7:
          return {
            title: 'Build Plan',
            content: liveState.build_package
              ? `Milestones and developer task lists generated.`
              : 'Preparing roadmap & execution plan...'
          };
        case 8:
          return {
            title: 'Presentation',
            content: liveState.presentation
              ? `Pitch slides structured.`
              : 'Generating judge-ready slide content...'
          };
        case 9:
        case 10:
          return {
            title: 'Pitch Ready',
            content: liveState.pitch
              ? `Elevator pitch and Q&A simulator scripts ready.`
              : 'Preparing elevator pitch...'
          };
      }
    }
    const panels = [
      { title: 'Challenge', content: project.challenge.slice(0, 200) + '...' },
      { title: 'Problem Analysis', content: 'Stakeholders: Students, Parents, Financial institutions\nPain Points: Low financial awareness, No budgeting habits\nSuccess Metrics: User retention, habit formation rate' },
      { title: 'Research Complete', content: `${project.research.competitors.length} Competitors • ${project.research.apis.length} APIs • ${project.research.ossProjects.length} OSS Projects\n\n${project.research.insights[0]}` },
      { title: 'Ideas Generated', content: project.ideas.map((idea) => `• ${idea.title}`).join('\n') },
      { title: 'Validation Complete', content: project.ideas.map((idea) => `${idea.title}: ${idea.scores.innovation}/100`).join('\n') },
      { title: 'Selected Idea', content: `✓ ${project.ideas[0].title}\n\n${project.ideas[0].tagline}` },
      { title: 'Architecture', content: 'Frontend: Next.js 15\nBackend: FastAPI + LangGraph\nDatabase: PostgreSQL + Redis\nAI: Groq / Gemini / Tavily' },
      { title: 'Build Plan', content: project.buildPlan.milestones.map((m) => `${m.day}: ${m.title}`).join('\n') },
      { title: 'Presentation', content: '12 slides generated\nExecutive Summary, Problem, Solution, Tech, Architecture, Demo, Pitch, Q&A...' },
      { title: 'Pitch Ready', content: `30s Pitch: Ready\n2 Min Pitch: Ready\nJudge Q&A: ${project.pitch.judgeQA.length} questions prepared` },
    ];
    return panels[Math.min(stageIndex, panels.length - 1)];
  };

  const current = getPanelData();
  return (
    <div
      style={{
        width: '240px',
        flexShrink: 0,
        background: '#0B1020',
        borderRadius: '16px',
        border: '1px solid rgba(255,255,255,0.06)',
        padding: '20px',
        height: 'fit-content',
        position: 'sticky',
        top: '80px',
      }}
    >
      <p style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '0.1em', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', marginBottom: '16px' }}>
        Live State
      </p>
      <div key={stageIndex} style={{ animation: 'fade-in 300ms ease-out' }}>
        <p style={{ fontSize: '13px', fontWeight: 600, color: '#A855F7', marginBottom: '10px' }}>{current.title}</p>
        <pre
          style={{
            fontSize: '12px',
            color: 'rgba(255,255,255,0.5)',
            lineHeight: 1.7,
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            margin: 0,
            fontFamily: 'Inter, sans-serif',
          }}
        >
          {current.content}
        </pre>
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

function getStageIndex(backendStage: string): number {
  switch (backendStage) {
    case 'challenge_intelligence': return 0;
    case 'problem_analysis': return 1;
    case 'opportunity_discovery': return 2;
    case 'idea_generation': return 3;
    case 'idea_validation': return 4;
    case 'human_selection':
    case 'idea_selection': return 5;
    case 'tech_stack':
    case 'architecture': return 6;
    case 'build_accelerator':
    case 'build_plan': return 7;
    case 'presentation': return 8;
    case 'pitch': return 9;
    case 'export': return 9;
    default: return 0;
  }
}

export default function WorkflowPage({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = use(params);
  const searchParams = useSearchParams();
  const wId = searchParams.get('wId');

  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [taskMessages, setTaskMessages] = useState<string[]>([]);
  const [elapsed, setElapsed] = useState(0);
  const [progress, setProgress] = useState(0);
  const [complete, setComplete] = useState(false);
  const [waitingForSelection, setWaitingForSelection] = useState(false);
  const [liveState, setLiveState] = useState<any>(null);
  const taskRef = useRef<string[]>([]);

  useEffect(() => {
    const timer = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  // Poll backend workflow execution if wId is present
  useEffect(() => {
    if (!wId || projectId === 'demo-finance-001') {
      return;
    }

    let intervalId: NodeJS.Timeout;

    const pollStatus = async () => {
      try {
        const statusRes = await getWorkflowStatus(wId);
        if (statusRes.success) {
          const { status, current_stage, progress: backendProgress } = statusRes.data;

          const stageIdx = getStageIndex(current_stage);
          setCurrentStageIndex(stageIdx);
          setProgress(backendProgress);

          const tasks = STAGE_TASKS[current_stage] || ['Processing stage details...'];
          setTaskMessages(tasks);

          if (status === 'waiting_for_user') {
            setWaitingForSelection(true);
            setComplete(false);
            clearInterval(intervalId);
          } else if (status === 'completed') {
            setComplete(true);
            setWaitingForSelection(false);
            clearInterval(intervalId);
          } else if (status === 'failed') {
            setComplete(false);
            setWaitingForSelection(false);
            clearInterval(intervalId);
            alert('Workflow execution failed. Please verify API keys in backend env.');
          }
        }
      } catch (err) {
        console.error('[exHacker API] Polling status failed:', err);
      }
    };

    pollStatus();
    intervalId = setInterval(pollStatus, 2500);
    return () => clearInterval(intervalId);
  }, [wId, projectId]);

  // Fetch full live state
  useEffect(() => {
    if (!wId || projectId === 'demo-finance-001') return;

    const fetchState = async () => {
      try {
        const stateRes = await getWorkflowState(wId);
        if (stateRes.success && stateRes.data.state) {
          setLiveState(stateRes.data.state);
        }
      } catch (err) {
        console.error('[exHacker API] Fetching live state failed:', err);
      }
    };

    fetchState();
    const stateInterval = setInterval(fetchState, 5000);
    return () => clearInterval(stateInterval);
  }, [wId, projectId]);

  // Simulate workflow progression (Fallback)
  useEffect(() => {
    if (wId && projectId !== 'demo-finance-001') {
      return;
    }

    if (currentStageIndex >= WORKFLOW_STAGES.length) {
      setComplete(true);
      return;
    }

    const stage = WORKFLOW_STAGES[currentStageIndex];
    const tasks = STAGE_TASKS[stage.id] || ['Processing...'];
    taskRef.current = [];
    setTaskMessages([]);

    let taskIdx = 0;
    const taskInterval = setInterval(() => {
      if (taskIdx < tasks.length) {
        taskRef.current = [...taskRef.current, tasks[taskIdx]];
        setTaskMessages([...taskRef.current]);
        taskIdx++;
      } else {
        clearInterval(taskInterval);
        setTimeout(() => {
          setCurrentStageIndex((prev) => prev + 1);
          setProgress(Math.round(((currentStageIndex + 1) / WORKFLOW_STAGES.length) * 100));
        }, 800);
      }
    }, 1200);

    return () => clearInterval(taskInterval);
  }, [currentStageIndex]);

  const fmtTime = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
  const stage = WORKFLOW_STAGES[Math.min(currentStageIndex, WORKFLOW_STAGES.length - 1)];
  const agentColor = AGENT_COLORS[stage?.id] || '#7C3AED';
  const AgentIcon = STAGE_ICONS[stage?.id] || Target;

  return (
    <div style={{ background: '#050816', minHeight: '100vh', color: '#F1F5F9' }}>
      <Navbar />
      <div style={{ paddingTop: '80px' }}>
        {/* Page Header */}
        <div
          style={{
            borderBottom: '1px solid rgba(255,255,255,0.06)',
            padding: '20px 32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div>
            <h1 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '4px' }}>Workflow Command Center</h1>
            <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>Project: {liveState?.project?.name || DEMO_FINANCE_PROJECT.name}</p>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span
              style={{
                padding: '5px 14px',
                borderRadius: '99px',
                fontSize: '12px',
                fontWeight: 500,
                background: complete 
                  ? 'rgba(34,197,94,0.12)' 
                  : waitingForSelection 
                    ? 'rgba(245,158,11,0.12)' 
                    : 'rgba(59,130,246,0.12)',
                color: complete 
                  ? '#22C55E' 
                  : waitingForSelection 
                    ? '#F59E0B' 
                    : '#3B82F6',
                border: `1px solid ${complete 
                  ? 'rgba(34,197,94,0.3)' 
                  : waitingForSelection 
                    ? 'rgba(245,158,11,0.3)' 
                    : 'rgba(59,130,246,0.3)'}`,
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              {!complete && !waitingForSelection && <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#3B82F6', display: 'inline-block', animation: 'pulse-ring 1.5s ease-in-out infinite' }} />}
              {complete ? 'Complete' : waitingForSelection ? 'Awaiting Selection' : 'Running'}
            </span>
            {waitingForSelection && (
              <Link
                href={`/ideas/${projectId}?wId=${wId}`}
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px',
                  padding: '8px 20px', borderRadius: '8px', background: '#F59E0B',
                  color: '#fff', fontSize: '13px', fontWeight: 600, textDecoration: 'none',
                }}
              >
                <Star size={14} /> Select Idea <ArrowRight size={14} />
              </Link>
            )}
            {complete && (
              <Link
                href={`/dashboard/${projectId}?wId=${wId}`}
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px',
                  padding: '8px 20px', borderRadius: '8px', background: '#7C3AED',
                  color: '#fff', fontSize: '13px', fontWeight: 600, textDecoration: 'none',
                }}
              >
                View Results <ArrowRight size={14} />
              </Link>
            )}
          </div>
        </div>

        {/* Three-Column Layout */}
        <div
          style={{
            display: 'flex',
            gap: '20px',
            padding: '24px 32px',
            maxWidth: '1400px',
            margin: '0 auto',
            alignItems: 'flex-start',
          }}
        >
          {/* Left: Timeline */}
          <TimelinePanel stages={WORKFLOW_STAGES} currentStageIndex={Math.min(currentStageIndex, WORKFLOW_STAGES.length - 1)} />

          {/* Center: Agent Activity */}
          <div style={{ flex: 1, minWidth: 0 }}>
            {/* Active Agent Card */}
            <div
              style={{
                background: '#0B1020',
                borderRadius: '20px',
                border: `1px solid ${complete ? 'rgba(34,197,94,0.3)' : `rgba(${hexToRgb(agentColor)}, 0.25)`}`,
                padding: '32px',
                marginBottom: '20px',
                boxShadow: complete ? 'none' : `0 0 30px rgba(${hexToRgb(agentColor)}, 0.08)`,
                transition: 'all 400ms ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '20px', marginBottom: '24px' }}>
                {/* Agent Avatar */}
                <div
                  style={{
                    width: '64px',
                    height: '64px',
                    borderRadius: '16px',
                    background: `rgba(${hexToRgb(agentColor)}, 0.15)`,
                    border: `1px solid rgba(${hexToRgb(agentColor)}, 0.3)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    color: agentColor,
                    animation: complete ? 'none' : 'pulse-ring 2s ease-in-out infinite',
                  }}
                >
                  <AgentIcon size={28} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '6px' }}>
                    <h2 style={{ fontSize: '22px', fontWeight: 700 }}>{complete ? 'Workflow Complete' : stage?.name || 'Processing'}</h2>
                    <span
                      style={{
                        padding: '3px 10px',
                        borderRadius: '99px',
                        fontSize: '11px',
                        fontWeight: 600,
                        background: complete ? 'rgba(34,197,94,0.12)' : `rgba(${hexToRgb(agentColor)}, 0.12)`,
                        color: complete ? '#22C55E' : agentColor,
                        border: `1px solid ${complete ? 'rgba(34,197,94,0.3)' : `rgba(${hexToRgb(agentColor)}, 0.3)`}`,
                        display: 'flex', alignItems: 'center', gap: '4px',
                      }}
                    >
                      {complete ? <><CheckCircle size={10} /> Done</> : 'Active'}
                    </span>
                  </div>
                  <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.5)' }}>
                    {complete
                      ? 'All 10 agents completed. Your project package is ready.'
                      : `Step ${Math.min(currentStageIndex + 1, WORKFLOW_STAGES.length)} of ${WORKFLOW_STAGES.length} — AI agents are working in parallel`}
                  </p>
                </div>
              </div>

              {/* Progress Bar */}
              <div style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>Overall Progress</span>
                  <span style={{ fontSize: '13px', fontWeight: 700, color: agentColor }}>{Math.min(progress, 100)}%</span>
                </div>
                <div style={{ height: '6px', borderRadius: '3px', background: 'rgba(255,255,255,0.06)' }}>
                  <div
                    style={{
                      height: '100%',
                      width: `${Math.min(progress, 100)}%`,
                      borderRadius: '3px',
                      background: `linear-gradient(90deg, ${agentColor}, ${agentColor}cc)`,
                      transition: 'width 600ms cubic-bezier(0.16,1,0.3,1)',
                      boxShadow: `0 0 10px ${agentColor}60`,
                    }}
                  />
                </div>
              </div>

              {/* Activity Feed */}
              {!complete && (
                <div>
                  <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.3)', marginBottom: '10px', fontWeight: 500 }}>Agent Log</p>
                  <AgentActivityFeed messages={taskMessages} />
                </div>
              )}

              {waitingForSelection && (
                <div
                  style={{
                    padding: '20px',
                    borderRadius: '12px',
                    background: 'rgba(245,158,11,0.06)',
                    border: '1px solid rgba(245,158,11,0.2)',
                    textAlign: 'center',
                  }}
                >
                   <p style={{ fontSize: '16px', fontWeight: 600, color: '#F59E0B', marginBottom: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                    <HourglassIcon size={16} /> Awaiting your selection
                  </p>
                  <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.5)', marginBottom: '16px' }}>
                    The AI Validator has analyzed the generated ideas with live web research. Click the button below to pick the winning concept.
                  </p>
                  <Link
                    href={`/ideas/${projectId}?wId=${wId}`}
                    style={{
                      display: 'inline-flex', alignItems: 'center', gap: '6px',
                      padding: '10px 24px', borderRadius: '8px', background: '#F59E0B',
                      color: '#fff', fontSize: '14px', fontWeight: 600, textDecoration: 'none',
                      boxShadow: '0 0 15px rgba(245,158,11,0.3)',
                    }}
                  >
                    <Star size={14} /> Select Winning Idea
                  </Link>
                </div>
              )}

              {complete && (
                <div
                  style={{
                    padding: '20px',
                    borderRadius: '12px',
                    background: 'rgba(34,197,94,0.06)',
                    border: '1px solid rgba(34,197,94,0.2)',
                    textAlign: 'center',
                  }}
                >
                  <p style={{ fontSize: '16px', fontWeight: 600, color: '#22C55E', marginBottom: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                    <Sparkles size={16} /> Your AI package is ready
                  </p>
                  <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.5)' }}>Architecture, pitch, presentation, and build plan generated successfully</p>
                </div>
              )}
            </div>

            {/* Completed Stages Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '12px' }}>
              {WORKFLOW_STAGES.slice(0, Math.min(currentStageIndex, WORKFLOW_STAGES.length)).map((s, i) => {
                const Icon = STAGE_ICONS[s.id] || Target;
                const color = AGENT_COLORS[s.id] || '#22C55E';
                return (
                  <div
                    key={s.id}
                    style={{
                      background: '#0B1020',
                      borderRadius: '12px',
                      border: '1px solid rgba(34,197,94,0.2)',
                      padding: '16px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      animation: 'slide-up 300ms ease-out both',
                      animationDelay: `${i * 50}ms`,
                    }}
                  >
                    <div
                      style={{
                        width: '32px', height: '32px', borderRadius: '8px',
                        background: 'rgba(34,197,94,0.1)', display: 'flex',
                        alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                      }}
                    >
                      <CheckCircle size={14} color="#22C55E" />
                    </div>
                    <span style={{ fontSize: '12px', fontWeight: 500, color: 'rgba(255,255,255,0.6)' }}>{s.name}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right: State Preview */}
          <StatePreview stageIndex={Math.min(currentStageIndex, WORKFLOW_STAGES.length - 1)} liveState={liveState} />
        </div>

        {/* Footer Bar */}
        <div
          style={{
            position: 'fixed',
            bottom: 0, left: 0, right: 0,
            background: 'rgba(5,8,22,0.9)',
            backdropFilter: 'blur(16px)',
            borderTop: '1px solid rgba(255,255,255,0.06)',
            padding: '12px 32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            zIndex: 50,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Clock size={14} color="rgba(255,255,255,0.3)" />
              <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.5)' }}>{fmtTime(elapsed)}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={14} color={agentColor} />
              <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.5)' }}>
                {complete ? 'All agents complete' : stage?.name || 'Processing'}
              </span>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>{Math.min(progress, 100)}% complete</span>
            <ChevronRight size={14} color="rgba(255,255,255,0.2)" />
          </div>
        </div>
      </div>
      <div style={{ height: '56px' }} />
      <style>{`
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
        @keyframes slide-in-right { from { opacity: 0; transform: translateX(10px); } to { opacity: 1; transform: translateX(0); } }
      `}</style>
    </div>
  );
}
