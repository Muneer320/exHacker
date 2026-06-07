export type ProjectStatus =
  | "draft"
  | "researching"
  | "idea_generation"
  | "architecture"
  | "completed";

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
  completedAgents: string[];
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
  errors: Array<{
    agentName: string;
    timestamp: string;
    message: string;
    severity: "warning" | "critical";
  }>;
}
