/**
 * exHacker API Service Client
 * Thin layer over the FastAPI backend.
 * Gracefully falls back to mock data when backend is offline.
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

interface ApiError {
  code?: string;
  message?: string;
  detail?: Record<string, unknown>;
  suggestion?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: ApiError;
}

// ── Base Request ──────────────────────────────────────────────────────────

async function request<T>(path: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL}${path}`;
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers as Record<string, string> },
      ...options,
    });
    const json = await res.json();
    if (res.ok) return json as ApiResponse<T>;

    const mock = sessionStorage.getItem('exhacker_mock');
    if (mock === 'true') {
      return { success: true, data: {} as T };
    }
    return { success: false, data: {} as T, error: json };
  } catch {
    return { success: true, data: {} as T };
  }
}

// ── Projects ──────────────────────────────────────────────────────────────

export interface ProjectData {
  project: Project;
}

export interface ProjectListData {
  projects: Project[];
}

export async function createProject(idea: string): Promise<ApiResponse<ProjectData>> {
  const res = await request<ProjectData>('/projects', {
    method: 'POST',
    body: JSON.stringify({ idea }),
  });
  if (res.success) return res;
  return {
    success: true,
    data: {
      project: {
        id: 'mock-' + Date.now(),
        name: idea.slice(0, 40),
        description: null,
        idea,
        status: 'draft',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    },
  };
}

export async function getProject(id: string): Promise<ApiResponse<ProjectData>> {
  const res = await request<ProjectData>(`/projects/${id}`);
  if (res.success) return res;
  return {
    success: true,
    data: {
      project: {
        id, name: 'Demo Project', description: null,
        idea: 'A sample project idea for demo purposes',
        status: 'draft',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    },
  };
}

export async function listProjects(): Promise<ApiResponse<ProjectListData>> {
  const res = await request<ProjectListData>('/projects');
  if (res.success) return res;
  return { success: true, data: { projects: [] } };
}

// ── Research (legacy 4-category) ──────────────────────────────────────────

export interface ResearchData {
  summary: {
    total_results: number;
    competitors_found: number;
    apis_found: number;
    oss_found: number;
    insights_found: number;
    cached: boolean;
  };
  competitors: ResearchItemLegacy[];
  apis: ResearchItemLegacy[];
  oss_projects: ResearchItemLegacy[];
  insights: ResearchItemLegacy[];
}

export interface ResearchItemLegacy {
  title: string;
  url: string | null;
  snippet: string | null;
  relevance_score: number | null;
  result_type: string;
}

function getMockResearchData(): ResearchData {
  return {
    summary: { total_results: 3, competitors_found: 3, apis_found: 0, oss_found: 0, insights_found: 0, cached: false },
    competitors: [
      { title: 'YNAB', url: 'https://ynab.com', snippet: 'Popular budgeting app for students', relevance_score: 0.9, result_type: 'competitor' },
      { title: 'Mint', url: 'https://mint.intuit.com', snippet: 'Free personal finance tracking', relevance_score: 0.85, result_type: 'competitor' },
      { title: 'PocketGuard', url: 'https://pocketguard.com', snippet: 'Simplified budgeting for beginners', relevance_score: 0.7, result_type: 'competitor' },
    ],
    apis: [], oss_projects: [], insights: [],
  };
}

export async function startResearch(projectId: string): Promise<ApiResponse<ResearchData>> {
  const res = await request<ResearchData>('/projects/' + projectId + '/research', { method: 'POST' });
  if (res.success) return res;
  return { success: true, data: getMockResearchData() };
}

export async function getResearch(projectId: string): Promise<ApiResponse<ResearchData>> {
  const res = await request<ResearchData>('/projects/' + projectId + '/research');
  if (res.success) return res;
  return { success: true, data: getMockResearchData() };
}

// ── S2 Research (10-category format) ─────────────────────────────────────────

export interface ResearchCategory {
  id: string;
  label: string;
  count: number;
  items: ResearchItem2[];
}

export interface ResearchItem2 {
  id: string;
  title: string;
  url: string | null;
  snippet: string | null;
  result_type: string;
  category: string;
  confidence: number | null;
  freshness: string | null;
  relevance: string | null;
  relevance_score: number | null;
  source: string | null;
}

export interface ResearchSynthesis {
  synthesis: {
    summary: string;
    key_opportunities: string[];
    critical_gaps: string[];
    competitor_landscape: string;
  } | null;
  categories: { category: string; summary: string; actionable_insight: string; gap_identified: string }[] | null;
  technology_recommendations: { technology: string; why: string; confidence: string; appears_in_results: number }[] | null;
  differentiation_opportunities: { area: string; current_state: string; opportunity: string }[] | null;
  risks_from_research: { risk: string; evidence: string }[] | null;
  recommended_priorities: string[] | null;
}

export interface ResearchData2 {
  summary: {
    total_results: number;
    categories_found: number;
    categories: ResearchCategory[];
    cached: boolean;
  };
  synthesis: ResearchSynthesis | null;
}

function getMockS2ResearchData(): ResearchData2 {
  const items = (cats: { id: string; label: string; items: { title: string; snippet: string; confidence: number }[] }) => ({
    id: cats.id, label: cats.label, count: cats.items.length,
    items: cats.items.map((item, i) => ({
      id: `${cats.id}-${i}`, title: item.title, url: null, snippet: item.snippet,
      result_type: cats.id, category: cats.id, confidence: item.confidence,
      freshness: 'weeks', relevance: item.confidence >= 0.8 ? 'high' : 'medium',
      relevance_score: item.confidence, source: 'mock',
    })),
  });

  const allCats = [
    items({ id: 'product', label: 'Existing Products', items: [
      { title: 'YNAB', snippet: 'Leading personal budgeting app with envelope methodology', confidence: 0.92 },
      { title: 'Mint', snippet: 'Free personal finance app with bank integration', confidence: 0.88 },
      { title: 'PocketGuard', snippet: 'Simplified budgeting for younger users', confidence: 0.75 },
    ]}),
    items({ id: 'api', label: 'APIs & SDKs', items: [
      { title: 'Plaid API', snippet: 'Banking API connecting to 12k+ financial institutions', confidence: 0.95 },
      { title: 'Finicity', snippet: 'Open banking platform with account aggregation', confidence: 0.82 },
      { title: 'Teller API', snippet: 'Modern banking API with read/write access', confidence: 0.78 },
    ]}),
    items({ id: 'hackathon_winner', label: 'Hackathon Winners', items: [
      { title: 'Penny AI (TreeHacks 2024)', snippet: 'AI-powered budgeting coach', confidence: 0.85 },
      { title: 'SaveMate (HackMIT 2025)', snippet: 'Social savings with accountability groups', confidence: 0.80 },
    ]}),
    items({ id: 'trend', label: 'Industry Trends', items: [
      { title: 'Gen Z Finance Preferences', snippet: '73% of Gen Z prefer AI-powered budgeting', confidence: 0.70 },
    ]}),
    items({ id: 'oss', label: 'Open Source', items: [
      { title: 'Actual Budget', snippet: 'Open-source finance tool with 15k+ GitHub stars', confidence: 0.88 },
    ]}),
  ];

  return {
    summary: { total_results: 11, categories_found: 5, categories: allCats, cached: false },
    synthesis: {
      synthesis: {
        summary: 'The student budgeting space is competitive but fragmented. Major players target older demographics, leaving Gen Z underserved.',
        key_opportunities: ['AI-powered coaching (not just tracking)', 'Social accountability groups', 'Gamification mechanics', 'Simplified student-focused UX'],
        critical_gaps: ['No app combines AI coaching with social accountability', 'Existing apps feel judgmental', 'Student-specific features underserved'],
        competitor_landscape: 'Fragmented market with incumbents losing relevance with Gen Z.',
      },
      categories: [{ category: 'existing_products', summary: 'Products focus on tracking not coaching', actionable_insight: 'Differentiate through AI coaching', gap_identified: 'No personalized coaching for students' }],
      technology_recommendations: [{ technology: 'Plaid API', why: 'Industry standard for bank connectivity', confidence: 'high', appears_in_results: 5 }],
      differentiation_opportunities: [{ area: 'AI Coaching', current_state: 'Apps show data but dont advise', opportunity: 'Build an AI coach for personalized advice' }],
      risks_from_research: [{ risk: 'Plaid API dependency', evidence: '3 of 3 APIs found are Plaid' }],
      recommended_priorities: ['Build AI coaching loop', 'Integrate Plaid', 'Add social accountability', 'Target Gen Z UX'],
    },
  };
}

export async function startResearchV2(projectId: string): Promise<ApiResponse<ResearchData2>> {
  try {
    const url = `${API_BASE_URL}/projects/${projectId}/research`;
    const res = await fetch(url, { method: 'POST' });
    if (res.ok) {
      const data = await res.json();
      if (data?.data?.summary?.categories) {
        return { success: true, data: data.data };
      }
    }
  } catch { /* fallback to mock */ }
  return { success: true, data: getMockS2ResearchData() };
}

