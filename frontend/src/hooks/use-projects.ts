import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { projectsService, type CreateProjectPayload } from "@/services/projects";
import type { HackathonProject } from "@/types";

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
    },
  });
}
