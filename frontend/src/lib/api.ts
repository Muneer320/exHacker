import {
  ProjectFormData,
  ProjectResult,
  WorkflowResponse,
  WorkflowSelectResponse,
  WorkflowStateResponse,
} from "../types/project";

const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

// ─── Legacy one-shot pipeline ─────────────────────────────────────────────────

const GENERATE_TIMEOUT_MS = 3 * 60 * 1000;

export async function generateProject(data: ProjectFormData): Promise<ProjectResult> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), GENERATE_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_URL}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
      signal: controller.signal,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || `Server error: ${response.status}`);
    }

    return response.json() as Promise<ProjectResult>;
  } catch (err: unknown) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new Error("Request timed out after 3 minutes. Please try again.");
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/`, {
      method: "GET",
      signal: AbortSignal.timeout(5000),
    });
    return response.ok;
  } catch {
    return false;
  }
}

// ─── HITL Workflow API ────────────────────────────────────────────────────────

const STEP_TIMEOUT_MS = 3 * 60 * 1000;

async function workflowFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), STEP_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      ...options,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || `Server error: ${response.status}`);
    }

    return response.json() as Promise<T>;
  } catch (err: unknown) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new Error("Agent timed out after 3 minutes. Please try again.");
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

export function startWorkflow(data: ProjectFormData): Promise<WorkflowResponse> {
  return workflowFetch<WorkflowResponse>("/workflow/start", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function continueWorkflow(sessionId: string): Promise<WorkflowResponse> {
  return workflowFetch<WorkflowResponse>("/workflow/continue", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId }),
  });
}

export function selectIdea(
  sessionId: string,
  ideaIndex: number,
  idea?: Record<string, unknown>
): Promise<WorkflowSelectResponse> {
  return workflowFetch<WorkflowSelectResponse>("/workflow/select-idea", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, idea_index: ideaIndex, idea: idea ?? null }),
  });
}

export function updateStepOutput(
  sessionId: string,
  step: string,
  updates: Record<string, unknown>
): Promise<{ ok: boolean; step: string; updated_keys: string[] }> {
  return workflowFetch("/workflow/update-output", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, step, updates }),
  });
}

export function getWorkflowState(sessionId: string): Promise<WorkflowStateResponse> {
  return workflowFetch<WorkflowStateResponse>(`/workflow/state/${sessionId}`, {
    method: "GET",
  });
}

export function getCurrentStep(sessionId: string): Promise<{
  current_step: string | null;
  step_meta: Record<string, unknown> | null;
  completed_steps: string[];
  done: boolean;
}> {
  return workflowFetch(`/workflow/current-step/${sessionId}`, { method: "GET" });
}