// ── Challenge Intelligence ────────────────────────────────────────────────

export interface ChallengeData {
  executive_summary: string;
  core_problem: { problem: string; who_experiences: string; why_important: string };
  hidden_problems: string[];
  stakeholders: { role: string; description: string }[];
  constraints: { type: string; description: string }[];
  success_criteria: { criterion: string; weight: number; description: string }[];
  opportunity_areas: string[];
  innovation_opportunities: { area: string; description: string }[];
  risk_areas: { area: string; severity: string; description: string }[];
  difficulty: { technical: number | null; research: number | null; demo: number | null; judge: number | null; overall: number | null };
  recommended_strategy: string;
  themes: string[];
  keywords: string[];
  confidence: number;
  model_used: string;
}

function getMockChallengeData(): ChallengeData {
  return {
    executive_summary: 'This challenge asks teams to build a financial literacy tool. The organizers want behavioral change, not just tracking.',
    core_problem: { problem: 'College students lack financial literacy skills leading to long-term debt.', who_experiences: 'Students aged 18-24', why_important: 'Financial habits formed in college persist into adulthood.' },
    hidden_problems: ['Students are embarrassed to ask for financial help', 'Existing apps feel judgmental'],
    stakeholders: [
      { role: 'Primary users', description: 'College students managing limited budgets' },
      { role: 'Judges', description: 'Looking for innovation + AI application' },
    ],
    constraints: [{ type: 'time', description: '48 hours for a working prototype' }],
    success_criteria: [{ criterion: 'Problem relevance', weight: 25, description: 'Does it actually address student struggles?' }],
    opportunity_areas: ['Behavioral economics', 'Gamification', 'AI coaching'],
    innovation_opportunities: [{ area: 'Behavioral AI', description: 'AI that detects patterns and delivers personalized nudges' }],
    risk_areas: [{ area: 'Scope creep', severity: 'high', description: 'Teams try to build too much' }],
    difficulty: { technical: 65, research: 40, demo: 55, judge: 60, overall: 55 },
    recommended_strategy: 'Focus on a single user journey. Build the core loop: data → AI analysis → actionable insight.',
    themes: ['financial literacy', 'AI coaching', 'student wellness'],
    keywords: ['budgeting', 'AI', 'students', 'finance'],
    confidence: 0.92,
    model_used: 'glm-5.2',
  };
}

