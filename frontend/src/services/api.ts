/** The studio API never substitutes sample data for a failed request. */

export type Skill = {
  technology: string;
  proficiency: "beginner" | "intermediate" | "advanced";
};
export type Teammate = {
  name: string;
  role: string;
  skills: Skill[];
  hours_available: number | null;
};
export type Intake = {
  idea: string;
  name: string;
  available_hours: number;
  teammates: Teammate[];
  hackathon: string;
  judging_criteria: string;
  rules: string;
  required_technologies: string;
  preferred_technologies: string;
  excluded_technologies: string;
  target_platform: string;
  budget: string;
  constraints: string;
};
export type Risk = { risk: string; severity: string; mitigation: string };
export type Score = { value: number; rationale: string };
export type Idea = {
  id: string;
  title: string;
  hook: string;
  problem: string;
  solution: string;
  target_users: string;
  differentiation: string;
  core_features: string[];
  stretch_features: string[];
  non_goals: string[];
  demo_scenario: string;
  effort_hours: number;
  risks: Risk[];
  assumptions: string[];
  scores: Record<string, Score>;
  overall: number;
  evidence_ids: string[];
  evidence_status: string;
  critique: string[];
  changes_made: string[];
};
export type Source = {
  id: string;
  title: string;
  url: string;
  snippet: string;
  query: string;
  retrieved_at: string;
};
export type Research = {
  sources: Source[];
  queries: string[];
  warnings: string[];
};
export type Stack = {
  summary: string;
  choices: {
    category: string;
    technology: string;
    purpose: string;
    rationale: string;
    alternatives: string[];
    tradeoffs: string[];
  }[];
  components: {
    name: string;
    responsibility: string;
    technology: string;
    depends_on: string[];
  }[];
  data_flow: string[];
  compatibility_notes: string[];
  risks: Risk[];
  setup_steps: string[];
};
export type DocumentFile = {
  filename: string;
  content: string;
  sha256: string;
};
export type Documents = {
  revision: number;
  generated_at: string;
  files: DocumentFile[];
};
export type Project = {
  id: string;
  name: string;
  intake: Intake;
  revision: number;
  state: string;
  context: {
    ideas?: Idea[];
    selected_idea_id?: string | null;
    research?: Research;
    stack?: Stack | null;
    stack_confirmed?: boolean;
    documents?: Documents | null;
    demo?: boolean;
    rounds?: number;
  };
  active_job: string | null;
  ai_cost: number;
  search_count: number;
  created_at: string;
  updated_at: string;
};
export type Job = {
  id: string;
  kind: string;
  status: string;
  events: { message: string; at: string }[];
  error: string | null;
  attempts: number;
  created_at: string;
  updated_at: string;
};
export type Message = {
  id: string;
  role: string;
  content: string;
  context_revision: number;
  created_at: string;
};
export type Artifact = {
  id: string;
  kind: string;
  revision: number;
  created_at: string;
};
export type Configuration = {
  demo: boolean;
  ai_configured: boolean;
  research_configured: boolean;
  model: string;
  worker_enabled: boolean;
  cost_limit: number;
  score_weights: Record<string, number>;
};

export class ApiError extends Error {
  constructor(
    message: string,
    public status = 0,
    public fields: { field: string; message: string }[] = [],
  ) {
    super(message);
  }
}

const BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
const ACCESS_KEY = "exhacker.workspace.access.v2";

export function accessKey(): string {
  let key = localStorage.getItem(ACCESS_KEY);
  if (!key) {
    key = Array.from(crypto.getRandomValues(new Uint8Array(32)), (byte) =>
      byte.toString(16).padStart(2, "0"),
    ).join("");
    localStorage.setItem(ACCESS_KEY, key);
  }
  return key;
}

export function restoreAccessKey(key: string) {
  if (!/^[0-9a-f]{64}$/.test(key.trim()))
    throw new Error("Enter a valid 64-character workspace key.");
  localStorage.setItem(ACCESS_KEY, key.trim());
}

async function fetchApi(path: string, options: RequestInit = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(BASE + path, {
      ...options,
      cache: "no-store",
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessKey()}`,
        ...options.headers,
      },
    });
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new ApiError(
        body?.error?.message ||
          `Request failed (${response.status}). Please retry.`,
        response.status,
        body?.error?.fields || [],
      );
    }
    return response;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(
      error instanceof DOMException && error.name === "AbortError"
        ? "The request timed out. Your saved work is safe; check the connection and retry."
        : "Cannot reach the project service. Check your connection and try again.",
    );
  } finally {
    clearTimeout(timer);
  }
}

export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const response = await fetchApi(path, {
    method,
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const result = await response.json();
  if (!result.success)
    throw new ApiError(result.error?.message || "The operation failed.");
  return result.data as T;
}

export async function download(path: string, filename: string) {
  const response = await fetchApi(path);
  const url = URL.createObjectURL(await response.blob());
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export const emptyIntake: Intake = {
  idea: "",
  name: "",
  available_hours: 48,
  teammates: [
    {
      name: "",
      role: "",
      skills: [{ technology: "", proficiency: "intermediate" }],
      hours_available: null,
    },
  ],
  hackathon: "",
  judging_criteria: "",
  rules: "",
  required_technologies: "",
  preferred_technologies: "",
  excluded_technologies: "",
  target_platform: "web",
  budget: "",
  constraints: "",
};
