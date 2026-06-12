/**
 * exHacker API Service Client
 * Handles connection to FastAPI backend (localhost:8000)
 * Gracefully falls back to mock data if the backend is offline.
 */

import { DEMO_FINANCE_PROJECT } from '@/mock/data';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// ── Health check with caching ─────────────────────────────────────────────
let _healthCache: { alive: boolean; ts: number } | null = null;
const HEALTH_CACHE_MS = 15_000; // cache for 15 seconds

export async function checkBackendHealth(): Promise<boolean> {
  if (_healthCache && Date.now() - _healthCache.ts < HEALTH_CACHE_MS) {
    return _healthCache.alive;
  }
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 2000);
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { signal: controller.signal });
    clearTimeout(timeoutId);
    _healthCache = { alive: res.ok, ts: Date.now() };
    return res.ok;
  } catch {
    clearTimeout(timeoutId);
    _healthCache = { alive: false, ts: Date.now() };
    return false;
  }
}

export function invalidateHealthCache() {
  _healthCache = null;
}

// Helper to fetch or fall back to mock data
async function safeFetch<T>(
  endpoint: string,
  options?: RequestInit,
  mockFallback?: () => T
): Promise<T> {
  try {
    const isOnline = await checkBackendHealth();
    if (!isOnline && mockFallback) {
      console.warn(`[exHacker API] Backend offline → mock: ${endpoint}`);
      return mockFallback();
    }

    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail?.message || `HTTP ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.error(`[exHacker API] ${endpoint}:`, error);
    if (mockFallback) {
      console.warn(`[exHacker API] Error fallback → mock: ${endpoint}`);
      return mockFallback();
    }
    throw error;
  }
}

// ── Interfaces ─────────────────────────────────────────────────────────────

export interface ProjectCreatePayload {
  name: string;
  challenge_statements: string[];
  duration_hours: number;
  team_profile: {
    team_size: number;
    experience_level: string;
    known_technologies: string[];
    preferred_technologies: string[];
  };
}

export interface ProjectResponse {
  success: boolean;
  data: {
    project_id: string;
    workflow_id: string;
    status: string;
  };
  message?: string;
}

export interface WorkflowStatusResponse {
  success: boolean;
  data: {
    workflow_id: string;
    status: string;
    current_stage: string;
    progress: number;
  };
}

export interface WorkflowStateResponse {
  success: boolean;
  data: {
    state: any;
  };
}

export interface IdeasResponse {
  success: boolean;
  data: {
    ideas: any[];
    validation_reports: any[];
  };
}

// ── Comprehensive mock state ────────────────────────────────────────────────
function buildMockState() {
  const p = DEMO_FINANCE_PROJECT;
  const idea = p.ideas[0];
  return {
    project: { name: p.name, challenge_statements: [p.challenge] },
    selected_idea: {
      id: idea.id,
      title: idea.title,
      description: idea.tagline,
      key_features: idea.strengths,
      target_users: ['University students', 'Recent graduates', 'Young professionals'],
      innovation_score: idea.scores.innovation / 10,
      feasibility_score: idea.scores.feasibility / 10,
    },
    generated_ideas: p.ideas,
    validation_reports: p.ideas.map(i => ({
      idea_id: i.id,
      final_score: i.scores.innovation / 10,
      innovation_score: i.scores.innovation / 10,
      feasibility_score: i.scores.feasibility / 10,
      strengths: i.strengths || [],
      competitors: p.research?.competitors || [],
      apis: p.research?.apis || [],
    })),
    architecture: {
      system_design: p.architecture.components.map(c => c.name).join(' → '),
      mermaid_diagram: p.architecture.mermaidDiagram,
      components: p.architecture.components,
    },
    tech_stack: {
      frontend: p.techStack.frontend.map(t => t.name).join(', '),
      backend: p.techStack.backend.map(t => t.name).join(', '),
      database: p.techStack.database.map(t => t.name).join(', '),
      ai_stack: p.techStack.ai.map(t => t.name),
      deployment: p.techStack.infrastructure.map(t => t.name),
      reasoning: [
        ...p.techStack.frontend.map(t => t.reason),
        ...p.techStack.backend.map(t => t.reason),
      ],
    },
    build_package: {
      frontend_tasks: p.buildPlan.milestones[0]?.tasks || [],
      backend_tasks: p.buildPlan.milestones[1]?.tasks || [],
      database_tasks: p.buildPlan.milestones[2]?.tasks || [],
      testing_tasks: ['Write unit tests', 'Integration testing', 'E2E testing with Playwright'],
      deployment_tasks: p.buildPlan.milestones[3]?.tasks || [],
    },
    presentation: {
      slide_content: [
        { title: 'Title & Hook', content: [`${idea.title} — ${idea.tagline}`] },
        { title: 'Problem Statement', content: ['72% of students graduate without basic financial skills', 'Existing tools are adult-focused and complex'] },
        { title: 'Market Opportunity', content: ['$200B student debt crisis', '44M college students in the US', '$1.3T addressable market'] },
        { title: 'Our Solution', content: [idea.title, ...idea.strengths.slice(0, 3)] },
        { title: 'Live Demo', content: ['Real-time AI coaching session', 'Budget analysis in <2 seconds', 'Personalized recommendations'] },
        { title: 'Technical Architecture', content: ['Next.js + FastAPI + LangGraph', '10-stage AI agent workflow', 'Groq + Gemini LLM fallback chain'] },
        { title: 'AI Intelligence', content: ['Multi-agent orchestration', 'Grounded web research via Tavily', 'Context-aware financial coaching'] },
        { title: 'Business Model', content: ['Freemium: free tier with basic features', 'Premium: $9.99/month for full AI coaching', 'Enterprise: university partnership deals'] },
        { title: 'Team & Traction', content: ['Built in 48 hours', 'Full stack: AI + finance domain expertise', 'Validated with 20 student beta users'] },
        { title: 'Roadmap', content: ['Month 1: Launch beta', 'Month 3: University partnerships', 'Month 6: Mobile app', 'Year 1: 100K users'] },
        { title: 'Competitive Advantage', content: ['Only student-first AI finance platform', 'Proprietary coaching model', 'Real bank data via Plaid integration'] },
        { title: 'Call to Action', content: ['Join us in solving the student financial crisis', 'Let\'s build the financial confidence of the next generation'] },
      ],
      demo_story: `Imagine you're a sophomore who just got your first part-time job. You open ${idea.title}, scan your paycheck, and instantly get a personalized savings plan that accounts for your tuition, dorm fees, and coffee habit. That's the magic we've built.`,
    },
    pitch: {
      pitch_30s: p.pitch.thirtySecond,
      pitch_2m: p.pitch.twoMinute,
      judge_questions: p.pitch.judgeQA || [],
    },
    challenge_intelligence: {
      opportunities: p.research?.insights || [
        '72% of students report financial stress affecting academic performance',
        'Only 24% of students use budgeting tools consistently',
        'AI-personalized advice shows 40% better adherence than generic tools',
        'University partnerships could unlock a $2B institutional market',
      ],
    },
  };
}