export async function analyzeChallenge(projectId: string): Promise<ApiResponse<ChallengeData>> {
  const res = await request<ChallengeData>('/projects/' + projectId + '/challenge', { method: 'POST' });
  if (res.success) return res;
  return { success: true, data: getMockChallengeData() };
}

export async function getChallengeAnalysis(projectId: string): Promise<ApiResponse<ChallengeData>> {
  const res = await request<ChallengeData>('/projects/' + projectId + '/challenge');
  if (res.success) return res;
  return { success: true, data: getMockChallengeData() };
}

// ── Competitor Intelligence (S3) ──────────────────────────────────────────

export interface CompetitorProfile {
  name: string;
  description: string;
  target_users: string;
  strengths: string[];
  weaknesses: string[];
  tech_stack: string[];
  business_model: string;
  missing_features: string[];
  innovation_level: number;
  market_maturity: string;
  last_activity: string;
}

export interface ComparisonRow {
  dimension: string;
  scores: Record<string, number>;
}

export interface GapAnalysis {
  patterns: string[];
  white_space: string[];
  pain_points: string[];
  hackathon_opportunities: string[];
  oversaturated: string[];
  to_avoid: string[];
}

export interface Opportunity {
  title: string;
  difficulty: number;
  impact: number;
  judge_appeal: number;
  effort_hours: number;
}

export interface InnovationBreakdown {
  market_saturation: number;
  technical_novelty: number;
  execution_feasibility: number;
  judge_memorability: number;
  business_potential: number;
}

export interface Warning {
  warning: string;
  why: string;
  alternative: string;
}

export interface CompetitorData {
  summary: string;
  landscape_summary: string;
  competitors: CompetitorProfile[];
  comparison_matrix: ComparisonRow[];
  gap_analysis: GapAnalysis;
  quick_wins: Opportunity[];
  medium_innovations: Opportunity[];
  moonshots: Opportunity[];
  innovation_score: number | null;
  innovation_breakdown: InnovationBreakdown;
  warnings: Warning[];
  keywords: string[];
  themes: string[];
  confidence: number;
  model_used: string;
}

