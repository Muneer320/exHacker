// ─── Idea ───────────────────────────────────────────────────────────────────
export interface Idea {
  title: string;
  description: string;
  problem_solved: string;
  target_users: string[];
  core_features: string[];
  innovation_factor: string;
  why_it_wins: string;
  feasibility_score: number;
  innovation_score: number;
  hackathon_fit_score: number;
  category?: string;
  tech_stack?: string[];
}

// ─── Ranked Idea ─────────────────────────────────────────────────────────────
export interface RankedIdea {
  title: string;
  description?: string;
  final_score: number;
  overall_score?: number;
  innovation_score: number;
  feasibility_score: number;
  hackathon_fit_score: number;
  market_potential_score: number;
  technical_wow_factor: number;
  strengths: string[];
  weaknesses: string[];
  why_ranked_here: string;
}

// ─── Product Vision ───────────────────────────────────────────────────────────
export interface ProductVision {
  name: string;
  description: string;
  elevator_pitch: string;
  problem_solved: string;
  why_this_wins: string;
}

// ─── Backend Component ────────────────────────────────────────────────────────
export interface BackendComponent {
  endpoint: string;
  method: string;
  description: string;
  live_logic: boolean;
}

// ─── Solution Blueprint ───────────────────────────────────────────────────────
export interface SolutionBlueprint {
  product_vision: ProductVision;
  target_users: string[];
  core_features: string[];
  user_flow: string[];
  architecture_overview: string;
  frontend_components: string[];
  backend_components: BackendComponent[];
  database_schema: string[];
  ai_components: string[];
  integrations: string[];
  mvp_scope: string[];
  future_scope: string[];
  implementation_steps: string[];
}

// ─── Slide ────────────────────────────────────────────────────────────────────
export interface Slide {
  slide_number: number;
  title: string;
  objective: string;
  content: string[];
  speaker_notes: string;
  visual_suggestion: string;
  slide_type?: string;
}

// ─── Problem & Opportunity ────────────────────────────────────────────────────
export interface ProblemAnalysis {
  problem_statement: string;
  pain_points: string[];
  stakeholders: string[];
  success_metrics: string[];
}

export interface OpportunityAnalysis {
  market_gap: string;
  target_market: string;
  market_size: string;
  key_opportunities: string[];
}

// ─── Full project result ─────────────────────────────────────────────────────
export interface ProjectResult {
  challenge_statement: string;
  hackathon_name: string;
  sponsors: string[];
  tracks: string[];
  problem_analysis: ProblemAnalysis;
  opportunity_analysis: OpportunityAnalysis;
  ideas: Idea[];
  ranked_ideas: RankedIdea[];
  selected_idea: Idea;
  solution_blueprint: SolutionBlueprint;
  slides: Slide[];
  pitch_30s: string;
  pitch_2min: string;
  pitch_5min: string;
  final_report: string;
  prd_document?: string;
  vision_document?: string;
}

// ─── Form input ───────────────────────────────────────────────────────────────
export interface ProjectFormData {
  challenge_statement: string;
  hackathon_name: string;
  sponsors: string[];
  tracks: string[];
}

// ─── HITL Workflow Types ──────────────────────────────────────────────────────

export interface StepMeta {
  key: string;
  label: string;
  description: string;
  output_key: string;
  is_select_step: boolean;
  symbol: string;
}

export interface CompletedStep {
  step: string;
  label: string;
  output: Record<string, unknown>;
}

export interface WorkflowResponse {
  session_id: string;
  completed_step: string;
  completed_step_label: string;
  output: Record<string, unknown>;
  next_step: string | null;
  next_step_label: string | null;
  next_is_select_step: boolean;
  done: boolean;
}

export interface WorkflowSelectResponse {
  session_id: string;
  completed_step: string;
  completed_step_label: string;
  selected_idea: Record<string, unknown>;
  output: Record<string, unknown>;
  next_step: string | null;
  next_step_label: string | null;
  next_is_select_step: boolean;
  done: boolean;
}

export interface WorkflowStateResponse {
  session_id: string;
  state: Record<string, unknown>;
  current_step: string | null;
  completed_steps: string[];
  step_outputs: Record<string, Record<string, unknown>>;
  steps_meta: StepMeta[];
  done: boolean;
}
