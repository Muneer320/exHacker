/** Pipeline types — specialist stage definitions for the mission control panel. */

export type StageStatus =
  | "queued"
  | "waiting"
  | "running"
  | "streaming"
  | "completed"
  | "failed"
  | "cached"
  | "using_fallback"
  | "skipped";

export interface StreamingLogEntry {
  id: string;
  text: string;
  timestamp: number;
  type: "info" | "search" | "ai" | "synthesis" | "complete" | "error";
}

export interface PipelineStageDefinition {
  id: string;
  icon: string;
  name: string;
  shortName: string;
  description: string;
  specialistId: string; // e.g. "challenge_analyst"
}

export interface PipelineStageState {
  /** Definition reference */
  stageId: string;
  /** Current status */
  status: StageStatus;
  /** Progress 0-100 */
  progress: number;
  /** Confidence 0-1 */
  confidence: number | null;
  /** AI model used */
  modelUsed: string | null;
  /** Runtime in seconds */
  runtime: number | null;
  /** Last updated timestamp */
  lastUpdated: number | null;
  /** Whether this stage is expanded */
  expanded: boolean;
  /** Summary text for the completed stage */
  summary: string | null;
  /** Streaming log entries */
  log: StreamingLogEntry[];
  /** Error message if failed */
  error: string | null;
  /** Whether this used cached data */
  isCached: boolean;
  /** Whether this used fallback */
  isFallback: boolean;
  /** Key findings from this stage (for quick scan) */
  keyFindings: string[];
}

export interface PipelineState {
  stages: Record<string, PipelineStageState>;
  activeStageId: string | null;
  projectName: string;
  projectStatus: string;
}

export type PipelineAction =
  | { type: "SET_STAGE_STATUS"; stageId: string; status: StageStatus }
  | { type: "SET_PROGRESS"; stageId: string; progress: number }
  | { type: "SET_CONFIDENCE"; stageId: string; confidence: number }
  | { type: "SET_MODEL"; stageId: string; model: string }
  | { type: "SET_RUNTIME"; stageId: string; runtime: number }
  | { type: "SET_SUMMARY"; stageId: string; summary: string }
  | { type: "SET_KEY_FINDINGS"; stageId: string; findings: string[] }
  | { type: "SET_ERROR"; stageId: string; error: string }
  | { type: "TOGGLE_EXPAND"; stageId: string }
  | { type: "ADD_LOG"; stageId: string; entry: StreamingLogEntry }
  | { type: "CLEAR_LOG"; stageId: string }
  | { type: "MARK_CACHED"; stageId: string; isCached: boolean }
  | { type: "MARK_FALLBACK"; stageId: string; isFallback: boolean }
  | { type: "SET_ACTIVE_STAGE"; stageId: string | null }
  | { type: "RESET" };

/** All specialist stages in order */
export const PIPELINE_STAGES: PipelineStageDefinition[] = [
  { id: "challenge", icon: "🧠", name: "Challenge Intelligence", shortName: "Challenge", description: "Extract themes, constraints, opportunities from the brief", specialistId: "challenge_analyst" },
  { id: "research", icon: "🔍", name: "Research Specialist", shortName: "Research", description: "Scan competitors, APIs, OSS, winners, trends", specialistId: "research_specialist" },
  { id: "competitors", icon: "🎯", name: "Competitor Analysis", shortName: "Competitors", description: "Identify gaps, white space, differentiation", specialistId: "competitor_analyst" },
  { id: "memory", icon: "💾", name: "Shared Intelligence", shortName: "Memory", description: "Store and link all specialist outputs", specialistId: "shared_memory" },
  { id: "ideas", icon: "💡", name: "Idea Generation", shortName: "Ideas", description: "Generate and score 5 distinct product concepts", specialistId: "idea_generator" },
  { id: "architecture", icon: "🏗️", name: "Solution Architect", shortName: "Architecture", description: "Design complete technical architecture", specialistId: "solution_architect" },
  { id: "docs", icon: "📝", name: "Documentation Writer", shortName: "Documentation", description: "Generate PRD, README, API docs, and pitch", specialistId: "documentation_writer" },
  { id: "export", icon: "📦", name: "Export", shortName: "Export", description: "Download complete project package", specialistId: "export" },
];

export const INITIAL_STAGE_STATE: PipelineStageState = {
  stageId: "",
  status: "queued",
  progress: 0,
  confidence: null,
  modelUsed: null,
  runtime: null,
  lastUpdated: null,
  expanded: false,
  summary: null,
  log: [],
  error: null,
  isCached: false,
  isFallback: false,
  keyFindings: [],
};

export function createInitialState(projectName?: string): PipelineState {
  const stages: Record<string, PipelineStageState> = {};
  for (const stage of PIPELINE_STAGES) {
    stages[stage.id] = { ...INITIAL_STAGE_STATE, stageId: stage.id };
  }
  return { stages, activeStageId: null, projectName: projectName || "Untitled", projectStatus: "draft" };
}