function getMockCompetitorData(): CompetitorData {
  return {
    summary: 'The student budgeting space is moderately competitive with 3 direct competitors.',
    landscape_summary: 'Fragmented market dominated by YNAB, Mint, and PocketGuard.',
    competitors: [
      { name: 'YNAB', description: 'Zero-based budgeting', target_users: 'Adults 25-45', strengths: ['Proven methodology'], weaknesses: ['No AI features'], tech_stack: ['React', 'Rails', 'PostgreSQL'], business_model: 'Subscription', missing_features: ['AI coaching'], innovation_level: 45, market_maturity: 'mature', last_activity: 'Monthly' },
      { name: 'Mint', description: 'Free finance tracker', target_users: 'Consumers 20-50', strengths: ['Free', 'Bank integration'], weaknesses: ['Cluttered UI'], tech_stack: ['React', 'Java', 'MySQL'], business_model: 'Free', missing_features: ['AI coaching'], innovation_level: 35, market_maturity: 'mature', last_activity: 'Quarterly' },
      { name: 'PocketGuard', description: 'Simplified budgeting', target_users: 'Beginners 18-30', strengths: ['Simple UX'], weaknesses: ['Limited features'], tech_stack: ['React Native', 'Node.js', 'MongoDB'], business_model: 'Freemium', missing_features: ['AI coaching'], innovation_level: 50, market_maturity: 'growing', last_activity: '2 months ago' },
    ],
    comparison_matrix: [
      { dimension: 'Innovation', scores: { YNAB: 45, Mint: 35, PocketGuard: 50 } },
      { dimension: 'UX Quality', scores: { YNAB: 70, Mint: 50, PocketGuard: 75 } },
      { dimension: 'AI Usage', scores: { YNAB: 10, Mint: 15, PocketGuard: 20 } },
    ],
    gap_analysis: {
      patterns: ['All focus on tracking not behavior change', 'AI features minimal', 'Social accountability absent'],
      white_space: ['AI-powered coaching', 'Social accountability', 'Emotional spending'],
      pain_points: ['Users feel judged', 'Budgeting is a chore', 'Students priced out'],
      hackathon_opportunities: ['AI coaching prototype', 'Social saving challenge', 'Gen Z UX'],
      oversaturated: ['Basic trackers', 'Manual entry'],
      to_avoid: ['General budgeting app', 'Complex integrations', 'Student subscriptions'],
    },
    quick_wins: [
      { title: 'AI spending chat', difficulty: 30, impact: 85, judge_appeal: 90, effort_hours: 4 },
      { title: 'Saving challenge', difficulty: 25, impact: 75, judge_appeal: 80, effort_hours: 3 },
    ],
    medium_innovations: [
      { title: 'Emotional spending', difficulty: 55, impact: 80, judge_appeal: 85, effort_hours: 12 },
    ],
    moonshots: [
      { title: 'Full AI coach', difficulty: 85, impact: 95, judge_appeal: 95, effort_hours: 40 },
    ],
    innovation_score: 82,
    innovation_breakdown: { market_saturation: 65, technical_novelty: 78, execution_feasibility: 72, judge_memorability: 85, business_potential: 70 },
    warnings: [
      { warning: 'Plaid dependency', why: 'Banking APIs need partnerships', alternative: 'Mock data for prototype' },
    ],
    keywords: ['fintech', 'budgeting', 'AI coaching'],
    themes: ['financial literacy', 'AI'],
    confidence: 0.85,
    model_used: 'glm-5.2',
  };
}

export async function analyzeCompetitors(projectId: string): Promise<ApiResponse<CompetitorData>> {
  try {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/competitors`, { method: 'POST' });
    if (res.ok) { const d = await res.json(); if (d?.data?.competitors) return { success: true, data: d.data }; }
  } catch { /* fallback */ }
  return { success: true, data: getMockCompetitorData() };
}

export async function getCompetitorAnalysis(projectId: string): Promise<ApiResponse<CompetitorData>> {
  try {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/competitors`);
    if (res.ok) { const d = await res.json(); if (d?.data) return { success: true, data: d.data }; }
  } catch { /* fallback */ }
  return { success: true, data: getMockCompetitorData() };
}

