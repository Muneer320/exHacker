"use client";

import { useParams, useRouter } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useProject, useStartWorkflow, useWorkflowProgress } from "@/hooks/use-projects";
import { projectsService } from "@/services/projects";
import { AgentLogEntry, AgentError } from "@/types";

const workflowSteps = [
  { key: "user_profiler", label: "User Profile" },
  { key: "challenge_intelligence", label: "Challenge Intelligence" },
  { key: "problem_analyst", label: "Problem Analysis" },
  { key: "opportunity_planner", label: "Opportunity Discovery" },
  { key: "idea_generator", label: "Idea Generation" },
  { key: "idea_validator", label: "Idea Validation" },
  { key: "solution_architect", label: "Solution Architecture" },
  { key: "tech_stack_advisor", label: "Tech Stack" },
  { key: "build_accelerator", label: "Build Accelerator" },
  { key: "presentation_agent", label: "Presentation" },
  { key: "pitch_coach", label: "Pitch Coach" },
];

function LogPanel({ logs, errors }: { logs: AgentLogEntry[]; errors: AgentError[] }) {
  if (logs.length === 0 && errors.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
        No logs yet. Start the workflow to see agent activity.
      </div>
    );
  }

  return (
    <ScrollArea className="h-64 rounded-md border bg-black/5 p-4 dark:bg-white/5">
      <div className="space-y-3">
        {logs.map((log, i) => (
          <div key={i} className="flex flex-col gap-1 rounded bg-background p-2 text-sm shadow-sm">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-primary">{log.agent}</span>
              <span className="text-xs text-muted-foreground">
                {(log.duration_ms / 1000).toFixed(1)}s
              </span>
            </div>
            <div className="flex gap-2 text-xs text-muted-foreground">
              {log.provider && (
                <Badge variant="outline" className="text-[10px]">
                  {log.provider}
                </Badge>
              )}
              {log.model && <span>{log.model}</span>}
              {log.cost !== undefined && <span>${log.cost.toFixed(4)}</span>}
            </div>
            {!log.success && log.error && (
              <div className="mt-1 text-destructive">{log.error}</div>
            )}
          </div>
        ))}
        {errors.map((err, i) => (
          <div key={`err-${i}`} className="rounded bg-destructive/10 p-2 text-sm text-destructive">
            <span className="font-semibold">{err.agent_name || "System"}:</span> {err.message}
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  
  const { data: project, isLoading, refetch } = useProject(params.id);
  const startWorkflow = useStartWorkflow();

  const isWorkflowActive = project?.status === "researching" || project?.status === "idea_generation" || project?.status === "architecture";
  const isFailed = project?.status === "failed";
  const { data: progressData } = useWorkflowProgress(params.id, isWorkflowActive || isFailed);

  const handleRunAgent = async (agentName: string) => {
    await projectsService.runAgent(params.id, agentName);
    refetch();
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-muted-foreground">Loading project...</p>
        </div>
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

  // Merge local progress state with project state
  const completedAgents = progressData?.completed_agents || project.completedAgents || [];
  const completedSet = new Set(completedAgents);
  const currentAgent = progressData?.current_agent || project.currentAgent || null;
  const agentLogs = progressData?.agent_logs || project.agentLogs || [];
  const errorLog = progressData?.error_log || project.errorLog || [];
  const state = (project as any).state || null;
  const arch = state?.architecture || null;
  const techStack = state?.tech_stack || null;
  const prompts = state?.prompts || null;
  const ideas = state?.generated_ideas || [];

  // Only count pipeline steps (deduplicates loops, excludes "export"/"human_approval")
  const completedInPipeline = workflowSteps.filter(s => completedSet.has(s.key));
  const progressPct = Math.min(100, Math.round((completedInPipeline.length / workflowSteps.length) * 100));

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">{project.name}</h1>
            <div className="text-muted-foreground mt-1 flex items-center gap-2">
              <span>Status:</span>
              <Badge
                variant={
                  project.status === "completed"
                    ? "default"
                    : project.status === "failed"
                      ? "destructive"
                      : "secondary"
                }
                className={
                  project.status === "researching" ? "animate-pulse" : ""
                }
              >
                {project.status}
              </Badge>
            </div>
          </div>
          <div className="flex gap-2">
            {project.status === "draft" && (
              <Button
                onClick={() => startWorkflow.mutate(params.id)}
                disabled={startWorkflow.isPending}
                className="relative overflow-hidden"
              >
                {startWorkflow.isPending ? (
                  <>
                    <span className="opacity-0">Start Analysis</span>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
                    </div>
                  </>
                ) : (
                  "Start Analysis"
                )}
              </Button>
            )}
            <Button variant="outline" onClick={() => router.push("/projects")}>
              Back
            </Button>
          </div>
        </div>

        <div className="mt-8">
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="font-medium text-muted-foreground">Overall Progress</span>
            <span className="font-bold">{progressPct}%</span>
          </div>
          <Progress value={progressPct} className="h-3" />
        </div>
      </div>

      <div className="grid gap-8 md:grid-cols-2">
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Agent Pipeline</h2>
          <div className="space-y-3 relative before:absolute before:inset-y-0 before:left-4 before:w-0.5 before:bg-muted">
            {workflowSteps.map((step, idx) => {
              const isCompleted = completedSet.has(step.key);
              const isRunning = currentAgent === step.key;
              const hasError = errorLog.some(e => e.agent_name === step.key);
              
              let statusColor = "bg-muted text-muted-foreground";
              let statusRing = "border-transparent";
              let statusIcon: string | number = idx + 1;
              
              if (isCompleted) {
                statusColor = "bg-green-500 text-white";
                statusIcon = "✓";
              } else if (isRunning) {
                statusColor = "bg-primary text-primary-foreground";
                statusRing = "ring-4 ring-primary/20 animate-pulse";
              } else if (hasError) {
                statusColor = "bg-destructive text-white";
                statusIcon = "!";
              }

              return (
                <div key={step.key} className="relative flex items-center gap-4 pl-12 group transition-all">
                  <div
                    className={`absolute left-0 flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium transition-all duration-300 ${statusColor} ${statusRing}`}
                  >
                    {isRunning ? (
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    ) : (
                      statusIcon
                    )}
                  </div>
                  
                  <Card className={`w-full transition-all duration-300 ${
                    isRunning
                      ? "border-primary shadow-lg scale-[1.02] animate-pulse"
                      : hasError
                        ? "border-destructive/50"
                        : "hover:border-primary/50"
                  }`}>
                    <CardHeader className="py-3 px-4 flex flex-row items-center justify-between">
                      <div className="flex flex-col">
                        <CardTitle className="text-sm">{step.label}</CardTitle>
                        {isRunning && (
                          <span className="text-xs text-primary animate-pulse mt-0.5 font-medium">Processing...</span>
                        )}
                        {hasError && (
                          <span className="text-xs text-destructive mt-0.5">Failed</span>
                        )}
                      </div>
                      
                      {(!isWorkflowActive && project.status !== "completed" && project.status !== "draft") && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                          onClick={() => handleRunAgent(step.key)}
                        >
                          Run
                        </Button>
                      )}
                    </CardHeader>
                  </Card>
                </div>
              );
            })}
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Live Logs</h2>
          <Card>
            <CardContent className="p-0">
              <LogPanel logs={agentLogs} errors={errorLog} />
            </CardContent>
          </Card>
          
          {project.status === "completed" && (
            <div className="space-y-3">
              {arch && (
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Architecture</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    {arch.vision && <p className="text-muted-foreground">{arch.vision}</p>}
                    {arch.features && arch.features.length > 0 && (
                      <div>
                        <span className="font-medium">Features: </span>
                        <span className="text-muted-foreground">{arch.features.join(", ")}</span>
                      </div>
                    )}
                    {arch.user_stories && arch.user_stories.length > 0 && (
                      <div>
                        <span className="font-medium">User Stories: </span>
                        <ul className="mt-1 list-inside list-disc text-muted-foreground">
                          {arch.user_stories.map((s: string, i: number) => (
                            <li key={i}>{s}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {arch.architecture && (
                      <div>
                        <span className="font-medium">Architecture: </span>
                        <pre className="mt-1 overflow-x-auto rounded bg-muted p-2 text-xs">
                          {JSON.stringify(arch.architecture, null, 2)}
                        </pre>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {techStack && (
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Tech Stack</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    {techStack.frontend && (
                      <div>
                        <span className="font-medium">Frontend: </span>
                        <span className="text-muted-foreground">
                          {(techStack.frontend.frameworks || techStack.frontend.languages || []).join(", ")}
                        </span>
                      </div>
                    )}
                    {techStack.backend && (
                      <div>
                        <span className="font-medium">Backend: </span>
                        <span className="text-muted-foreground">
                          {(techStack.backend.frameworks || techStack.backend.languages || []).join(", ")}
                        </span>
                      </div>
                    )}
                    {techStack.databases && techStack.databases.length > 0 && (
                      <div>
                        <span className="font-medium">Databases: </span>
                        <span className="text-muted-foreground">{techStack.databases.join(", ")}</span>
                      </div>
                    )}
                    {techStack.devops && techStack.devops.length > 0 && (
                      <div>
                        <span className="font-medium">DevOps: </span>
                        <span className="text-muted-foreground">{techStack.devops.join(", ")}</span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {prompts && (
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Build Prompts</CardTitle>
                  </CardHeader>
                  <CardContent className="max-h-48 overflow-y-auto space-y-2 text-sm">
                    {prompts.prompts && prompts.prompts.map((p: { title: string; prompt: string }, i: number) => (
                      <div key={i} className="rounded bg-muted p-2">
                        <div className="font-medium">{p.title}</div>
                        <div className="mt-1 whitespace-pre-wrap text-xs text-muted-foreground">{p.prompt}</div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {ideas.length > 0 && (
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Generated Ideas ({ideas.length})</CardTitle>
                  </CardHeader>
                  <CardContent className="max-h-48 overflow-y-auto space-y-2 text-sm">
                    {ideas.map((idea: { id: string; title: string; description: string; innovation_score: number }, i: number) => (
                      <div key={i} className="rounded border p-2">
                        <div className="font-medium">{idea.title}</div>
                        <div className="text-xs text-muted-foreground">{idea.description}</div>
                        {idea.innovation_score !== undefined && (
                          <div className="mt-1 text-xs">Score: {typeof idea.innovation_score === 'number' ? idea.innovation_score.toFixed(1) : idea.innovation_score}</div>
                        )}
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {isFailed && (
            <Card className="border-destructive/50 bg-destructive/10">
              <CardHeader>
                <CardTitle className="text-destructive">Workflow Failed</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-destructive/80 space-y-2">
                <p>The workflow encountered an error and could not complete.</p>
                {errorLog.length > 0 && (
                  <div className="rounded bg-destructive/20 p-2 font-mono text-xs">
                    {errorLog.map((err, i) => (
                      <div key={i} className="mb-1 last:mb-0">
                        <span className="font-semibold">{err.agent_name}:</span> {err.message}
                      </div>
                    ))}
                  </div>
                )}
                <p className="text-muted-foreground text-xs">
                  Check your API keys in the .env file and try creating a new project.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </main>
  );
}
