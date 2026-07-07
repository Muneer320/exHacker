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
  if (res.success && (res.data as any).project) return res;
  // Backend returns data directly, wrap in { project }
  if (res.success && (res.data as any).id) {
    return { success: true, data: { project: res.data as unknown as Project } };
  }
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
  if (res.success && (res.data as any).project) return res;
  if (res.success && (res.data as any).id) {
    return { success: true, data: { project: res.data as unknown as Project } };
  }
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

// ── Shared Intelligence (Bible §7) ──────────────────────────────────────────

export interface SharedMemoryEntry {
  id: string;
  project_id: string;
  specialist: string;
  memory_type: string;
  version: number;
  content: Record<string, unknown>;
  confidence: number | null;
  references: string[];
  model_used: string | null;
  is_active: boolean;
  created_at: string;
}

export interface DecisionEntry {
  id: string;
  project_id: string;
  entry_number: number;
  title: string;
  category: string;
  description: string;
  rationale: string | null;
  alternatives_considered: { title: string; pros: string[]; cons: string[] }[];
  confidence: number | null;
  originating_specialist: string;
  references: string[];
  status: 'proposed' | 'accepted' | 'rejected' | 'superseded' | 'needs_review';
  superseded_by: string | null;
  created_at: string;
  updated_at: string;
}

const CATEGORY_LABELS: Record<string, string> = {
  opportunity_selected: '🎯 Opportunity Selected',
  direction_rejected: '❌ Direction Rejected',
  tech_chosen: '⚙️ Technology Chosen',
  architecture_tradeoff: '🏗️ Architecture Tradeoff',
  research_finding: '🔬 Research Finding',
  risk_accepted: '⚠️ Risk Accepted',
  feature_scoped: '📐 Feature Scoped',
  specialist_review: '🧠 Specialist Review',
  direction_generated: '💡 Direction Generated',
};

function getMockSharedData(): { memory: SharedMemoryEntry[]; decisions: DecisionEntry[] } {
  return {
    memory: [
      {
        id: 'mem-1', project_id: '', specialist: 'challenge_analyst', memory_type: 'challenge_intelligence',
        version: 1, content: { executive_summary: 'Build a financial literacy tool for students' },
        confidence: 0.92, references: [], model_used: 'glm-5.2', is_active: true, created_at: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        id: 'mem-2', project_id: '', specialist: 'research_specialist', memory_type: 'research_report',
        version: 1, content: { summary: 'Found 12 relevant results across 7 categories' },
        confidence: 0.85, references: ['mem-1'], model_used: 'deepseek-v4-flash', is_active: true, created_at: new Date(Date.now() - 1800000).toISOString(),
      },
      {
        id: 'mem-3', project_id: '', specialist: 'competitor_analyst', memory_type: 'competitor_intelligence',
        version: 1, content: { landscape_summary: '3 direct competitors identified' },
        confidence: 0.88, references: ['mem-1', 'mem-2'], model_used: 'glm-5.2', is_active: true, created_at: new Date(Date.now() - 600000).toISOString(),
      },
    ],
    decisions: [
      {
        id: 'dec-1', project_id: '', entry_number: 1, title: 'Challenge analyzed', category: 'specialist_review',
        description: 'Challenge Intelligence completed for the project.',
        rationale: null, alternatives_considered: [], confidence: 0.92, originating_specialist: 'challenge_analyst',
        references: ['mem-1'], status: 'accepted', superseded_by: null,
        created_at: new Date(Date.now() - 3500000).toISOString(),
        updated_at: new Date(Date.now() - 3500000).toISOString(),
      },
      {
        id: 'dec-2', project_id: '', entry_number: 2, title: 'Research completed', category: 'research_finding',
        description: 'Found 12 results: 3 competitors, 3 APIs, 2 hackathon winners, 2 trends, 1 OSS, 1 startup.',
        rationale: 'Research used Plaid as the primary search term across categories.',
        alternatives_considered: [], confidence: 0.85, originating_specialist: 'research_specialist',
        references: ['mem-2'], status: 'accepted', superseded_by: null,
        created_at: new Date(Date.now() - 1700000).toISOString(),
        updated_at: new Date(Date.now() - 1700000).toISOString(),
      },
      {
        id: 'dec-3', project_id: '', entry_number: 3, title: 'Competitor landscape analyzed', category: 'specialist_review',
        description: 'YNAB, Mint, PocketGuard identified as primary competitors. AI coaching identified as key white space.',
        rationale: 'All competitors track but none coach. Social accountability is absent across the board.',
        alternatives_considered: [
          { title: 'Build another general tracker', pros: ['Familiar pattern'], cons: ['No differentiation', 'Oversaturated'] },
          { title: 'Focus on AI coaching', pros: ['Unique angle', 'Strong judge appeal', 'Feasible in 48h'], cons: ['Less proven market'] },
        ],
        confidence: 0.88, originating_specialist: 'competitor_analyst',
        references: ['mem-3'], status: 'accepted', superseded_by: null,
        created_at: new Date(Date.now() - 500000).toISOString(),
        updated_at: new Date(Date.now() - 500000).toISOString(),
      },
    ],
  };
}

