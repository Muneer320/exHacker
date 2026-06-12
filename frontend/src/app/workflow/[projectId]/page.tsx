'use client';

import { use, useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  Target, Brain, Search, Lightbulb, CheckCircle, GitBranch, Zap, Monitor, Mic,
  Star, Clock, ArrowRight, ChevronRight, ChevronDown, ChevronUp, Activity, Sparkles, PartyPopper, HourglassIcon,
  Calendar, Terminal
} from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import { DEMO_FINANCE_PROJECT, WORKFLOW_STAGES } from '@/mock/data';
import { getWorkflowStatus, getWorkflowState } from '@/services/api';

const STAGE_ICONS: Record<string, React.ElementType> = {
  challenge_intelligence: Target,
  problem_analysis: Brain,
  opportunity_discovery: Search,
  idea_generation: Lightbulb,
  idea_validation: CheckCircle,
  idea_selection: Star,
  architecture: GitBranch,
  build_plan: Calendar,
  presentation: Monitor,
  pitch: Mic,
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

const STAGE_DESCRIPTIONS: Record<string, string> = {
  challenge_intelligence: 'Analyzing challenge scope & constraints',
  problem_analysis: 'Mapping stakeholders & defining pain points',
  opportunity_discovery: 'Scanning competitors, APIs & open-source libraries',
  idea_generation: 'Brainstorming & scoring 5 unique concepts',
  idea_validation: 'Deep-dive analysis & feasibility scoring',
  idea_selection: 'Human-in-the-loop selection checkpoint',
  architecture: 'Designing components & Mermaid data flows',
  build_plan: 'Structuring milestones & developer task lists',
  presentation: 'Creating slide decks & project documentation',
  pitch: 'Formulating pitches & preparing judge Q&A',
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
    case 'build_plan':
    case 'build_accelerator': return 7;
    case 'presentation': return 8;
    case 'pitch': return 9;
    case 'export': return 9;
    default: return 0;
  }
}

function StageTerminal({
  logs,
  isRunning,
  simulatedTasks,
}: {
  logs: any[];
  isRunning: boolean;
  simulatedTasks: string[];
}) {
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, isRunning]);

  return (
    <div
      style={{
        background: '#040713',
        borderRadius: '8px',
        border: '1px solid rgba(255,255,255,0.06)',
        padding: '16px',
        maxHeight: '220px',
        overflowY: 'auto',
        fontFamily: '"Fira Code", "JetBrains Mono", monospace',
        fontSize: '12px',
        marginTop: '12px',
        boxShadow: 'inset 0 0 10px rgba(0,0,0,0.8)',
      }}
    >
      {logs.length > 0 ? (
        logs.map((log, i) => (
          <div key={i} style={{ marginBottom: '6px', color: 'rgba(255,255,255,0.7)', lineHeight: 1.5 }}>
            <span style={{ color: '#A855F7', marginRight: '8px' }}>[{new Date(log.timestamp).toLocaleTimeString()}]</span>
            <span style={{ color: log.message.includes('error') ? '#EF4444' : log.message.includes('completed') ? '#22C55E' : '#3B82F6', marginRight: '6px' }}>
              &gt;
            </span>
            <span>{log.message}</span>
          </div>
        ))
      ) : isRunning ? (
        simulatedTasks.map((task, i) => (
          <div key={i} style={{ marginBottom: '6px', color: 'rgba(255,255,255,0.5)', lineHeight: 1.5 }}>
            <span style={{ color: 'rgba(255,255,255,0.3)', marginRight: '8px' }}>[Live]</span>
            <span style={{ color: '#3B82F6', marginRight: '6px' }}>&gt;</span>
            <span>{task}</span>
          </div>
        ))
      ) : (
        <div style={{ color: 'rgba(255,255,255,0.25)', fontSize: '11px', fontStyle: 'italic' }}>
          Queue empty. Awaiting execution...
        </div>
      )}
      {isRunning && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '8px', color: '#22C55E' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#22C55E', display: 'inline-block', animation: 'blink 1s step-end infinite' }} />
          <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.4)' }}>Executing instructions...</span>
        </div>
      )}
      <div ref={terminalEndRef} />
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
            title: 'Challenge Intelligence',
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
            title: 'Research Analysis',
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
      { title: 'Challenge Intelligence', content: project.challenge.slice(0, 200) + '...' },
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
        background: '#0B1020',
        borderRadius: '16px',
        border: '1px solid rgba(255,255,255,0.06)',
        padding: '20px',
        animation: 'fade-in 300ms ease-out',
      }}
    >
      <p style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '0.1em', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', marginBottom: '16px' }}>
        Live State Preview
      </p>
      <div>
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
            maxHeight: '300px',
            overflowY: 'auto',
          }}
        >
          {current.content}
        </pre>
      </div>
    </div>
  );
}