// ── Directions ──────────────────────────────────────────────────────────

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
  const base = { project_id: '', description: null, elevator_pitch: null, problem_statement: null, solution: null, differentiation: null, core_features: null, stretch_features: null, risks: null, estimated_effort_hours: null, created_at: new Date().toISOString() };
  return [
    { ...base, id: 'md1', title: 'AI Finance Coach', tagline: 'Personalized AI advisor', scores: { innovation: 92, creativity: 85, technical_depth: 78, feasibility: 70, demo_potential: 88, judge_appeal: 85, business_potential: 75, overall: 82 }, is_selected: false },
    { ...base, id: 'md2', title: 'Gamified Savings', tagline: 'Turn saving into a game', scores: { innovation: 85, creativity: 90, technical_depth: 65, feasibility: 78, demo_potential: 82, judge_appeal: 80, business_potential: 70, overall: 79 }, is_selected: false },
    { ...base, id: 'md3', title: 'Financial Habit Builder', tagline: 'Micro-habit coaching', scores: { innovation: 78, creativity: 82, technical_depth: 72, feasibility: 85, demo_potential: 75, judge_appeal: 78, business_potential: 65, overall: 76 }, is_selected: false },
  ];
}

export async function generateDirections(projectId: string): Promise<ApiResponse<{ directions: Direction[] }>> {
  const res = await request<{ directions: Direction[] }>('/projects/' + projectId + '/directions', { method: 'POST' });
  if (res.success) return res;
  return { success: true, data: { directions: getMockDirections() } };
}

export async function getDirections(projectId: string): Promise<ApiResponse<{ directions: Direction[] }>> {
  const res = await request<{ directions: Direction[] }>('/projects/' + projectId + '/directions');
  if (res.success) return res;
  return { success: true, data: { directions: getMockDirections() } };
}

export async function selectDirection(projectId: string, directionId: string): Promise<ApiResponse<{ direction: Direction }>> {
  const res = await request<{ direction: Direction }>('/projects/' + projectId + '/directions/' + directionId + '/select', { method: 'POST' });
  if (res.success) return res;
  return { success: true, data: { direction: getMockDirections().find(d => d.id === directionId) || getMockDirections()[0] } };
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

function getMockBlueprint(): BlueprintData {
  return {
    summary: { components: 4, entities: 4, endpoints: 28, tasks: 32, estimated_hours: 78, has_tech_stack: true },
    tech_stack: { project_type: 'mobile_app', frontend: { framework: 'React Native' }, backend: { framework: 'FastAPI' }, database: { database: 'PostgreSQL' } },
    architecture: { components: [{ name: 'Mobile App', description: 'React Native app', tech: 'React Native' }, { name: 'Backend API', description: 'FastAPI server', tech: 'FastAPI' }, { name: 'Database', description: 'PostgreSQL', tech: 'PostgreSQL' }, { name: 'Auth', description: 'Authentication service', tech: 'NextAuth.js' }] },
    data_model: { entities: [{ name: 'user', fields: [{ name: 'id', type: 'UUID' }, { name: 'email', type: 'string' }] }, { name: 'budget', fields: [{ name: 'id', type: 'UUID' }, { name: 'limit', type: 'decimal' }] }] },
    api_contracts: { endpoints: [{ method: 'GET', path: '/users', description: 'List users' }, { method: 'POST', path: '/budgets', description: 'Create budget' }] },
    plan: { phases: [{ name: 'Foundation', tasks: [{ title: 'Initialize project', estimated_hours: 2 }] }], total_tasks: 32, estimated_hours: 78 },
    generated_at: new Date().toISOString(),
  };
}

export async function generateBlueprint(projectId: string): Promise<ApiResponse<{ blueprint: BlueprintData }>> {
  const res = await request<{ blueprint: BlueprintData }>('/projects/' + projectId + '/blueprint', { method: 'POST' });
  if (res.success) return res;
  return { success: true, data: { blueprint: getMockBlueprint() } };
}

// ── Export ────────────────────────────────────────────────────────────────

export async function downloadExport(projectId: string, format: 'markdown' | 'json' = 'markdown'): Promise<void> {
  const url = `${API_BASE_URL}/projects/${projectId}/export/download?format=${format}`;
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error('Export failed');
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `blueprint.${format === 'json' ? 'json' : 'md'}`;
    a.click();
    URL.revokeObjectURL(a.href);
  } catch {
    const content = format === 'json' ? JSON.stringify(getMockBlueprint(), null, 2) : '# Project Blueprint\n\nMock export';
    const blob = new Blob([content], { type: format === 'json' ? 'application/json' : 'text/markdown' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `blueprint.${format === 'json' ? 'json' : 'md'}`;
    a.click();
    URL.revokeObjectURL(a.href);
  }
}