export async function getSharedMemory(projectId: string): Promise<ApiResponse<{ entries: SharedMemoryEntry[] }>> {
  try {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/shared/memory`);
    if (res.ok) { const d = await res.json(); if (d?.data?.entries) return { success: true, data: d.data }; }
  } catch { /* fallback */ }
  return { success: true, data: { entries: getMockSharedData().memory } };
}

export async function getDecisions(
  projectId: string, category?: string,
): Promise<ApiResponse<{ entries: DecisionEntry[]; count: number }>> {
  try {
    let url = `${API_BASE_URL}/projects/${projectId}/shared/decisions`;
    if (category) url += `?category=${category}`;
    const res = await fetch(url);
    if (res.ok) { const d = await res.json(); if (d?.data?.entries) return { success: true, data: d.data }; }
  } catch { /* fallback */ }
  const mock = getMockSharedData();
  const filtered = category ? mock.decisions.filter(d => d.category === category) : mock.decisions;
  return { success: true, data: { entries: filtered, count: filtered.length } };
}

// ── S5 Idea Generation ───────────────────────────────────────────────────

export interface IdeaScoreT { innovation: number|null; creativity: number|null; technical_depth: number|null; feasibility: number|null; demo_potential: number|null; judge_appeal: number|null; business_potential: number|null; originality: number|null; confidence: number|null; overall: number|null; }
export interface IdeaRiskT { risk: string; severity: string; mitigation: string; }

export interface IdeaData {
  id: string; project_id: string; generation_id: string;
  title: string; hook: string; elevator_pitch: string;
  problem_statement: string; solution: string; target_users: string;
  why_now: string; usp: string; strategy_label: string;
  innovation_summary: string; competitive_differentiation: string; technical_highlights: string;
  core_features: string[]; stretch_features: string[];
  demo_scenario: string; judge_wow_moment: string;
  technical_risks: IdeaRiskT[]; business_potential: string;
  estimated_build_hours: number|null; estimated_difficulty: number|null;
  recommended_team_size: string; recommended_roles: string[]; future_roadmap: string[];
  target_platform: string; scores: IdeaScoreT;
  why_generated: string; gap_addressed: string; comparison_tags: string[];
  is_selected: boolean; rank: number;
}

export interface IdeasResponseData { generation_id: string; ideas: IdeaData[]; count: number; }

function getMockIdeas(): IdeaData[] {
  const b = { project_id:'', generation_id:'mock', problem_statement:'Students struggle with finances.', solution:'AI coach that learns patterns.', target_users:'College students 18-24', why_now:'Gen Z fintech adoption at all-time high.', usp:'First budgeting app that feels like a coach.', innovation_summary:'Combines behavioral psych with AI.', competitive_differentiation:'Focus on coaching not tracking.', technical_highlights:'LLM + Plaid + React Native.', core_features:['AI analysis','Insights'], stretch_features:['Challenges'], demo_scenario:'AI responds with personalized insight.', judge_wow_moment:'AI shows deep understanding.', technical_risks:[{risk:'Plaid',severity:'medium',mitigation:'Mock'}], business_potential:'Freemium for 20M+ students.', estimated_build_hours:28, estimated_difficulty:55, recommended_team_size:'4', recommended_roles:['Frontend','Backend','AI'], future_roadmap:['V1: Coaching','V2: Banks'], target_platform:'mobile', scores:{innovation:88,creativity:85,technical_depth:72,feasibility:70,demo_potential:92,judge_appeal:90,business_potential:78,originality:80,confidence:85,overall:82}, why_generated:'From competitor gap analysis.', gap_addressed:'AI coaching for students.', is_selected:false };
  return [
    { ...b, id:'i1', title:'Penny', hook:'AI financial coach', elevator_pitch:'AI coach that learns your habits.', strategy_label:'Most Innovative', comparison_tags:['most_innovative'], rank:0 },
    { ...b, id:'i2', title:'SaveQuest', hook:'Saving as a game', elevator_pitch:'Gamified savings with friends.', strategy_label:'Most Practical', comparison_tags:['most_practical'], rank:1, scores:{...b.scores,innovation:82,feasibility:85,overall:80} },
    { ...b, id:'i3', title:'HabitFinance', hook:'Micro-habits impact', elevator_pitch:'Daily habits build skills.', strategy_label:'Best Judge Appeal', comparison_tags:['best_judge_appeal'], rank:2, scores:{...b.scores,feasibility:82,judge_appeal:88,overall:79} },
    { ...b, id:'i4', title:'SplitWise AI', hook:'Smart expenses', elevator_pitch:'AI-powered split expenses.', strategy_label:'Highest Tech Depth', comparison_tags:['highest_technical_depth'], rank:3, scores:{...b.scores,technical_depth:88,overall:76} },
    { ...b, id:'i5', title:'FinLit', hook:'Finance is fun', elevator_pitch:'Interactive finance education.', strategy_label:'Highest Business', comparison_tags:['highest_business'], rank:4, scores:{...b.scores,business_potential:90,overall:75} },
  ];
}

export async function generateIdeas(pid:string): Promise<ApiResponse<IdeasResponseData>> {
  try { const r=await fetch(API_BASE_URL+'/projects/'+pid+'/ideas',{method:'POST'}); if(r.ok){const d=await r.json();if(d?.data?.ideas)return{success:true,data:d.data}} }catch{}
  return { success: true, data: { generation_id:'mock', ideas: getMockIdeas(), count:5 } };
}
export async function getIdeas(pid:string): Promise<ApiResponse<IdeasResponseData>> {
  try { const r=await fetch(API_BASE_URL+'/projects/'+pid+'/ideas'); if(r.ok){const d=await r.json();if(d?.data?.ideas)return{success:true,data:d.data}} }catch{}
  return { success: true, data: { generation_id:'mock', ideas: getMockIdeas(), count:5 } };
}
export async function selectIdea(pid:string,iid:string): Promise<ApiResponse<IdeaData>> {
  try { const r=await fetch(API_BASE_URL+'/projects/'+pid+'/ideas/'+iid+'/select',{method:'POST'}); if(r.ok){const d=await r.json();if(d?.data?.idea)return{success:true,data:d.data.idea}} }catch{}
  return { success: true, data: getMockIdeas()[0] };
}

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

// ── Architecture ──────────────────────────────────────────────────────────────

export interface ArchitectureData {
  system_overview?: string;
  architecture_rationale?: string;
  components?: { name: string; tech?: string; purpose?: string; description?: string }[];
  mermaid_system?: string;
  mermaid_request_flow?: string;
  mermaid_data_flow?: string;
  mermaid_deployment?: string;
  frontend?: { framework: string; routing?: { path: string; component: string }[]; component_hierarchy?: string[] };
  backend?: { framework: string; modules?: string[] };
  database?: { entities: { name: string; fields: { name: string; type: string; pk?: boolean; unique?: boolean }[] }[]; mermaid_er?: string };
  api_contracts?: { method: string; path: string; description?: string }[];
  authentication?: { provider: string; model?: string };
  external_services?: { name: string; purpose: string; fallback?: string }[];
  tradeoffs?: { decision: string; rationale: string; alternatives?: string[]; pros?: string[]; cons?: string[] }[];
  review?: { weak_points?: string[]; failure_modes?: string[] };
  scalability?: { hackathon_version: string; production_version: string };
  generated_at?: string;
}

export async function getArchitecture(projectId: string): Promise<ApiResponse<{ architecture: ArchitectureData }>> {
  try {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/architecture`);
    if (res.ok) { const d = await res.json(); if (d?.data) return { success: true, data: { architecture: d.data } }; }
  } catch {}
  return { success: true, data: { architecture: {} as ArchitectureData } };
}

export async function generateArchitecture(projectId: string): Promise<ApiResponse<{ architecture: ArchitectureData }>> {
  try {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/architecture`, { method: 'POST' });
    if (res.ok) { const d = await res.json(); if (d?.data) return { success: true, data: { architecture: d.data } }; }
  } catch {}
  return { success: true, data: { architecture: {} as ArchitectureData } };
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
    const content = format === 'json' ? '{"message": "Export unavailable"}' : '# Project Export\n\nExport not available.';
    const blob = new Blob([content], { type: format === 'json' ? 'application/json' : 'text/markdown' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `blueprint.${format === 'json' ? 'json' : 'md'}`;
    a.click();
    URL.revokeObjectURL(a.href);
  }
}