export default function WorkflowPage({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = use(params);
  const router = useRouter();
  const searchParams = useSearchParams();
  const wId = searchParams.get('wId');

  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const [progress, setProgress] = useState(0);
  const [complete, setComplete] = useState(false);
  const [waitingForSelection, setWaitingForSelection] = useState(false);
  const [liveState, setLiveState] = useState<any>(null);
  const [expandedStages, setExpandedStages] = useState<Record<string, boolean>>({});
  const [countdown, setCountdown] = useState<number | null>(null);

  // Timer
  useEffect(() => {
    const timer = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  // Set expanded stages based on current active stage
  useEffect(() => {
    const activeStage = WORKFLOW_STAGES[currentStageIndex]?.id;
    if (activeStage) {
      setExpandedStages((prev) => ({
        ...prev,
        [activeStage]: true,
      }));
    }
  }, [currentStageIndex]);

  // Countdown redirect
  useEffect(() => {
    if (complete) {
      setCountdown(2);
    }
  }, [complete]);

  useEffect(() => {
    if (countdown === null) return;
    if (countdown <= 0) {
      router.push(`/dashboard/${projectId}?wId=${wId || ''}`);
      return;
    }
    const timer = setTimeout(() => {
      setCountdown((c) => (c !== null ? c - 1 : null));
    }, 1000);
    return () => clearTimeout(timer);
  }, [countdown, projectId, wId, router]);

  // Poll backend workflow status
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
    const stateInterval = setInterval(fetchState, 4000);
    return () => clearInterval(stateInterval);
  }, [wId, projectId]);

  // Simulate workflow progression (Fallback Mode)
  useEffect(() => {
    if (wId && projectId !== 'demo-finance-001') {
      return;
    }

    if (currentStageIndex >= WORKFLOW_STAGES.length) {
      setComplete(true);
      return;
    }

    const timer = setTimeout(() => {
      const nextIdx = currentStageIndex + 1;
      if (nextIdx === 5) {
        // Selection checkpoint
        setWaitingForSelection(true);
        setCurrentStageIndex(nextIdx);
        setProgress(Math.round((nextIdx / WORKFLOW_STAGES.length) * 100));
      } else if (nextIdx >= WORKFLOW_STAGES.length) {
        setComplete(true);
        setProgress(100);
      } else {
        setCurrentStageIndex(nextIdx);
        setProgress(Math.round((nextIdx / WORKFLOW_STAGES.length) * 100));
      }
    }, 8000); // 8 seconds per stage for fallback simulation

    return () => clearTimeout(timer);
  }, [currentStageIndex, wId, projectId]);

  const toggleStage = (stageId: string) => {
    setExpandedStages((prev) => ({
      ...prev,
      [stageId]: !prev[stageId],
    }));
  };

  const fmtTime = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;

  const getStageLogs = (stageId: string, isActive: boolean, isDone: boolean) => {
    const realLogs = liveState?.logs?.filter((log: any) => log.stage === stageId) || [];
    if (realLogs.length > 0) {
      return realLogs;
    }

    const tasks = STAGE_TASKS[stageId] || [];
    if (isDone) {
      return tasks.map((task, idx) => ({
        timestamp: new Date(Date.now() - (tasks.length - idx) * 2000).toISOString(),
        message: `${task} - completed successfully`,
        stage: stageId,
      }));
    }

    if (isActive) {
      const elapsedLogsCount = Math.min(Math.floor((elapsed % 8) / 2) + 1, tasks.length);
      return tasks.slice(0, elapsedLogsCount).map((task, idx) => ({
        timestamp: new Date(Date.now() - (elapsedLogsCount - idx) * 2000).toISOString(),
        message: task,
        stage: stageId,
      }));
    }

    return [];
  };

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
            <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>
              Project: {liveState?.project?.name || DEMO_FINANCE_PROJECT.name}
            </p>
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
                border: `1px solid ${
                  complete
                    ? 'rgba(34,197,94,0.3)'
                    : waitingForSelection
                      ? 'rgba(245,158,11,0.3)'
                      : 'rgba(59,130,246,0.3)'
                }`,
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              {!complete && !waitingForSelection && (
                <span
                  style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    background: '#3B82F6',
                    display: 'inline-block',
                    animation: 'pulse-ring 1.5s ease-in-out infinite',
                  }}
                />
              )}
              {complete ? 'Complete' : waitingForSelection ? 'Awaiting Selection' : 'Running'}
            </span>
          </div>
        </div>

        {/* 2-Column Responsive Layout */}
        <div
          style={{
            display: 'flex',
            gap: '24px',
            padding: '24px 32px 100px',
            maxWidth: '1400px',
            margin: '0 auto',
            alignItems: 'flex-start',
          }}
        >
          {/* Left Column: Control Panel & Live State Preview */}
          <div
            style={{
              width: '320px',
              flexShrink: 0,
              display: 'flex',
              flexDirection: 'column',
              gap: '20px',
              position: 'sticky',
              top: '80px',
            }}
          >
            {/* Status Card */}
            <div style={{ background: '#0B1020', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '16px', padding: '24px' }}>
              <p style={{ fontSize: '11px', fontWeight: 600, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '16px' }}>
                Status Summary
              </p>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <span style={{ fontSize: '14px', color: 'rgba(255,255,255,0.5)' }}>Overall Progress</span>
                <span style={{ fontSize: '16px', fontWeight: 800, color: '#7C3AED' }}>{Math.min(progress, 100)}%</span>
              </div>

              <div style={{ height: '6px', borderRadius: '3px', background: 'rgba(255,255,255,0.06)', marginBottom: '20px' }}>
                <div
                  style={{
                    height: '100%',
                    width: `${Math.min(progress, 100)}%`,
                    borderRadius: '3px',
                    background: 'linear-gradient(90deg, #7C3AED, #06B6D4)',
                    transition: 'width 600ms cubic-bezier(0.16,1,0.3,1)',
                  }}
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                  <span style={{ color: 'rgba(255,255,255,0.4)' }}>Time Elapsed:</span>
                  <span style={{ color: '#F1F5F9', fontWeight: 600, fontFamily: 'monospace' }}>{fmtTime(elapsed)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                  <span style={{ color: 'rgba(255,255,255,0.4)' }}>Active Agents:</span>
                  <span style={{ color: '#3B82F6', fontWeight: 600 }}>10 Parallel</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                  <span style={{ color: 'rgba(255,255,255,0.4)' }}>Pipeline Status:</span>
                  <span
                    style={{
                      color: complete ? '#22C55E' : waitingForSelection ? '#F59E0B' : '#3B82F6',
                      fontWeight: 600,
                    }}
                  >
                    {complete ? 'Complete' : waitingForSelection ? 'Awaiting Checkpoint' : 'Processing'}
                  </span>
                </div>
              </div>

              {waitingForSelection && (
                <div style={{ marginTop: '24px' }}>
                  <Link
                    href={`/ideas/${projectId}?wId=${wId}`}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px',
                      padding: '12px 16px',
                      borderRadius: '8px',
                      background: 'linear-gradient(135deg, #F59E0B, #D97706)',
                      color: '#fff',
                      fontSize: '13px',
                      fontWeight: 700,
                      textDecoration: 'none',
                      boxShadow: '0 0 15px rgba(245,158,11,0.35)',
                      textAlign: 'center',
                    }}
                  >
                    <Star size={14} /> Select Idea Checkpoint
                  </Link>
                </div>
              )}

              {complete && (
                <div style={{ marginTop: '24px' }}>
                  <Link
                    href={`/dashboard/${projectId}?wId=${wId}`}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px',
                      padding: '12px 16px',
                      borderRadius: '8px',
                      background: 'linear-gradient(135deg, #7C3AED, #4F46E5)',
                      color: '#fff',
                      fontSize: '13px',
                      fontWeight: 700,
                      textDecoration: 'none',
                      boxShadow: '0 0 15px rgba(124,58,237,0.35)',
                      textAlign: 'center',
                    }}
                  >
                    View Results Dashboard
                  </Link>
                </div>
              )}
            </div>

            {/* Live State Preview */}
            <StatePreview stageIndex={Math.min(currentStageIndex, WORKFLOW_STAGES.length - 1)} liveState={liveState} />
          </div>

          {/* Right Column: 10 Agent Pipeline Cards */}
          <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {WORKFLOW_STAGES.map((s, i) => {
              const Icon = STAGE_ICONS[s.id] || Target;
              const color = AGENT_COLORS[s.id] || '#7C3AED';
              const isActive = i === currentStageIndex;
              const isDone = i < currentStageIndex;
              const isSelectionCheckpoint = s.id === 'idea_selection' && waitingForSelection;

              let statusLabel = 'Waiting';
              let statusColor = 'rgba(255,255,255,0.35)';
              let statusBg = 'rgba(255,255,255,0.02)';
              let statusBorder = 'rgba(255,255,255,0.06)';

              if (isDone) {
                statusLabel = 'Completed';
                statusColor = '#22C55E';
                statusBg = 'rgba(34,197,94,0.12)';
                statusBorder = 'rgba(34,197,94,0.3)';
              } else if (isSelectionCheckpoint) {
                statusLabel = 'Awaiting Selection';
                statusColor = '#F59E0B';
                statusBg = 'rgba(245,158,11,0.12)';
                statusBorder = 'rgba(245,158,11,0.3)';
              } else if (isActive) {
                statusLabel = 'Running';
                statusColor = '#3B82F6';
                statusBg = 'rgba(59,130,246,0.12)';
                statusBorder = 'rgba(59,130,246,0.3)';
              }

              const isExpanded = !!expandedStages[s.id];
              const stageLogs = getStageLogs(s.id, isActive, isDone);
              const simulatedTasks = STAGE_TASKS[s.id] || [];

              return (
                <div
                  key={s.id}
                  style={{
                    background: '#0B1020',
                    borderRadius: '16px',
                    border: `1px solid ${isActive ? color : isDone ? 'rgba(34,197,94,0.2)' : 'rgba(255,255,255,0.06)'}`,
                    padding: '20px',
                    transition: 'all 200ms ease',
                    boxShadow: isActive ? `0 0 20px rgba(${hexToRgb(color)}, 0.05)` : 'none',
                  }}
                >
                  {/* Header */}
                  <div
                    onClick={() => toggleStage(s.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      cursor: 'pointer',
                      userSelect: 'none',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <div
                        style={{
                          width: '40px',
                          height: '40px',
                          borderRadius: '10px',
                          background: `rgba(${hexToRgb(color)}, 0.1)`,
                          border: `1px solid rgba(${hexToRgb(color)}, 0.25)`,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: color,
                        }}
                      >
                        <Icon size={18} />
                      </div>
                      <div>
                        <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#F1F5F9', marginBottom: '2px' }}>{s.name}</h3>
                        <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>
                          {STAGE_DESCRIPTIONS[s.id] || s.name}
                        </p>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span
                        style={{
                          padding: '3px 10px',
                          borderRadius: '99px',
                          fontSize: '11px',
                          fontWeight: 600,
                          background: statusBg,
                          color: statusColor,
                          border: `1px solid ${statusBorder}`,
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                        }}
                      >
                        {isActive && !isSelectionCheckpoint && (
                          <span
                            style={{
                              width: '5px',
                              height: '5px',
                              borderRadius: '50%',
                              background: '#3B82F6',
                              display: 'inline-block',
                              animation: 'pulse-ring 1.5s ease-in-out infinite',
                            }}
                          />
                        )}
                        {isSelectionCheckpoint && (
                          <span
                            style={{
                              width: '5px',
                              height: '5px',
                              borderRadius: '50%',
                              background: '#F59E0B',
                              display: 'inline-block',
                              animation: 'pulse-ring 1.5s ease-in-out infinite',
                            }}
                          />
                        )}
                        {statusLabel}
                      </span>

                      {isExpanded ? (
                        <ChevronUp size={16} color="rgba(255,255,255,0.4)" />
                      ) : (
                        <ChevronDown size={16} color="rgba(255,255,255,0.4)" />
                      )}
                    </div>
                  </div>

                  {/* Collapsible Log Terminal */}
                  {isExpanded && (
                    <div style={{ animation: 'slide-up 200ms ease-out' }}>
                      <StageTerminal logs={stageLogs} isRunning={isActive && !isSelectionCheckpoint} simulatedTasks={simulatedTasks} />

                      {isSelectionCheckpoint && (
                        <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-start' }}>
                          <Link
                            href={`/ideas/${projectId}?wId=${wId}`}
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '8px',
                              padding: '10px 20px',
                              borderRadius: '8px',
                              background: 'linear-gradient(135deg, #F59E0B, #D97706)',
                              border: 'none',
                              color: '#fff',
                              fontSize: '13px',
                              fontWeight: 600,
                              textDecoration: 'none',
                              cursor: 'pointer',
                              boxShadow: '0 0 15px rgba(245,158,11,0.4)',
                              transition: 'all 150ms ease',
                            }}
                          >
                            <Star size={14} /> Go to Selection Checkpoint <ArrowRight size={14} />
                          </Link>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer Bar */}
        <div
          style={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
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
              <Activity size={14} color="#7C3AED" />
              <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.5)' }}>
                {complete ? 'Workflow Complete' : 'Executing agents in parallel...'}
              </span>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>{Math.min(progress, 100)}% complete</span>
            <ChevronRight size={14} color="rgba(255,255,255,0.2)" />
          </div>
        </div>
      </div>

      {/* Countdown glassmorphic overlay */}
      {countdown !== null && countdown > 0 && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(5, 8, 22, 0.85)',
            backdropFilter: 'blur(20px)',
            zIndex: 9999,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            animation: 'fade-in 300ms ease-out',
          }}
        >
          <div
            style={{
              textAlign: 'center',
              padding: '40px',
              borderRadius: '24px',
              background: '#0B1020',
              border: '1px solid rgba(34,197,94,0.3)',
              boxShadow: '0 0 50px rgba(34,197,94,0.15)',
              maxWidth: '400px',
              width: '90%',
            }}
          >
            <div
              style={{
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                background: 'rgba(34,197,94,0.1)',
                border: '2px solid rgba(34,197,94,0.4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 24px',
                animation: 'scale-up 400ms ease-out',
              }}
            >
              <PartyPopper size={36} color="#22C55E" />
            </div>
            <h2 style={{ fontSize: '24px', fontWeight: 800, color: '#F1F5F9', marginBottom: '8px' }}>
              Project Package Ready!
            </h2>
            <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.5)', marginBottom: '24px' }}>
              All 10 agents have completed their tasks. Redirecting to dashboard in...
            </p>
            <div style={{ fontSize: '48px', fontWeight: 900, color: '#22C55E', fontFamily: 'monospace', lineHeight: 1 }}>
              {countdown}
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
        @keyframes pulse-ring {
          0% { box-shadow: 0 0 0 0 rgba(59,130,246,0.4); }
          70% { box-shadow: 0 0 0 8px rgba(59,130,246,0); }
          100% { box-shadow: 0 0 0 0 rgba(59,130,246,0); }
        }
        @keyframes scale-up { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
        @keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slide-up { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </div>
  );
}
