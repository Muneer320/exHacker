"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { AgentLogEntry } from "@/types";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Dict = Record<string, any>;

const AGENT_DESCRIPTIONS: Record<string, string> = {
  user_profiler:
    "Analyzes team composition, skills, experience level, and constraints to build a team profile that guides scope and complexity decisions throughout the hackathon.",
  challenge_intelligence:
    "Researches the hackathon challenge statement, themes, evaluation criteria, and available resources to surface opportunities and constraints.",
  problem_analyst:
    "Deep-dives into the challenge space, identifying pain points, user needs, and technical hurdles to scope a well-defined problem worth solving.",
  opportunity_planner:
    "Maps out opportunities by combining challenge intelligence with team strengths, identifying high-impact areas where the team can differentiate.",
  idea_generator:
    "Brainstorms 5 distinct hackathon project ideas with structured scoring across innovation, feasibility, hackathon fit, and technical wow factor.",
  idea_validator:
    "Evaluates all generated ideas against team capability and challenge constraints, producing validation reports with scores, risks, and strengths.",
  solution_architect:
    "Designs the system architecture (vision, features, user stories, API design, database schema, integrations) AND recommends a tech stack.",
  tech_stack_advisor:
    "Recommends specific technologies (frontend, backend, database, hosting, AI models, vector DB, auth) aligned with architecture and team skills.",
  build_accelerator:
    "Generates detailed, actionable build prompts and code snippets for each component of the architecture to accelerate implementation.",
  presentation_agent:
    "Creates presentation slides, architecture diagrams, and a compelling demo story narrative for the final pitch.",
  pitch_coach:
    "Coaches the team on pitch delivery, generating 30-second, 2-minute, and 5-minute pitch scripts with Q&A practice questions.",
};

const AGENT_INPUT_KEYS: Record<string, string[]> = {
  user_profiler: ["project"],
  challenge_intelligence: ["project"],
  problem_analyst: ["teamProfile", "challengeIntelligence"],
  opportunity_planner: ["problemAnalysis", "challengeIntelligence"],
  idea_generator: ["problemAnalysis", "opportunityAnalysis", "teamProfile", "challengeIntelligence"],
  idea_validator: ["generatedIdeas", "teamProfile"],
  solution_architect: ["selectedIdea", "generatedIdeas", "teamProfile", "project"],
  tech_stack_advisor: ["architecture", "teamProfile", "challengeIntelligence", "project"],
  build_accelerator: ["architecture", "techStack"],
  presentation_agent: ["architecture", "generatedIdeas", "selectedIdea", "validationReports"],
  pitch_coach: ["presentation"],
};

const AGENT_CHECKPOINT_STAGES: Record<string, string> = {
  solution_architect: "architecture_review",
  tech_stack_advisor: "tech_stack_review",
  build_accelerator: "prompts_review",
};

function formatOutput(val: unknown, depth = 0): string {
  const indent = "  ".repeat(depth);
  if (Array.isArray(val)) {
    if (val.length === 0) return "[]";
    return val
      .map(item => {
        if (typeof item === "object" && item !== null) {
          const entries = Object.entries(item)
            .filter(([k]) => !["id"].includes(k))
            .map(([k, v]) => {
              const label = k.replace(/([A-Z])/g, " $1").replace(/^./, s => s.toUpperCase());
              if (Array.isArray(v)) return `${indent}  ${label}: ${v.join(", ")}`;
              if (typeof v === "object" && v !== null)
                return `${indent}  ${label}: ${JSON.stringify(v)}`;
              return `${indent}  ${label}: ${v}`;
            })
            .join("\n");
          return `${indent}- ${entries}`;
        }
        return `${indent}- ${String(item)}`;
      })
      .join("\n");
  }
  if (typeof val === "object" && val !== null) {
    return Object.entries(val)
      .filter(([k]) => !["id"].includes(k))
      .map(([k, v]) => {
        const label = k.replace(/([A-Z])/g, " $1").replace(/^./, s => s.toUpperCase());
        if (Array.isArray(v)) return `${indent}${label}: ${v.join(", ")}`;
        if (typeof v === "object" && v !== null)
          return `${indent}${label}: ${JSON.stringify(v, null, 2)}`;
        return `${indent}${label}: ${v}`;
      })
      .join("\n");
  }
  return String(val);
}

