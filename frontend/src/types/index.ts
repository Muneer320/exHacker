export type ProjectStatus =
  | "draft"
  | "researching"
  | "idea_generation"
  | "architecture"
  | "completed"
  | "failed";

export interface TeamProfile {
  teamSize: number;
  experienceLevel: "beginner" | "intermediate" | "advanced";
  skills: string[];
  complexityBudget: "low" | "medium" | "high";
  recommendedScope: "mvp" | "advanced_mvp";
}

export interface ResourceCollection {
  tracks: string[];
  datasets: string[];
  apis: string[];
  documentationLinks: string[];
}

export interface AgentLogEntry {
  agent: string;
  started_at: string;
  finished_at: string;
  duration_ms: number;
  success: boolean;
  provider?: string;
  model?: string;
  input_tokens?: number;
  output_tokens?: number;
  cost?: number;
  error?: string;
}

export interface AgentError {
  agent_name: string;
  timestamp: string;
  message: string;
  severity: "warning" | "critical";
}

export interface HackathonProject {
  id: string;
  name: string;
  challengeStatements: string[];
  durationHours: number;
  createdAt: string;
  updatedAt: string;
  status: ProjectStatus;
  team: TeamProfile;
  resources: ResourceCollection;
  currentStage: string;
  currentAgent: string | null;
  completedAgents: string[];
  agentLogs: AgentLogEntry[];
  errorLog: AgentError[];
  state?: Record<string, unknown>;
}

export interface WorkflowProgress {
  project_id: string;
  status: ProjectStatus;
  current_stage: string;
  current_agent: string | null;
  completed_agents: string[];
  agent_logs: AgentLogEntry[];
  error_log: AgentError[];
  updated_at: string | null;
}

export interface ChallengeIntelligence {
  themes: string[];
  opportunities: string[];
  constraints: string[];
  resourceOpportunities: string[];
  evaluationFocus: string[];
}

export interface Idea {
  id: string;
  title: string;
  description: string;
  targetUsers: string[];
  keyFeatures: string[];
  innovationScore: number;
  feasibilityScore: number;
  hackathonFitScore: number;
  technicalWowScore: number;
  finalScore: number;
}

export interface ExHackerState {
  project: HackathonProject;
  teamProfile?: TeamProfile;
  challengeIntelligence?: ChallengeIntelligence;
  generatedIdeas?: Idea[];
  currentStage: string;
  completedAgents: string[];
  errors: AgentError[];
}