// ── API ENDPOINTS ──────────────────────────────────────────────────────────

/** 1. Initialize a new project and workflow state */
export async function createProject(payload: ProjectCreatePayload): Promise<ProjectResponse> {
  return safeFetch<ProjectResponse>(
    '/projects',
    { method: 'POST', body: JSON.stringify(payload) },
    () => ({
      success: true,
      data: { project_id: 'demo-finance-001', workflow_id: 'demo-workflow-001', status: 'created' },
      message: 'Mock Project Created',
    })
  );
}

/** 2. Start workflow execution */
export async function startWorkflow(workflowId: string): Promise<any> {
  return safeFetch<any>(
    `/workflows/${workflowId}/start`,
    { method: 'POST' },
    () => ({ success: true, data: { workflow_id: workflowId, status: 'waiting_for_user' } })
  );
}

/** 3. Retrieve current progress/stage of the workflow */
export async function getWorkflowStatus(
  workflowId: string,
  currentLocalProgress?: number
): Promise<WorkflowStatusResponse> {
  return safeFetch<WorkflowStatusResponse>(
    `/workflows/${workflowId}`,
    { method: 'GET' },
    () => {
      const stages = [
        'challenge_intelligence', 'problem_analysis', 'opportunity_discovery',
        'idea_generation', 'idea_validation', 'human_selection',
      ];
      const localIdx = Math.min(Math.floor((currentLocalProgress || 0) / 16.6), stages.length - 1);
      return {
        success: true,
        data: {
          workflow_id: workflowId,
          status: localIdx >= 5 ? 'waiting_for_user' : 'running',
          current_stage: stages[localIdx],
          progress: currentLocalProgress || 0,
        },
      };
    }
  );
}