function ValueCard({ title, value }: { title: string; value: unknown }) {
  if (value === null || value === undefined || (Array.isArray(value) && value.length === 0)) {
    return null;
  }
  return (
    <div>
      <div className="mb-1 text-xs font-medium text-muted-foreground uppercase tracking-wider">
        {title}
      </div>
      <div className="max-h-48 overflow-y-auto rounded bg-muted/50 p-2">
        <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed">
          {formatOutput(value)}
        </pre>
      </div>
    </div>
  );
}

function InputTab({
  agentKey,
  state,
}: {
  agentKey: string;
  state: Dict | null;
}) {
  const inputKeys = AGENT_INPUT_KEYS[agentKey] ?? [];
  const relevantKeys = inputKeys.filter(k => state?.[k] !== undefined && state?.[k] !== null);

  if (relevantKeys.length === 0) {
    return (
      <div className="flex h-24 items-center justify-center text-sm text-muted-foreground">
        No input data available.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {relevantKeys.map(key => (
        <ValueCard key={key} title={key.replace(/([A-Z])/g, " $1").replace(/^./, s => s.toUpperCase())} value={state?.[key]} />
      ))}
    </div>
  );
}

function OutputTab({
  agentKey,
  stateValue,
  state,
}: {
  agentKey: string;
  stateValue: unknown;
  state: Dict | null;
}) {
  const checkpointStage = AGENT_CHECKPOINT_STAGES[agentKey];

  if (!stateValue) {
    return (
      <div className="flex h-24 items-center justify-center text-sm text-muted-foreground">
        No output yet.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <ValueCard title="Output" value={stateValue} />
      {checkpointStage && state?.checkpointApprovals?.[checkpointStage] !== undefined && (
        <div className="rounded border p-2 text-xs">
          <span className="font-medium">Checkpoint:</span>{" "}
          {state.checkpointApprovals[checkpointStage] ? (
            <span className="text-green-600">Approved</span>
          ) : (
            <span className="text-amber-600">Pending approval</span>
          )}
        </div>
      )}
    </div>
  );
}

function AboutTab({ agentKey }: { agentKey: string }) {
  const description = AGENT_DESCRIPTIONS[agentKey] ?? "No description available.";
  const inputKeys = AGENT_INPUT_KEYS[agentKey] ?? [];
  const checkpointStage = AGENT_CHECKPOINT_STAGES[agentKey];

  return (
    <div className="space-y-3 text-sm">
      <div>
        <div className="mb-1 text-xs font-medium text-muted-foreground uppercase tracking-wider">
          What this agent does
        </div>
        <p className="leading-relaxed text-foreground/80">{description}</p>
      </div>
      {inputKeys.length > 0 && (
        <div>
          <div className="mb-1 text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Consumes
          </div>
          <div className="flex flex-wrap gap-1.5">
            {inputKeys.map(key => (
              <span key={key} className="rounded-md bg-muted px-2 py-0.5 text-xs">
                {key.replace(/([A-Z])/g, " $1").replace(/^./, s => s.toUpperCase())}
              </span>
            ))}
          </div>
        </div>
      )}
      {checkpointStage && (
        <div>
          <div className="mb-1 text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Checkpoint
          </div>
          <p className="leading-relaxed text-foreground/80">
            This agent requires human approval before the pipeline continues. Review the output
            carefully before approving.
          </p>
        </div>
      )}
    </div>
  );
}

function LogsTab({ log }: { log?: AgentLogEntry }) {
  if (!log) {
    return (
      <div className="flex h-24 items-center justify-center text-sm text-muted-foreground">
        No logs available.
      </div>
    );
  }
  return (
    <div className="grid grid-cols-2 gap-2 text-sm">
      <div className="rounded bg-muted p-2">
        <div className="text-xs text-muted-foreground">Duration</div>
        <div className="font-medium">{((log.durationMs ?? 0) / 1000).toFixed(1)}s</div>
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
          <div className="font-medium">
            {log.inputTokens} → {log.outputTokens}
          </div>
        </div>
      )}
      {log.startedAt && (
        <div className="rounded bg-muted p-2">
          <div className="text-xs text-muted-foreground">Started</div>
          <div className="font-medium text-xs">
            {new Date(log.startedAt).toLocaleString()}
          </div>
        </div>
      )}
      {!log.success && log.error && (
        <div className="col-span-2 rounded bg-destructive/10 p-2 text-xs">
          <div className="mb-0.5 font-medium text-destructive">Error</div>
          <div className="whitespace-pre-wrap font-mono text-destructive/80">
            {log.error}
          </div>
        </div>
      )}
    </div>
  );
}

