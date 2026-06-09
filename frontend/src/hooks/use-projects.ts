import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { projectsService, type CreateProjectPayload } from "@/services/projects";
import type { HackathonProject, WorkflowProgress } from "@/types";

const ACTIVE_STATUSES = new Set(["researching", "idea_generation", "architecture"]);

export function useProjects() {
  return useQuery<HackathonProject[]>({
    queryKey: ["projects"],
    queryFn: () => projectsService.list(),
  });
}

export function useProject(id: string) {
  return useQuery<HackathonProject>({
    queryKey: ["projects", id],
    queryFn: () => projectsService.get(id),
    enabled: !!id,
    // Re-fetch every 3 s while the workflow is actively running
    refetchInterval: (query) => {
      const data = query.state.data as HackathonProject | undefined;
      return data && ACTIVE_STATUSES.has(data.status) ? 3000 : false;
    },
  });
}

export function useWorkflowProgress(id: string, enabled: boolean) {
  return useQuery<WorkflowProgress>({
    queryKey: ["progress", id],
    queryFn: () => projectsService.getProgress(id),
    enabled: !!id && enabled,
    // Poll every 2 s when the workflow is running
    refetchInterval: enabled ? 2000 : false,
    staleTime: 0,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateProjectPayload) => projectsService.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}

export function useStartWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (projectId: string) => projectsService.startWorkflow(projectId),
    onSuccess: (_data, projectId) => {
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
      queryClient.invalidateQueries({ queryKey: ["progress", projectId] });
    },
  });
}