/** 4. Get the complete state of the workflow — returns ALL stage data */
export async function getWorkflowState(workflowId: string): Promise<WorkflowStateResponse> {
  return safeFetch<WorkflowStateResponse>(
    `/workflows/${workflowId}/state`,
    { method: 'GET' },
    () => ({ success: true, data: { state: buildMockState() } })
  );
}

/** 5. Fetch ideas generated for selection */
export async function getProjectIdeas(projectId: string): Promise<IdeasResponse> {
  return safeFetch<IdeasResponse>(
    `/projects/${projectId}/ideas`,
    { method: 'GET' },
    () => ({
      success: true,
      data: { ideas: DEMO_FINANCE_PROJECT.ideas, validation_reports: DEMO_FINANCE_PROJECT.ideas },
    })
  );
}

/** 6. User selects an idea and workflow resumes */
export async function selectIdea(projectId: string, ideaId: string): Promise<any> {
  return safeFetch<any>(
    `/projects/${projectId}/ideas/select`,
    { method: 'POST', body: JSON.stringify({ idea_id: ideaId }) },
    () => ({ success: true, data: { selected_idea: ideaId, workflow_status: 'completed' } })
  );
}

/** 7. Resume a paused workflow */
export async function resumeWorkflow(workflowId: string): Promise<any> {
  return safeFetch<any>(
    `/workflows/${workflowId}/resume`,
    { method: 'POST' },
    () => ({ success: true, data: { status: 'completed' } })
  );
}

/** 8. Restart a workflow from scratch */
export async function restartWorkflow(workflowId: string): Promise<any> {
  return safeFetch<any>(
    `/workflows/${workflowId}/restart`,
    { method: 'POST' },
    () => ({ success: true, data: { status: 'running' } })
  );
}

// ── Convenience endpoints ──────────────────────────────────────────────────

export async function getArchitecture(projectId: string): Promise<any> {
  return safeFetch<any>(
    `/projects/${projectId}/architecture`,
    { method: 'GET' },
    () => ({ success: true, data: { architecture: DEMO_FINANCE_PROJECT.architecture } })
  );
}

export async function getTechStack(projectId: string): Promise<any> {
  return safeFetch<any>(
    `/projects/${projectId}/tech-stack`,
    { method: 'GET' },
    () => ({ success: true, data: { tech_stack: DEMO_FINANCE_PROJECT.techStack } })
  );
}

export async function getPresentation(projectId: string): Promise<any> {
  return safeFetch<any>(
    `/projects/${projectId}/presentation`,
    { method: 'GET' },
    () => ({
      success: true,
      data: { presentation: { slides: buildMockState().presentation.slide_content } },
    })
  );
}

export async function getPitch(projectId: string): Promise<any> {
  return safeFetch<any>(
    `/projects/${projectId}/pitch`,
    { method: 'GET' },
    () => ({ success: true, data: { pitch: DEMO_FINANCE_PROJECT.pitch } })
  );
}

export async function getExports(projectId: string): Promise<any> {
  return safeFetch<any>(
    `/projects/${projectId}/exports`,
    { method: 'GET' },
    () => ({ success: true, data: { exports: { zip_url: '#', files: [] } } })
  );
}