function QATab({ stateValue }: { stateValue: unknown }) {
  let qaList: Array<{ question: string; answer: string }> = [];

  if (stateValue && typeof stateValue === "object" && !Array.isArray(stateValue)) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const v = stateValue as Record<string, any>;
    if (v.qa && Array.isArray(v.qa)) {
      qaList = v.qa;
    } else if (v.questions && Array.isArray(v.questions)) {
      qaList = v.questions;
    } else if (v.pitchQuestions && Array.isArray(v.pitchQuestions)) {
      qaList = v.pitchQuestions;
    }
  }

  if (qaList.length === 0) {
    return (
      <div className="flex h-24 items-center justify-center text-sm text-muted-foreground">
        No questions available.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {qaList.map((qa, i) => (
        <div key={i} className="rounded-lg border p-3">
          <div className="mb-1 text-xs font-medium text-foreground/80">
            Q: {qa.question}
          </div>
          <div className="text-xs text-muted-foreground leading-relaxed">
            A: {qa.answer}
          </div>
        </div>
      ))}
    </div>
  );
}

export function AgentTabs({
  agentKey,
  agentLabel,
  log,
  stateValue,
  state,
  showApproval,
  onApprove,
  approving,
}: {
  agentKey: string;
  agentLabel: string;
  log?: AgentLogEntry;
  stateValue: unknown;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  state: Record<string, any> | null;
  showApproval: boolean;
  onApprove: () => void;
  approving: boolean;
}) {
  const hasOutput = stateValue !== null && stateValue !== undefined;
  const hasQA =
    hasOutput &&
    typeof stateValue === "object" &&
    !Array.isArray(stateValue) &&
    ((stateValue as Dict)?.qa?.length > 0 ||
      (stateValue as Dict)?.questions?.length > 0 ||
      (stateValue as Dict)?.pitchQuestions?.length > 0);
  const hasInput = AGENT_INPUT_KEYS[agentKey]?.some(k => state?.[k] !== undefined);

  const tabs = [
    { id: "about", label: "About" },
    { id: "input", label: "Input", disabled: !hasInput },
    { id: "output", label: "Output", disabled: !hasOutput },
    { id: "logs", label: "Logs" },
    { id: "qa", label: "Q&A", disabled: !hasQA },
  ].filter(t => !t.disabled);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between border-b py-3">
        <div className="flex items-center gap-2">
          <CardTitle className="text-base">{agentLabel}</CardTitle>
          {log && (
            <Badge variant={log.success ? "default" : "destructive"} className="text-[10px]">
              {log.success ? "Success" : "Failed"}
            </Badge>
          )}
        </div>
        {showApproval && (
          <button
            type="button"
            onClick={onApprove}
            disabled={approving}
            className="inline-flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground shadow transition-all hover:bg-primary/90 disabled:opacity-50"
          >
            {approving ? "Approving..." : "Approve & Continue"}
          </button>
        )}
      </CardHeader>
      <CardContent className="p-0">
        <Tabs defaultValue={tabs[0]?.id ?? "about"} className="p-4 pt-2">
          <TabsList className="mb-3">
            {tabs.map(t => (
              <TabsTrigger key={t.id} value={t.id}>
                {t.label}
              </TabsTrigger>
            ))}
          </TabsList>
          <TabsContent value="about" className="mt-0">
            <AboutTab agentKey={agentKey} />
          </TabsContent>
          <TabsContent value="input" className="mt-0">
            <ScrollArea className="max-h-80">
              <InputTab agentKey={agentKey} state={state} />
            </ScrollArea>
          </TabsContent>
          <TabsContent value="output" className="mt-0">
            <ScrollArea className="max-h-80">
              <OutputTab agentKey={agentKey} stateValue={stateValue} state={state} />
            </ScrollArea>
          </TabsContent>
          <TabsContent value="logs" className="mt-0">
            <LogsTab log={log} />
          </TabsContent>
          <TabsContent value="qa" className="mt-0">
            <ScrollArea className="max-h-80">
              <QATab stateValue={stateValue} />
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
