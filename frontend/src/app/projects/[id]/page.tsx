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

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Dict = Record<string, any>;

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

const STATE_KEYS: Record<string, string> = {
  user_profiler: "teamProfile",
  challenge_intelligence: "challengeIntelligence",
  problem_analyst: "problemAnalysis",
  opportunity_planner: "opportunityAnalysis",
  idea_generator: "generatedIdeas",
  idea_validator: "validationReports",
  solution_architect: "architecture",
  tech_stack_advisor: "techStack",
  build_accelerator: "prompts",
  presentation_agent: "presentation",
  pitch_coach: "pitch",
};

function AgentDetail({
  agentName,
  log,
  stateValue,
}: {
  agentName: string;
  log?: AgentLogEntry;
  stateValue: unknown;
}) {
  const step = workflowSteps.find(s => s.key === agentName);

  if (!log) {
    return (
      <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
        No data available for this agent.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">{step?.label || agentName}</h3>
        <Badge variant={log.success ? "default" : "destructive"}>
          {log.success ? "Success" : "Failed"}
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="rounded bg-muted p-2">
          <div className="text-xs text-muted-foreground">Duration</div>
          <div className="font-medium">{(log.durationMs / 1000).toFixed(1)}s</div>
        </div>
        {log.provider && (
          <div className="rounded bg-muted p-2">
            <div className="text-xs text-muted-foreground">Provider</div>
            <div className="font-medium">{log.provider}</div>
          </div>
        )}
        {log.model && (
          <div className="rounded bg-muted p-2">
            <div className="text-xs text-muted-foreground">Model</div>
            <div className="font-medium text-xs">{log.model}</div>
          </div>
        )}
        {log.cost !== undefined && (
          <div className="rounded bg-muted p-2">
            <div className="text-xs text-muted-foreground">Cost</div>
            <div className="font-medium">${log.cost.toFixed(4)}</div>
          </div>
        )}
        {log.inputTokens !== undefined && (
          <div className="rounded bg-muted p-2">
            <div className="text-xs text-muted-foreground">Tokens</div>
            <div className="font-medium">{log.inputTokens} → {log.outputTokens}</div>
          </div>
        )}
        {log.startedAt && (
          <div className="rounded bg-muted p-2">
            <div className="text-xs text-muted-foreground">Started</div>
            <div className="font-medium text-xs">{new Date(log.startedAt).toLocaleString()}</div>
          </div>
        )}
      </div>

      {!log.success && log.error && (
        <div className="rounded bg-destructive/10 p-3 text-sm">
          <div className="mb-1 font-medium text-destructive">Error</div>
          <div className="whitespace-pre-wrap font-mono text-xs text-destructive/80">
            {log.error.includes("rate_limit") || log.error.includes("429") || log.error.includes("Rate limit")
              ? "Rate limit reached. Please wait a few minutes or add a Gemini API key as fallback in your .env file."
              : log.error}
          </div>
        </div>
      )}

      {stateValue && (
        <div>
          <div className="mb-1 text-sm font-medium">Output</div>
          <ScrollArea className="max-h-64">
            <pre className="rounded bg-muted p-3 font-mono text-xs leading-relaxed">
              {formatOutput(stateValue)}
            </pre>
          </ScrollArea>
        </div>
      )}
    </div>
  );
}

function formatOutput(val: unknown): string {
  if (Array.isArray(val)) {
    return val.map(item => {
      if (typeof item === "object" && item !== null) {
        return Object.entries(item)
          .filter(([k]) => !["id"].includes(k))
          .map(([k, v]) => {
            const label = k.replace(/([A-Z])/g, " $1").replace(/^./, s => s.toUpperCase());
            if (Array.isArray(v)) return `${label}: ${v.join(", ")}`;
            if (typeof v === "object" && v !== null) return `${label}: ${JSON.stringify(v)}`;
            return `${label}: ${v}`;
          })
          .join("\n");
      }
      return String(item);
    }).join("\n---\n");
  }
  if (typeof val === "object" && val !== null) {
    return Object.entries(val)
      .filter(([k]) => !["id"].includes(k))
      .map(([k, v]) => {
        const label = k.replace(/([A-Z])/g, " $1").replace(/^./, s => s.toUpperCase());
        if (Array.isArray(v)) return `${label}: ${v.join(", ")}`;
        if (typeof v === "object" && v !== null) return `${label}: ${JSON.stringify(v, null, 2)}`;
        return `${label}: ${v}`;
      })
      .join("\n");
  }
  return String(val);
}

function LogPanel({ logs, errors, onSelect }: { logs: AgentLogEntry[]; errors: AgentError[]; onSelect: (agent: string) => void }) {
  if (logs.length === 0 && errors.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
        No logs yet. Start the workflow to see agent activity.
      </div>
    );
  }

  return (
    <ScrollArea className="h-80 rounded-md border bg-black/5 dark:bg-white/5">
      <div className="space-y-1 p-2">
        {logs.map((log, i) => (
          <button
            key={i}
            type="button"
            onClick={() => onSelect(log.agent)}
            className={`flex w-full items-center justify-between rounded px-3 py-2 text-left text-sm transition-colors hover:bg-accent ${
              !log.success ? "bg-destructive/5" : ""
            }`}
          >
            <div className="flex items-center gap-2 min-w-0">
              <span className={`h-2 w-2 shrink-0 rounded-full ${log.success ? "bg-green-500" : "bg-destructive"}`} />
              <span className="font-medium truncate">{log.agent}</span>
              {!log.success && log.error && (
                <span className="text-xs text-destructive shrink-0">Failed</span>
              )}
            </div>
            <span className="text-xs text-muted-foreground shrink-0 ml-2">
              {(log.durationMs / 1000).toFixed(1)}s
            </span>
          </button>
        ))}
        {errors.map((err, i) => (
          <div key={`err-${i}`} className="rounded bg-destructive/10 px-3 py-2 text-xs text-destructive">
            <span className="font-semibold">{err.agentName || "System"}:</span> {err.message}
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}

function IdeaPicker({ ideas, projectId, onSelect, onRegenerate }: { ideas: Dict[]; projectId: string; onSelect: () => void; onRegenerate: () => void }) {
  const [selected, setSelected] = useState<string | null>(null);
  const [regenerating, setRegenerating] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  return (
    <Card>
      <CardHeader className="border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Select an Idea</CardTitle>
          <Badge variant="outline">{ideas.length} generated</Badge>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Choose an idea to build, or regenerate for new options.
        </p>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="max-h-[400px]">
          <div className="space-y-2 p-4">
            {ideas.map((idea) => {
              const id = idea.id || "";
              const title = idea.title || "Untitled";
              const desc = idea.description || "";
              const score = idea.finalScore ?? idea.final_score ?? idea.innovationScore ?? idea.innovation_score ?? 0;
              const features = idea.keyFeatures || idea.key_features || [];
              const isSelected = selected === id;

              return (
                <button
                  key={id}
                  type="button"
                  className={`w-full rounded-lg border p-4 text-left transition-all ${
                    isSelected
                      ? "border-primary bg-primary/5 ring-2 ring-primary/20"
                      : "border-border hover:border-primary/50 hover:bg-accent/50"
                  }`}
                  onClick={() => setSelected(id)}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="font-semibold">{title}</div>
                      <div className="mt-1 text-sm text-muted-foreground line-clamp-2">{desc}</div>
                      {features.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1.5">
                          {features.slice(0, 5).map((f: string, fi: number) => (
                            <span key={fi} className="rounded-md bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
                              {f}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="shrink-0 text-right">
                      <div className="text-2xl font-bold tabular-nums">{typeof score === "number" ? Math.round(score) : score}</div>
                      <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Score</div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </ScrollArea>

        <div className="flex gap-3 border-t p-4">
          <Button
            className="flex-1"
            onClick={async () => {
              if (!selected) return;
              setSubmitting(true);
              await projectsService.selectIdea(projectId, selected);
              setSubmitting(false);
              onSelect();
            }}
            disabled={!selected || submitting}
          >
            {submitting ? "Building..." : "Build This Idea"}
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
            {regenerating ? "Generating..." : "Regenerate"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function ArchitectureReviewPanel({ arch, projectId, onApprove }: { arch: Dict | null; projectId: string; onApprove: () => void }) {
  const [approving, setApproving] = useState(false);

  return (
    <Card>
      <CardHeader className="border-b">
        <CardTitle className="text-base">Architecture Review</CardTitle>
        <p className="text-sm text-muted-foreground mt-1">
          Review the proposed architecture before continuing.
        </p>
      </CardHeader>
      <CardContent className="space-y-4 p-4">
        {arch && (
          <>
            {arch.vision && (
              <div>
                <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Vision</div>
                <p className="text-sm">{arch.vision}</p>
              </div>
            )}
            {arch.features?.length > 0 && (
              <div>
                <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Features</div>
                <div className="flex flex-wrap gap-1.5">
                  {arch.features.map((f: string, i: number) => (
                    <span key={i} className="rounded-md bg-muted px-2 py-0.5 text-xs">{f}</span>
                  ))}
                </div>
              </div>
            )}
            {arch.userStories?.length > 0 && (
              <div>
                <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">User Stories</div>
                <ul className="list-inside list-disc space-y-0.5 text-xs text-muted-foreground">
                  {arch.userStories.map((s: string, i: number) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
        <div className="flex gap-3 pt-2 border-t">
          <Button
            className="flex-1"
            onClick={async () => {
              setApproving(true);
              await projectsService.approveCheckpoint(projectId);
              setApproving(false);
              onApprove();
            }}
            disabled={approving}
          >
            {approving ? "Continuing..." : "Approve Architecture"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function TechStackReviewPanel({ techStack, projectId, onApprove }: { techStack: Dict | null; projectId: string; onApprove: () => void }) {
  const [approving, setApproving] = useState(false);

  return (
    <Card>
      <CardHeader className="border-b">
        <CardTitle className="text-base">Tech Stack Review</CardTitle>
        <p className="text-sm text-muted-foreground mt-1">
          Review the proposed technology stack before continuing.
        </p>
      </CardHeader>
      <CardContent className="space-y-4 p-4">
        {techStack && (
          <>
            {[
              { label: "Frontend", data: techStack.frontend },
              { label: "Backend", data: techStack.backend },
            ].map(({ label, data }) =>
              data ? (
                <div key={label}>
                  <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">{label}</div>
                  <div className="flex flex-wrap gap-1.5">
                    {[...(data.frameworks || []), ...(data.languages || [])].map((item: string, i: number) => (
                      <span key={i} className="rounded-md bg-muted px-2 py-0.5 text-xs">{item}</span>
                    ))}
                  </div>
                </div>
              ) : null
            )}
            {techStack.databases?.length > 0 && (
              <div>
                <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Databases</div>
                <div className="flex flex-wrap gap-1.5">
                  {techStack.databases.map((db: string, i: number) => (
                    <span key={i} className="rounded-md bg-muted px-2 py-0.5 text-xs">{db}</span>
                  ))}
                </div>
              </div>
            )}
            {techStack.devops?.length > 0 && (
              <div>
                <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">DevOps</div>
                <div className="flex flex-wrap gap-1.5">
                  {techStack.devops.map((item: string, i: number) => (
                    <span key={i} className="rounded-md bg-muted px-2 py-0.5 text-xs">{item}</span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
        <div className="flex gap-3 pt-2 border-t">
          <Button
            className="flex-1"
            onClick={async () => {
              setApproving(true);
              await projectsService.approveCheckpoint(projectId);
              setApproving(false);
              onApprove();
            }}
            disabled={approving}
          >
            {approving ? "Continuing..." : "Approve Tech Stack"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function PromptsReviewPanel({ prompts, projectId, onApprove }: { prompts: Dict | null; projectId: string; onApprove: () => void }) {
  const [approving, setApproving] = useState(false);

  return (
    <Card>
      <CardHeader className="border-b">
        <CardTitle className="text-base">Build Prompts Review</CardTitle>
        <p className="text-sm text-muted-foreground mt-1">
          Review the generated build prompts before continuing.
        </p>
      </CardHeader>
      <CardContent className="space-y-4 p-4">
        {prompts?.prompts?.length > 0 && (
          <div className="space-y-2">
            {prompts.prompts.map((p: { title: string; prompt: string }, i: number) => (
              <details key={i} className="group rounded-lg border p-3">
                <summary className="cursor-pointer text-sm font-medium hover:text-foreground">
                  {p.title}
                </summary>
                <div className="mt-2 whitespace-pre-wrap rounded bg-muted p-3 font-mono text-xs leading-relaxed text-muted-foreground">
                  {p.prompt}
                </div>
              </details>
            ))}
          </div>
        )}
        <div className="flex gap-3 pt-2 border-t">
          <Button
            className="flex-1"
            onClick={async () => {
              setApproving(true);
              await projectsService.approveCheckpoint(projectId);
              setApproving(false);
              onApprove();
            }}
            disabled={approving}
          >
            {approving ? "Continuing..." : "Approve Prompts"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function ResultPanel({ ideas, arch, techStack, prompts }: { ideas: Dict[]; arch: Dict | null; techStack: Dict | null; prompts: Dict | null }) {
  return (
    <div className="space-y-3">
      {ideas.length > 0 && (
        <Card>
          <CardHeader className="pb-3 border-b">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Generated Ideas</CardTitle>
              <Badge variant="outline">{ideas.length}</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="max-h-[400px]">
              <div className="space-y-2 p-4">
                {ideas.map((idea, i) => {
                  const title = idea.title || "Untitled";
                  const desc = idea.description || "";
                  const score = idea.finalScore ?? idea.final_score ?? idea.innovationScore ?? idea.innovation_score ?? 0;
                  return (
                    <div key={i} className="rounded-lg border p-3">
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <div className="font-medium">{title}</div>
                          <div className="mt-0.5 text-xs text-muted-foreground line-clamp-2">{desc}</div>
                        </div>
                        <div className="shrink-0 text-right">
                          <div className="text-lg font-bold tabular-nums">{typeof score === "number" ? Math.round(score) : score}</div>
                          <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Score</div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}

      {arch && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Architecture</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {arch.vision && <p className="text-muted-foreground">{arch.vision}</p>}
            {arch.features?.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {arch.features.map((f: string, i: number) => (
                  <span key={i} className="rounded-md bg-muted px-2 py-0.5 text-xs">{f}</span>
                ))}
              </div>
            )}
            {arch.userStories?.length > 0 && (
              <div>
                <div className="mb-1 text-xs font-medium text-muted-foreground uppercase tracking-wider">User Stories</div>
                <ul className="list-inside list-disc space-y-0.5 text-xs text-muted-foreground">
                  {arch.userStories.map((s: string, i: number) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            )}
            {arch.architecture && (
              <div>
                <details className="group">
                  <summary className="cursor-pointer text-xs font-medium text-muted-foreground hover:text-foreground">
                    Architecture Details
                  </summary>
                  <pre className="mt-2 overflow-x-auto rounded bg-muted p-3 font-mono text-xs">
                    {JSON.stringify(arch.architecture, null, 2)}
                  </pre>
                </details>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {techStack && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Tech Stack</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {[
              { label: "Frontend", data: techStack.frontend },
              { label: "Backend", data: techStack.backend },
            ].map(({ label, data }) =>
              data ? (
                <div key={label}>
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{label}</span>
                  <div className="mt-0.5 flex flex-wrap gap-1.5">
                    {[...(data.frameworks || []), ...(data.languages || [])].map((item: string, i: number) => (
                      <span key={i} className="rounded-md bg-muted px-2 py-0.5 text-xs">{item}</span>
                    ))}
                  </div>
                </div>
              ) : null
            )}
            {techStack.databases?.length > 0 && (
              <div>
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Databases</span>
                <div className="mt-0.5 flex flex-wrap gap-1.5">
                  {techStack.databases.map((db: string, i: number) => (
                    <span key={i} className="rounded-md bg-muted px-2 py-0.5 text-xs">{db}</span>
                  ))}
                </div>
              </div>
            )}
            {techStack.devops?.length > 0 && (
              <div>
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">DevOps</span>
                <div className="mt-0.5 flex flex-wrap gap-1.5">
                  {techStack.devops.map((item: string, i: number) => (
                    <span key={i} className="rounded-md bg-muted px-2 py-0.5 text-xs">{item}</span>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {prompts?.prompts?.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Build Prompts</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="max-h-[300px]">
              <div className="space-y-2 p-4">
                {prompts.prompts.map((p: { title: string; prompt: string }, i: number) => (
                  <details key={i} className="group rounded-lg border p-3">
                    <summary className="cursor-pointer text-sm font-medium hover:text-foreground">
                      {p.title}
                    </summary>
                    <div className="mt-2 whitespace-pre-wrap rounded bg-muted p-3 font-mono text-xs leading-relaxed text-muted-foreground">
                      {p.prompt}
                    </div>
                  </details>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

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
  const s = (project?.state ?? null) as Dict | null;
  const arch = s?.architecture ?? null;
  const techStack = s?.techStack ?? null;
  const prompts = s?.prompts ?? null;
  const ideas = s?.generatedIdeas ?? [];

  const completedInPipeline = workflowSteps.filter(step => completedSet.has(step.key));
  const progressCount = completedInPipeline.length;

  const selectedLog = agentLogs.find((l: AgentLogEntry) => l.agent === selectedAgent);
  const selectedStateKey = selectedAgent ? STATE_KEYS[selectedAgent] : null;
  const selectedStateValue = selectedStateKey ? s?.[selectedStateKey] : null;

  const statusBadgeVariant =
    project?.status === "completed" ? "default" as const
      : project?.status === "failed" ? "destructive" as const
        : project?.status === "idea_selection" ? "outline" as const
          : "secondary" as const;

  const stage = project?.currentStage || "";
  const statusLabel =
    project?.status === "idea_selection" && stage === "architecture_review" ? "reviewing architecture"
      : project?.status === "idea_selection" && stage === "tech_stack_review" ? "reviewing tech stack"
        : project?.status === "idea_selection" && stage === "prompts_review" ? "reviewing prompts"
          : project?.status === "idea_selection" ? "awaiting selection"
            : project?.status === "researching" ? "running"
              : project?.status || "";

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

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      {/* ── Header ─────────────────────────────────────────────────── */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.push("/projects")} className="shrink-0">
            ←
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{project.name}</h1>
            <div className="mt-0.5 flex items-center gap-2">
              <Badge
                variant={statusBadgeVariant}
                className={(project.status === "researching" || project.status === "idea_selection") ? "animate-pulse" : ""}
              >
                {statusLabel}
              </Badge>
              <span className="text-sm text-muted-foreground">{progressCount}/{workflowSteps.length}</span>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          {(project.status === "draft" || project.status === "idea_selection" || project.status === "failed") && (
            <Button
              onClick={() => startWorkflow.mutate(params.id)}
              disabled={startWorkflow.isPending}
            >
              {startWorkflow.isPending ? "Starting..." : project.status === "draft" ? "Start Analysis" : "Restart"}
            </Button>
          )}
        </div>
      </div>

      {/* ── Progress Bar ───────────────────────────────────────────── */}
      <div className="mb-6">
        <Progress value={(progressCount / workflowSteps.length) * 100} className="h-2" />
        <div className="mt-1 flex justify-between text-xs text-muted-foreground">
          <span>Pipeline progress</span>
          <span>{progressCount}/{workflowSteps.length} steps</span>
        </div>
      </div>

      {/* ── Main Grid ──────────────────────────────────────────────── */}
      <div className="grid gap-6 lg:grid-cols-2 xl:grid-cols-3">
        {/* Left: Agent Pipeline */}
        <div className="xl:col-span-1">
          <h2 className="mb-3 text-lg font-semibold">Pipeline</h2>
          <div className="space-y-1.5">
            {workflowSteps.map((step) => {
              const isCompleted = completedSet.has(step.key);
              const isRunning = currentAgent === step.key;
              const isSelected = selectedAgent === step.key;
              const log = agentLogs.find((l: AgentLogEntry) => l.agent === step.key);
              const hasError = log && !log.success;

              let statusDot = "bg-muted";
              if (isCompleted && !hasError) statusDot = "bg-green-500";
              else if (hasError) statusDot = "bg-destructive";
              else if (isRunning) statusDot = "bg-primary";

              return (
                <button
                  key={step.key}
                  type="button"
                  onClick={() => {
                    if (log) setSelectedAgent(step.key);
                  }}
                  disabled={!log}
                  className={`flex w-full items-center gap-3 rounded-lg border px-4 py-3 text-left transition-all ${
                    isSelected
                      ? "border-primary bg-primary/5 ring-2 ring-primary/20"
                      : isRunning
                        ? "border-primary/50 bg-primary/5 animate-pulse"
                        : "border-border hover:border-primary/30 hover:bg-accent/50"
                  } ${!log ? "opacity-50 cursor-default" : "cursor-pointer"}`}
                >
                  <div className={`h-2.5 w-2.5 shrink-0 rounded-full ${statusDot} ${isRunning ? "animate-pulse" : ""}`} />
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium">{step.label}</div>
                    <div className="text-xs text-muted-foreground">
                      {isRunning ? "Running..." : isCompleted ? `${((log?.durationMs || 0) / 1000).toFixed(1)}s` : "Pending"}
                    </div>
                  </div>
                  {isCompleted && (
                    <svg className="h-4 w-4 shrink-0 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                  {hasError && (
                    <svg className="h-4 w-4 shrink-0 text-destructive" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Right: Context Panel */}
        <div className="xl:col-span-2 space-y-4">
          {/* Agent Detail */}
          {selectedAgent && selectedLog ? (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between border-b py-3">
                <CardTitle className="text-base">Agent Details</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setSelectedAgent(null)}>Close</Button>
              </CardHeader>
              <CardContent className="p-4">
                <AgentDetail
                  agentName={selectedAgent}
                  log={selectedLog}
                  stateValue={selectedStateValue}
                />
              </CardContent>
            </Card>
          ) : null}

          {/* Checkpoints: route by current_stage */}
          {project.status === "idea_selection" && !selectedAgent && project.currentStage === "architecture_review" && (
            <ArchitectureReviewPanel
              arch={arch}
              projectId={project.id}
              onApprove={() => refetch()}
            />
          )}
          {project.status === "idea_selection" && !selectedAgent && project.currentStage === "tech_stack_review" && (
            <TechStackReviewPanel
              techStack={techStack}
              projectId={project.id}
              onApprove={() => refetch()}
            />
          )}
          {project.status === "idea_selection" && !selectedAgent && project.currentStage === "prompts_review" && (
            <PromptsReviewPanel
              prompts={prompts}
              projectId={project.id}
              onApprove={() => refetch()}
            />
          )}

          {/* Idea Selection */}
          {project.status === "idea_selection" && ideas.length > 0 && !selectedAgent && (
            project.currentStage === "idea_selection" || project.currentStage === "" || !project.currentStage
          ) && (
            <IdeaPicker
              ideas={ideas}
              projectId={project.id}
              onSelect={() => refetch()}
              onRegenerate={() => refetch()}
            />
          )}

          {/* Completed Results */}
          {project.status === "completed" && !selectedAgent && (
            <ResultPanel ideas={ideas} arch={arch} techStack={techStack} prompts={prompts} />
          )}

          {/* Failed */}
          {project.status === "failed" && !selectedAgent && (
            <Card className="border-destructive/50 bg-destructive/5">
              <CardHeader>
                <CardTitle className="text-destructive">Workflow Failed</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <p className="text-destructive/80">
                  The workflow could not complete. Select an agent above to see error details.
                </p>
                {errorLog.length > 0 && (
                  <div className="space-y-1.5">
                    {errorLog.map((err, i) => (
                      <div key={i} className="rounded bg-destructive/10 p-3 font-mono text-xs">
                        <div className="font-semibold text-destructive">{err.agentName || "System"}</div>
                        <div className="mt-0.5 text-destructive/80">
                          {err.message.includes("rate_limit") || err.message.includes("429")
                            ? "Rate limit reached. Please wait a few minutes or add a Gemini API key as fallback in your .env file."
                            : err.message}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Live Logs (default when no agent selected) */}
          {!selectedAgent && project.status !== "completed" && project.status !== "failed" && !(project.status === "idea_selection" && project.currentStage) && (
            <Card>
              <CardHeader className="border-b py-3">
                <CardTitle className="text-base">Live Logs</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <LogPanel logs={agentLogs} errors={errorLog} onSelect={setSelectedAgent} />
              </CardContent>
            </Card>
          )}

          {/* Prompt to select an agent */}
          {!selectedAgent && agentLogs.length > 0 && (project.status === "completed" || project.status === "idea_selection") && (
            <div className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
              Click an agent in the pipeline to inspect its output.
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
