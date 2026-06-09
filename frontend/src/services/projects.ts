import { api } from "@/lib/api";
import type { HackathonProject, WorkflowProgress } from "@/types";

export interface CreateProjectPayload {
  name: string;
  challenge_statements: string[];
  duration_hours: number;
  team_size: number;
  experience_level: string;
  skills: string[];
  tracks: string[];
  datasets: string[];
  apis: string[];
  documentation_links: string[];
  evaluation_criteria: string[];
  notes?: string;
}

export const projectsService = {
  list: () => api.get<HackathonProject[]>("/projects"),

  get: (id: string) => api.get<HackathonProject>(`/projects/${id}`),

  create: (payload: CreateProjectPayload) =>
    api.post<HackathonProject>("/projects", payload),

  delete: (id: string) => api.delete(`/projects/${id}`),

  startWorkflow: (id: string) =>
    api.post<{ status: string; project_id: string }>(`/workflows/${id}/start`, {}),

  getProgress: (id: string) =>
    api.get<WorkflowProgress>(`/workflows/${id}/progress`),

  runAgent: (projectId: string, agentName: string) =>
    api.post<{ status: string; agent: string }>(
      `/workflows/${projectId}/run-agent/${agentName}`,
      {},
    ),
};
