"use client";

import { useParams, useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useProject, useStartWorkflow } from "@/hooks/use-projects";
import { projectsService } from "@/services/projects";

const workflowSteps = [
  { key: "user_profiler", label: "User Profile", stage: "challenge_intelligence" },
  { key: "challenge_intelligence", label: "Challenge Intelligence", stage: "challenge_intelligence" },
  { key: "problem_analyst", label: "Problem Analysis", stage: "problem_analysis" },
  { key: "opportunity_planner", label: "Opportunity Discovery", stage: "opportunity_analysis" },
  { key: "idea_generator", label: "Idea Generation", stage: "idea_generation" },
  { key: "idea_validator", label: "Idea Validation", stage: "idea_validation" },
  { key: "solution_architect", label: "Solution Architecture", stage: "architecture" },
  { key: "tech_stack_advisor", label: "Tech Stack", stage: "tech_stack" },
  { key: "build_accelerator", label: "Build Accelerator", stage: "build_acceleration" },
  { key: "presentation_agent", label: "Presentation", stage: "presentation" },
  { key: "pitch_coach", label: "Pitch Coach", stage: "pitch" },
];

function getStageIndex(stage: string): number {
  const stages = [
    "input", "challenge_intelligence", "problem_analysis",
    "opportunity_analysis", "idea_generation", "idea_validation",
    "idea_selection", "architecture", "tech_stack",
    "build_acceleration", "presentation", "pitch", "completed",
  ];
  return stages.indexOf(stage);
}

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { data: project, isLoading, refetch } = useProject(params.id);
  const startWorkflow = useStartWorkflow();

  const handleRunAgent = async (agentName: string) => {
    await projectsService.runAgent(params.id, agentName);
    refetch();
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading project...</p>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-destructive">Project not found</p>
      </div>
    );
  }

  const stageIndex = getStageIndex(project.currentStage || "input");
  const progress = Math.round((stageIndex / 12) * 100);
  const completedSet = new Set(project.completedAgents || []);

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">{project.name}</h1>
            <p className="text-muted-foreground">
              Status: {project.status} &middot; Stage: {project.currentStage || "input"}
            </p>
          </div>
          <div className="flex gap-2">
            {project.status === "draft" && (
              <Button
                onClick={() => startWorkflow.mutate(params.id)}
                disabled={startWorkflow.isPending}
              >
                {startWorkflow.isPending ? "Starting..." : "Start Analysis"}
              </Button>
            )}
            <Button variant="outline" onClick={() => router.push("/projects")}>
              Back
            </Button>
          </div>
        </div>

        <div className="mt-4">
          <Progress value={progress} className="h-2" />
          <p className="mt-1 text-sm text-muted-foreground">
            {progress}% complete
          </p>
        </div>
      </div>

      <div className="grid gap-3">
        {workflowSteps.map((step) => {
          const isCompleted = completedSet.has(step.key);
          const isActive = step.stage === project.currentStage;

          return (
            <Card
              key={step.key}
              className={`transition-colors ${
                isCompleted
                  ? "border-green-500/50 bg-green-50/50 dark:bg-green-950/20"
                  : isActive
                    ? "border-primary"
                    : ""
              }`}
            >
              <CardHeader className="py-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium ${
                        isCompleted
                          ? "bg-green-500 text-white"
                          : isActive
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {isCompleted ? "\u2713" : workflowSteps.indexOf(step) + 1}
                    </div>
                    <CardTitle className="text-base">{step.label}</CardTitle>
                  </div>
                  {isActive && project.status !== "completed" && (
                    <Button
                      size="sm"
                      onClick={() => handleRunAgent(step.key)}
                    >
                      Run
                    </Button>
                  )}
                </div>
              </CardHeader>
            </Card>
          );
        })}
      </div>
    </main>
  );
}
