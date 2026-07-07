/**
 * exHacker API Service Client
 * Thin layer over the FastAPI backend.
 * G racefully falls back to mock data when backend is offline.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ── Types ──────────────────────────────────────────────────────────────────

export interface Project {
  id: string;
  name: string;
  description: string | null;
  idea: string;
  status: 'draft' | 'processing' | 'ready' | 'archived';
  created_at: string;
  updated_at: string;
}

export interface CreateProjectPayload {
  idea: string;
  name?: string;
  description?: string;
}

export interface UpdateProjectPayload {
  name?: string;
  description?: string;
  idea?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    detail?: Record<string, unknown>;
    suggestion?: string;
  };
}

// ── Client ─────────────────────────────────────────────────────────────────

async function request<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });

    const body = await res.json();

    if (!res.ok) {
      console.error(`[exHacker API] ${endpoint} failed:`, body);
    }

    return body as ApiResponse<T>;
  } catch (err) {
    console.error(`[exHacker API] Network error on ${endpoint}:`, err);
    return {
      success: false,
      data: null as unknown as T,
      error: {
        code: 'NETWORK_ERROR',
        message: 'Could not reach the backend.',
        suggestion: 'Make sure the backend is running on port 8000.',
      },
    };
  }
}

// ── Mock Data (for development without backend) ───────────────────────────

const MOCK_PROJECTS: Project[] = [
  {
    id: 'mock-001',
    name: 'Student Budget AI',
    description: null,
    idea: 'A mobile app that helps students budget their money using AI',
    status: 'draft',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

let mockIdCounter = 1;

function createMockProject(payload: CreateProjectPayload): Project {
  const project: Project = {
    id: `mock-${String(++mockIdCounter).padStart(3, '0')}`,
    name: payload.name || payload.idea.slice(0, 60) + (payload.idea.length > 60 ? '...' : ''),
    description: payload.description || null,
    idea: payload.idea,
    status: 'draft',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
  MOCK_PROJECTS.unshift(project);
  return project;
}

// ── Endpoints ──────────────────────────────────────────────────────────────

export async function createProject(
  payload: CreateProjectPayload,
): Promise<ApiResponse<{ project: Project }>> {
  const res = await request<{ id: string; name: string; description: string | null; idea: string; status: string; created_at: string; updated_at: string }>(
    '/projects',
    { method: 'POST', body: JSON.stringify(payload) },
  );

  if (res.success) {
    return {
      ...res,
      data: { project: res.data as unknown as Project },
    };
  }

  // Fallback to mock
  console.warn('[exHacker API] Using mock project creation');
  const mockProject = createMockProject(payload);
  return {
    success: true,
    data: { project: mockProject },
    message: 'Mock project created.',
  };
}

export async function listProjects(): Promise<ApiResponse<{ projects: Project[] }>> {
  const res = await request<{ projects: Project[] }>('/projects');

  if (res.success) {
    return res;
  }

  // Fallback to mock
  console.warn('[exHacker API] Using mock project list');
  return {
    success: true,
    data: { projects: MOCK_PROJECTS },
    message: 'Mock projects (backend offline).',
  };
}

export async function getProject(
  id: string,
): Promise<ApiResponse<{ project: Project }>> {
  const res = await request<Project>('/projects/' + id);

  if (res.success) {
    return { ...res, data: { project: res.data as unknown as Project } };
  }

  // Fallback to mock
  const mock = MOCK_PROJECTS.find((p) => p.id === id);
  if (mock) {
    return { success: true, data: { project: mock } };
  }

  return {
    success: false,
    data: null as unknown as { project: Project },
    error: { code: 'PROJECT_NOT_FOUND', message: 'Project not found.' },
  };
}

export async function deleteProject(id: string): Promise<ApiResponse<null>> {
  return request<null>('/projects/' + id, { method: 'DELETE' });
}

export async function transitionProject(
  id: string,
  transition: string,
): Promise<ApiResponse<{ id: string; status: string; message: string }>> {
  return request<{ id: string; status: string; message: string }>(
    '/projects/' + id + '/transition',
    { method: 'POST', body: JSON.stringify({ transition }) },
  );
}

// ── Research ────────────────────────────────────────────────────────────────

export interface ResearchResult {
  title: string;
  url: string | null;
  snippet: string | null;
  relevance_score: number | null;
  result_type: string;
}

export interface ResearchData {
  summary: {
    total_results: number;
    competitors_found: number;
    apis_found: number;
    oss_found: number;
    insights_found: number;
    cached: boolean;
  };
  competitors: ResearchResult[];
  apis: ResearchResult[];
  oss_projects: ResearchResult[];
  insights: ResearchResult[];
}

function getMockResearchData(): ResearchData {
  return {
    summary: { total_results: 5, competitors_found: 3, apis_found: 1, oss_found: 1, insights_found: 0, cached: false },
    competitors: [
      { title: 'YNAB (You Need A Budget)', url: 'https://www.ynab.com', snippet: 'Popular budgeting app with envelope-based system. Premium subscription model.', relevance_score: 0.92, result_type: 'competitor' },
      { title: 'Mint / Credit Karma', url: 'https://mint.intuit.com', snippet: 'Free personal finance tracking app. Connects to bank accounts automatically.', relevance_score: 0.88, result_type: 'competitor' },
      { title: 'PocketGuard', url: 'https://pocketguard.com', snippet: 'Budgeting app focused on how much spendable money you have left.', relevance_score: 0.75, result_type: 'competitor' },
    ],
    apis: [
      { title: 'Plaid API', url: 'https://plaid.com', snippet: 'Financial institution data aggregation API. Connects to 12,000+ institutions.', relevance_score: 0.95, result_type: 'api' },
    ],
    oss_projects: [
      { title: 'Firefly III', url: 'https://github.com/firefly-iii/firefly-iii', snippet: 'Self-hosted personal finance manager. PHP/Laravel, REST API.', relevance_score: 0.7, result_type: 'oss' },
    ],
    insights: [],
  };
}

export async function startResearch(
  projectId: string,
): Promise<ApiResponse<ResearchData>> {
  const res = await request<ResearchData>(
    '/projects/' + projectId + '/research',
    { method: 'POST' },
  );
  if (res.success) return res;
  console.warn('[exHacker API] Using mock research data');
  return { success: true, data: getMockResearchData() };
}

export async function getResearch(
  projectId: string,
): Promise<ApiResponse<ResearchData>> {
  const res = await request<ResearchData>(
    '/projects/' + projectId + '/research',
  );
  if (res.success) return res;
  return { success: true, data: getMockResearchData() };
}

// ── Directions ──────────────────────────────────────────────────────────────

export interface Direction {
  id: string;
  project_id: string;
  title: string;
  tagline: string;
  description: string | null;
  elevator_pitch: string | null;
  problem_statement: string | null;
  solution: string | null;
  differentiation: string | null;
  core_features: string[] | null;
  stretch_features: string[] | null;
  risks: { title: string; severity: string; mitigation: string }[] | null;
  scores: {
    innovation: number | null;
    creativity: number | null;
    technical_depth: number | null;
    feasibility: number | null;
    demo_potential: number | null;
    judge_appeal: number | null;
    business_potential: number | null;
    overall: number | null;
  } | null;
  estimated_effort_hours: number | null;
  is_selected: boolean;
  created_at: string;
}

function getMockDirections(): Direction[] {
  return [
    { id: 'mock-dir-1', project_id: '', title: 'AI Finance Coach', tagline: 'Personalized AI advisor that learns spending patterns', description: 'An intelligent budgeting coach that analyzes spending habits.', elevator_pitch: 'Get personalized financial coaching that learns your habits.', problem_statement: 'Students struggle to manage finances without guidance.', solution: 'AI coach that learns spending patterns and provides personalized advice.', differentiation: 'Truly personalized — adapts to individual behavior over time.', core_features: ['Spending analysis', 'Personalized insights', 'Goal tracking'], stretch_features: ['Community challenges', 'Bank integration'], risks: [{ title: 'Data privacy', severity: 'medium', mitigation: 'Local-first data processing' }], scores: { innovation: 92, creativity: 85, technical_depth: 78, feasibility: 70, demo_potential: 88, judge_appeal: 85, business_potential: 75, overall: 82 }, estimated_effort_hours: 28, is_selected: false, created_at: new Date().toISOString() },
    { id: 'mock-dir-2', project_id: '', title: 'Gamified Savings Platform', tagline: 'Turn saving into a competitive social game', description: 'A social savings platform where users compete in saving challenges.', elevator_pitch: 'Make saving money as addictive as a game.', problem_statement: 'Students find saving boring and lack motivation.', solution: 'Gamified savings with challenges, badges, and social competition.', differentiation: 'First savings app that makes saving genuinely fun.', core_features: ['Savings challenges', 'Leaderboards', 'Badges'], stretch_features: ['Group challenges', 'Reward marketplace'], risks: [{ title: 'Superficial gamification', severity: 'medium', mitigation: 'Partner with behavioral psychologists' }], scores: { innovation: 85, creativity: 90, technical_depth: 65, feasibility: 78, demo_potential: 82, judge_appeal: 80, business_potential: 70, overall: 79 }, estimated_effort_hours: 24, is_selected: false, created_at: new Date().toISOString() },
    { id: 'mock-dir-3', project_id: '', title: 'Financial Habit Builder', tagline: 'Micro-habit coaching with AI nudges', description: 'Build better financial habits through micro-actions and AI-powered nudges.', elevator_pitch: 'Build better money habits one micro-action at a time.', problem_statement: 'Behavior change is hard without consistent reinforcement.', solution: 'AI-powered micro-habit coaching with smart notifications.', differentiation: 'Focus on habit formation rather than tracking.', core_features: ['Micro-habits', 'AI nudges', 'Progress tracking'], stretch_features: ['Spending insights', 'Habit streaks'], risks: [{ title: 'User fatigue', severity: 'high', mitigation: 'Adaptive notification frequency' }], scores: { innovation: 78, creativity: 82, technical_depth: 72, feasibility: 85, demo_potential: 75, judge_appeal: 78, business_potential: 65, overall: 76 }, estimated_effort_hours: 20, is_selected: false, created_at: new Date().toISOString() },
  ];
}

export async function generateDirections(projectId: string): Promise<ApiResponse<{ directions: Direction[] }>> {
  const res = await request<{ directions: Direction[] }>('/projects/' + projectId + '/directions', { method: 'POST' });
  if (res.success) return res;
  console.warn('[exHacker API] Using mock directions');
  return { success: true, data: { directions: getMockDirections() } };
}

export async function getDirections(projectId: string): Promise<ApiResponse<{ directions: Direction[] }>> {
  const res = await request<{ directions: Direction[] }>('/projects/' + projectId + '/directions');
  if (res.success) return res;
  return { success: true, data: { directions: [] } };
}

export async function selectDirection(projectId: string, directionId: string): Promise<ApiResponse<{ direction: Direction }>> {
  const res = await request<{ direction: Direction }>('/projects/' + projectId + '/directions/' + directionId + '/select', { method: 'POST' });
  if (res.success) return res;
  // In mock mode, mark the direction as selected
  const dirs = getMockDirections().map(d => ({ ...d, id: directionId, is_selected: d.id === directionId }));
  return { success: true, data: { direction: dirs.find(d => d.id === directionId) || dirs[0] } };
}

// ── Blueprint ────────────────────────────────────────────────────────────────

export interface BlueprintData {
  summary: { components: number; entities: number; endpoints: number; tasks: number; estimated_hours: number; has_tech_stack: boolean };
  tech_stack: Record<string, unknown> | null;
  architecture: Record<string, unknown> | null;
  data_model: Record<string, unknown> | null;
  api_contracts: Record<string, unknown> | null;
  plan: Record<string, unknown> | null;
  generated_at: string;
}

export async function generateBlueprint(projectId: string): Promise<ApiResponse<{ blueprint: BlueprintData }>> {
  const res = await request<{ blueprint: BlueprintData }>('/projects/' + projectId + '/blueprint', { method: 'POST' });
  if (res.success) return res;
  return { success: true, data: { blueprint: getMockBlueprint() } };
}

export function getMockBlueprint(): BlueprintData {
  return {
    summary: { components: 4, entities: 4, endpoints: 28, tasks: 32, estimated_hours: 78, has_tech_stack: true },
    tech_stack: { project_type: 'web_app', frontend: { framework: 'Next.js' }, backend: { framework: 'FastAPI' }, database: { database: 'PostgreSQL' } },
    architecture: { components: [
      { name: 'Frontend', description: 'Web application', tech: 'Next.js', sub_components: ['Pages', 'Components', 'State'] },
      { name: 'Backend', description: 'API server', tech: 'FastAPI', sub_components: ['Routes', 'Services', 'Models'] },
      { name: 'Database', description: 'Data storage', tech: 'PostgreSQL', sub_components: ['Tables', 'Migrations'] },
    ]},
    data_model: { entities: [
      { name: 'user', fields: [{ name: 'id', type: 'UUID' }, { name: 'email', type: 'string' }] },
      { name: 'budget', fields: [{ name: 'id', type: 'UUID' }, { name: 'category', type: 'string' }, { name: 'limit', type: 'decimal' }] },
    ]},
    api_contracts: { endpoints: [
      { method: 'GET', path: '/users', description: 'List users' },
      { method: 'POST', path: '/users', description: 'Create user' },
    ]},
    plan: { phases: [{ name: 'Foundation', tasks: [{ title: 'Initialize project', estimated_hours: 1 }] }], total_tasks: 32, estimated_hours: 78 },
    generated_at: new Date().toISOString(),
  };
}

// ── Export ───────────────────────────────────────────────────────────────────

export async function downloadExport(projectId: string, format: 'markdown' | 'json' = 'markdown'): Promise<void> {
  const url = `${API_BASE_URL}/projects/${projectId}/export/download?format=${format}`;
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error('Export failed');
    const blob = await res.blob();
    const ext = format === 'json' ? 'json' : 'md';
    const filename = `blueprint.${ext}`;
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  } catch {
    // Fallback: generate mock download
    const content = format === 'json'
      ? JSON.stringify(getMockBlueprint(), null, 2)
      : `# Project Blueprint\n\nAuto-generated by exHacker (mock mode)`;
    const blob = new Blob([content], { type: format === 'json' ? 'application/json' : 'text/markdown' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `blueprint.${format === 'json' ? 'json' : 'md'}`;
    a.click();
    URL.revokeObjectURL(a.href);
  }
}
