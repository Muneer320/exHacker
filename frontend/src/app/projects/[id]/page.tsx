"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useProject, useStartWorkflow, useWorkflowProgress } from "@/hooks/use-projects";
import { projectsService } from "@/services/projects";
import type { AgentLogEntry, AgentError } from "@/types";

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

function LogEntry({ log }: { log: AgentLogEntry }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded bg-background p-2 text-sm shadow-sm">
      <button
        type="button"
        className="flex w-full items-center justify-between gap-2"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="font-semibold text-primary">{log.agent}</span>
        <div className="flex items-center gap-2">
          {!log.success && log.error && (
            <span className="text-xs text-destructive">Failed</span>
          )}
          <span className="text-xs text-muted-foreground">
            {(log.durationMs / 1000).toFixed(1)}s
          </span>
          <span className="text-xs text-muted-foreground">{expanded ? "▲" : "▼"}</span>
        </div>
      </button>

      {expanded && (
        <div className="mt-2 space-y-1.5 border-t pt-2 text-xs text-muted-foreground">
          {log.provider && (
            <div>
              <span className="font-medium">Provider:</span> {log.provider}
              {log.model && <> / {log.model}</>}
            </div>
          )}
          {log.cost !== undefined && (
            <div>
              <span className="font-medium">Cost:</span> ${log.cost.toFixed(4)}
            </div>
          )}
          {log.inputTokens !== undefined && (
            <div>
              <span className="font-medium">Tokens:</span> {log.inputTokens} in / {log.outputTokens} out
            </div>
          )}
          {log.startedAt && (
            <div>
              <span className="font-medium">Started:</span> {new Date(log.startedAt).toLocaleTimeString()}
            </div>
          )}
          {log.finishedAt && (
            <div>
              <span className="font-medium">Finished:</span> {new Date(log.finishedAt).toLocaleTimeString()}
            </div>
          )}
          {!log.success && log.error && (
            <div className="rounded bg-destructive/10 p-1 text-destructive">
              <span className="font-medium">Error:</span> {log.error}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function LogPanel({ logs, errors }: { logs: AgentLogEntry[]; errors: AgentError[] }) {
  if (logs.length === 0 && errors.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
        No logs yet. Start the workflow to see agent activity.
      </div>
    );
  }

  return (
    <ScrollArea className="h-80 rounded-md border bg-black/5 p-4 dark:bg-white/5">
      <div className="space-y-2">
        {logs.map((log, i) => (
          <LogEntry key={i} log={log} />
        ))}
        {errors.map((err, i) => (
          <div key={`err-${i}`} className="rounded bg-destructive/10 p-2 text-sm text-destructive">
            <span className="font-semibold">{err.agentName || "System"}:</span> {err.message}
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function IdeaPicker({ ideas, projectId, onSelect, onRegenerate }: { ideas: any[]; projectId: string; onSelect: () => void; onRegenerate: () => void }) {
  const [selected, setSelected] = useState<string | null>(null);
  const [regenerating, setRegenerating] = useState(false);

  return (
    <Card className="border-amber-500/50 bg-amber-50/50 dark:bg-amber-950/20">
      <CardHeader>
        <CardTitle className="text-amber-700 dark:text-amber-400">
          Select an Idea ({ideas.length} generated)
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-amber-600 dark:text-amber-300">
          Review the generated ideas and pick one to continue, or regenerate.
        </p>
        <ScrollArea className="max-h-64">
          <div className="space-y-2">
            {ideas.map((idea) => {
              const id = (idea as Record<string, string>).id || "";
              const title = (idea as Record<string, string>).title || "Untitled";
              const desc = (idea as Record<string, string>).description || "";
              const score = (idea as Record<string, number>).innovationScore ?? (idea as Record<string, number>).innovation_score ?? 0;
              const features = (idea as Record<string, string[]>).keyFeatures || (idea as Record<string, string[]>).key_features || [];

              return (
                <button
                  key={id}
                  type="button"
                  className={`w-full rounded border p-3 text-left text-sm transition-all ${
                    selected === id
                      ? "border-amber-500 bg-amber-500/10 ring-2 ring-amber-500/30"
                      : "border-transparent bg-background hover:border-amber-500/50"
                  }`}
                  onClick={() => setSelected(id)}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{title}</span>
                    <Badge variant="outline" className="text-xs">
                      Score: {typeof score === "number" ? score.toFixed(1) : score}
                    </Badge>
                  </div>
                  <div className="mt-1 text-xs text-muted-foreground line-clamp-2">{desc}</div>
                  {features.length > 0 && (
                    <div className="mt-1 flex flex-wrap gap-1">
                      {features.slice(0, 4).map((f: string, fi: number) => (
                        <span key={fi} className="rounded bg-muted px-1.5 py-0.5 text-[10px]">{f}</span>
                      ))}
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </ScrollArea>

        <div className="flex gap-2">
          <Button
            onClick={async () => {
              if (!selected) return;
              await projectsService.selectIdea(projectId, selected);
              onSelect();
            }}
            disabled={!selected}
            className="flex-1"
          >
            Build This Idea
          </Button>
          <Button
            variant="outline"
            onClick={async () => {
              setRegenerating(true);
              await projectsService.regenerateIdeas(projectId);
              setRegenerating(false);
              onRegenerate();
            }}
            disabled={regenerating}
          >
            {regenerating ? "Generating..." : "Regenerate Ideas"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function ResultPanel({ ideas, arch, techStack, prompts }: { ideas: any[]; arch: any; techStack: any; prompts: any }) {
  return (
    <div className="space-y-3">
      {ideas.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Generated Ideas ({ideas.length})</CardTitle>
          </CardHeader>
          <CardContent className="max-h-48 overflow-y-auto space-y-2 text-sm">
            {ideas.map((idea, i) => {
              const title = (idea as Record<string, string>).title || "Untitled";
              const desc = (idea as Record<string, string>).description || "";
              const score = (idea as Record<string, number>).innovationScore ?? (idea as Record<string, number>).innovation_score ?? 0;
              return (
                <div key={i} className="rounded border p-2">
                  <div className="font-medium">{title}</div>
                  <div className="text-xs text-muted-foreground">{desc}</div>
                  <div className="mt-1 text-xs">Score: {typeof score === "number" ? score.toFixed(1) : score}</div>
                </div>
              );
            })}
          </CardContent>
        </Card>
      )}

      {arch && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Architecture</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {arch.vision && <p className="text-muted-foreground">{arch.vision as string}</p>}
            {arch.features && (arch.features as string[]).length > 0 && (
              <div><span className="font-medium">Features: </span><span className="text-muted-foreground">{(arch.features as string[]).join(", ")}</span></div>
            )}
            {arch.userStories && (arch.userStories as string[]).length > 0 && (
              <div>
                <span className="font-medium">User Stories: </span>
                <ul className="mt-1 list-inside list-disc text-muted-foreground">
                  {(arch.userStories as string[]).map((s: string, i: number) => (
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
            {(techStack.frontend as Record<string, string[]> | undefined) && (
              <div><span className="font-medium">Frontend: </span><span className="text-muted-foreground">{((techStack.frontend as Record<string, string[]>).frameworks || (techStack.frontend as Record<string, string[]>).languages || []).join(", ")}</span></div>
            )}
            {(techStack.backend as Record<string, string[]> | undefined) && (
              <div><span className="font-medium">Backend: </span><span className="text-muted-foreground">{((techStack.backend as Record<string, string[]>).frameworks || (techStack.backend as Record<string, string[]>).languages || []).join(", ")}</span></div>
            )}
            {techStack.databases && (techStack.databases as string[]).length > 0 && (
              <div><span className="font-medium">Databases: </span><span className="text-muted-foreground">{(techStack.databases as string[]).join(", ")}</span></div>
            )}
            {techStack.devops && (techStack.devops as string[]).length > 0 && (
              <div><span className="font-medium">DevOps: </span><span className="text-muted-foreground">{(techStack.devops as string[]).join(", ")}</span></div>
            )}
          </CardContent>
        </Card>
      )}

      {prompts && (prompts.prompts as Array<{ title: string; prompt: string }>)?.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Build Prompts</CardTitle>
          </CardHeader>
          <CardContent className="max-h-48 overflow-y-auto space-y-2 text-sm">
            {(prompts.prompts as Array<{ title: string; prompt: string }>).map((p, i) => (
              <div key={i} className="rounded bg-muted p-2">
                <div className="font-medium">{p.title}</div>
                <div className="mt-1 whitespace-pre-wrap text-xs text-muted-foreground">{p.prompt}</div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();

  const { data: project, isLoading, refetch } = useProject(params.id);
  const startWorkflow = useStartWorkflow();

  const isWorkflowActive = project?.status === "researching"
    || project?.status === "idea_generation"
    || project?.status === "architecture"
    || project?.status === "idea_selection"
    || project?.status === "failed";

  const { data: progressData } = useWorkflowProgress(params.id, isWorkflowActive);

  const completedAgents = progressData?.completedAgents || project?.completedAgents || [];
  const completedSet = new Set(completedAgents);
  const currentAgent = progressData?.currentAgent || project?.currentAgent || null;
  const agentLogs = progressData?.agentLogs || project?.agentLogs || [];
  const errorLog = progressData?.errorLog || project?.errorLog || [];
  const state = project?.state ?? null;
  const arch = (state as any)?.architecture ?? null;
  const techStack = (state as any)?.techStack ?? null;
  const prompts = (state as any)?.prompts ?? null;
  const ideas = (state as any)?.generatedIdeas ?? [];

  const completedInPipeline = workflowSteps.filter(s => completedSet.has(s.key));
  const progressCount = completedInPipeline.length;
  const progressTotal = workflowSteps.length;

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

  const statusBadgeVariant =
    project.status === "completed" ? "default" as const
      : project.status === "failed" ? "destructive" as const
        : project.status === "idea_selection" ? "outline" as const
          : "secondary" as const;

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">{project.name}</h1>
            <div className="text-muted-foreground mt-1 flex items-center gap-2">
              <span>Status:</span>
              <Badge
                variant={statusBadgeVariant}
                className={
                  (project.status === "researching" || project.status === "idea_selection")
                    ? "animate-pulse" : ""
                }
              >
                {project.status === "idea_selection" ? "awaiting selection" : project.status}
              </Badge>
            </div>
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

        <div className="mt-8">
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="font-medium text-muted-foreground">Overall Progress</span>
            <span className="font-bold">{progressCount}/{progressTotal}</span>
          </div>
          <Progress value={(progressCount / progressTotal) * 100} className="h-3" />
        </div>
      </div>

      <div className="grid gap-8 md:grid-cols-2">
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Agent Pipeline</h2>
          <div className="space-y-3 relative before:absolute before:inset-y-0 before:left-4 before:w-0.5 before:bg-muted">
            {workflowSteps.map((step, idx) => {
              const isCompleted = completedSet.has(step.key);
              const isRunning = currentAgent === step.key;
              const hasError = errorLog.some(e => e.agentName === step.key);

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
                    <CardHeader className="py-3 px-4">
                      <CardTitle className="text-sm">{step.label}</CardTitle>
                      {isRunning && (
                        <span className="text-xs text-primary animate-pulse mt-0.5 font-medium">Processing...</span>
                      )}
                      {hasError && (
                        <span className="text-xs text-destructive mt-0.5">Failed</span>
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

          {project.status === "idea_selection" && ideas.length > 0 && (
            <IdeaPicker
              ideas={ideas}
              projectId={project.id}
              onSelect={() => refetch()}
              onRegenerate={() => refetch()}
            />
          )}

          {project.status === "completed" && (
            <ResultPanel ideas={ideas} arch={arch} techStack={techStack} prompts={prompts} />
          )}

          {project.status === "failed" && (
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
                        <span className="font-semibold">{err.agentName}:</span> {err.message}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </main>
  );
}
