/**
 * exHacker API Service Client
 * Handles connection to FastAPI backend (localhost:8000)
 * Gracefully falls back to mock data if the backend is offline.
 */

import { DEMO_FINANCE_PROJECT } from '@/mock/data';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export async function checkBackendHealth(): Promise<boolean> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 1500);
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { signal: controller.signal });
    clearTimeout(timeoutId);
    return res.ok;
  } catch (e) {
    clearTimeout(timeoutId);
    return false;
  }
}

// Helper to determine if we should mock or make request
async function safeFetch<T>(
  endpoint: string,
  options?: RequestInit,
  mockFallback?: () => T
): Promise<T> {
  try {
    const isOnline = await checkBackendHealth();
    if (!isOnline && mockFallback) {
      console.warn(`[exHacker API] Backend offline. Using mock fallback for endpoint: ${endpoint}`);
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
      throw new Error(errorData.detail?.message || `HTTP error! Status: ${res.status}`);
    }

    const data = await res.json();
    return data;
  } catch (error) {
    console.error(`[exHacker API] Error in endpoint ${endpoint}:`, error);
    if (mockFallback) {
      console.warn(`[exHacker API] Catch block fallback to mock data.`);
      return mockFallback();
    }
    throw error;
  }
}

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

// ── API ENDPOINTS ──

/**
 * 1. Initialize a new project and workflow state
 */
export async function createProject(payload: ProjectCreatePayload): Promise<ProjectResponse> {
  return safeFetch<ProjectResponse>(
    '/projects',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    () => ({
      success: true,
      data: {
        project_id: 'demo-finance-001',
        workflow_id: 'demo-workflow-001',
        status: 'created',
      },
      message: 'Mock Project Created',
    })
  );
}

/**
 * 2. Start workflow execution
 */
export async function startWorkflow(workflowId: string): Promise<any> {
  return safeFetch<any>(
    `/workflows/${workflowId}/start`,
    {
      method: 'POST',
    },
    () => ({
      success: true,
      data: {
        workflow_id: workflowId,
        status: 'waiting_for_user',
      },
    })
  );
}

/**
 * 3. Retrieve current progress/stage of the workflow
 */
export async function getWorkflowStatus(workflowId: string, currentLocalProgress?: number): Promise<WorkflowStatusResponse> {
  return safeFetch<WorkflowStatusResponse>(
    `/workflows/${workflowId}`,
    {
      method: 'GET',
    },
    () => {
      // Mock progress simulation fallback
      const stages = [
        'challenge_intelligence',
        'problem_analysis',
        'opportunity_discovery',
        'idea_generation',
        'idea_validation',
        'human_selection'
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

/**
 * 4. Get the complete state of the workflow
 */
export async function getWorkflowState(workflowId: string): Promise<WorkflowStateResponse> {
  return safeFetch<WorkflowStateResponse>(
    `/workflows/${workflowId}/state`,
    {
      method: 'GET',
    },
    () => ({
      success: true,
      data: {
        state: {
          generated_ideas: DEMO_FINANCE_PROJECT.ideas,
          validation_reports: DEMO_FINANCE_PROJECT.ideas,
        },
      },
    })
  );
}

/**
 * 5. Fetch ideas generated for selection
 */
export async function getProjectIdeas(projectId: string): Promise<IdeasResponse> {
  return safeFetch<IdeasResponse>(
    `/projects/${projectId}/ideas`,
    {
      method: 'GET',
    },
    () => ({
      success: true,
      data: {
        ideas: DEMO_FINANCE_PROJECT.ideas,
        validation_reports: DEMO_FINANCE_PROJECT.ideas,
      },
    })
  );
}

/**
 * 6. User selects an idea and workflow resumes
 */
export async function selectIdea(projectId: string, ideaId: string): Promise<any> {
  return safeFetch<any>(
    `/projects/${projectId}/ideas/select`,
    {
      method: 'POST',
      body: JSON.stringify({ idea_id: ideaId }),
    },
    () => ({
      success: true,
      data: {
        selected_idea: ideaId,
        workflow_status: 'completed',
      },
    })
  );
}

/**
 * 7. Resumepaused workflow (if needed separately)
 */
export async function resumeWorkflow(workflowId: string): Promise<any> {
  return safeFetch<any>(
    `/workflows/${workflowId}/resume`,
    {
      method: 'POST',
    },
    () => ({
      success: true,
      data: {
        status: 'completed',
      },
    })
  );
}

/**
 * 8. Restart a workflow from scratch
 */
export async function restartWorkflow(workflowId: string): Promise<any> {
  return safeFetch<any>(
    `/workflows/${workflowId}/restart`,
    {
      method: 'POST',
    },
    () => ({
      success: true,
      data: {
        status: 'running',
      },
    })
  );
}

// ── GET METRICS & RESULTS ──

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
      data: {
        presentation: {
          slides: [
            { title: 'Title & Hook' },
            { title: 'Problem Statement' },
            { title: 'Market Opportunity' },
            { title: 'Our Solution' },
            { title: 'Live Demo' },
            { title: 'Technical Architecture' },
            { title: 'AI Intelligence' },
            { title: 'Business Model' },
            { title: 'Team & Traction' },
            { title: 'Roadmap' },
            { title: 'Competitive Advantage' },
            { title: 'Call to Action' }
          ]
        }
      }
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
