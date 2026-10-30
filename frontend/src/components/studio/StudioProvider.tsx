"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import {
  api,
  type Configuration,
  type Job,
  type Project,
} from "@/services/api";
import CommandPalette from "@/components/shared/CommandPalette";

type Studio = {
  project: Project;
  config: Configuration | null;
  jobs: Job[];
  busy: boolean;
  refresh: () => Promise<void>;
  act: (path: string, body: unknown, method?: string) => Promise<boolean>;
};
const Context = createContext<Studio | null>(null);
export function useStudio() {
  const value = useContext(Context);
  if (!value) throw new Error("Missing studio provider");
  return value;
}

const sections = [
  ["overview", "Brief"],
  ["ideas", "Ideas"],
  ["stack", "Tech stack"],
  ["docs", "Documents"],
  ["chat", "Assistant"],
  ["research", "Research"],
  ["history", "History"],
];

export default function StudioProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const { id } = useParams<{ id: string }>();
  const pathname = usePathname();
  const [project, setProject] = useState<Project | null>(null);
  const [config, setConfig] = useState<Configuration | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [connectionError, setConnectionError] = useState("");
  const [notice, setNotice] = useState("");
  const requestNumber = useRef(0);

  const refresh = useCallback(async () => {
    const number = ++requestNumber.current;
    try {
      const [next, jobData] = await Promise.all([
        api<Project>(`/projects/${id}`),
        api<{ jobs: Job[] }>(`/projects/${id}/jobs`),
      ]);
      if (number === requestNumber.current) {
        setProject(next);
        setJobs(jobData.jobs);
        setConnectionError("");
      }
    } catch (err) {
      if (number === requestNumber.current)
        setConnectionError(
          err instanceof Error ? err.message : "Could not load this project.",
        );
    }
  }, [id]);

  useEffect(() => {
    let stopped = false;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      await refresh();
      if (!stopped) timer = setTimeout(poll, 1500);
    }
    void poll();
    api<Configuration>("/config")
      .then(setConfig)
      .catch(() => undefined);
    return () => {
      stopped = true;
      clearTimeout(timer);
    };
  }, [refresh]);

  const act = useCallback(
    async (path: string, body: unknown, method = "POST") => {
      setSaving(true);
      setError("");
      setNotice("");
      try {
        await api(path, method, body);
        await refresh();
        setNotice("Saved. Your project is up to date.");
        return true;
      } catch (err) {
        setError(err instanceof Error ? err.message : "The operation failed.");
        return false;
      } finally {
        setSaving(false);
      }
    },
    [refresh],
  );

  if (!project)
    return (
      <main className="studio-container">
        <Link href="/projects" className="text-link">
          ← Projects
        </Link>
        <div className="studio-card">
          {connectionError ? (
            <div role="alert">
              <p>{connectionError}</p>
              <button
                className="btn btn-primary"
                onClick={() => void refresh()}
              >
                Try again
              </button>
            </div>
          ) : (
            <p role="status">Loading your project…</p>
          )}
        </div>
      </main>
    );
  const active = jobs.find((j) => j.id === project.active_job);
  const latest = jobs[0];
  const busy = saving || !!project.active_job;
  const chosen = project.context.ideas?.find(
    (i) => i.id === project.context.selected_idea_id,
  );
  const completed = [
    !!project.context.ideas?.length,
    !!chosen,
    !!project.context.stack_confirmed,
    !!project.context.documents,
  ];

  return (
    <Context.Provider value={{ project, config, jobs, busy, refresh, act }}>
      <div className="workspace-shell">
        <header className="workspace-header">
          <Link href="/" className="brand">
            <span className="brand-mark">ex</span>Hacker
          </Link>
          <Link href="/projects" className="text-link">
            ← Projects
          </Link>
          <div className="project-heading">
            <strong>{project.name}</strong>
            <span className="muted">
              Revision {project.revision} · {project.state.replaceAll("_", " ")}
            </span>
          </div>
          <span className="keyboard-hint">Ctrl K</span>
        </header>
        <div className="workspace-body">
          <aside className="workspace-sidebar">
            <span className="eyebrow">YOUR BUILD STUDIO</span>
            <h2>
              From possibility
              <br />
              <span className="accent-lime">to a clear plan.</span>
            </h2>
            <ol className="milestones">
              {[
                "Five evaluated ideas",
                "Your direction confirmed",
                "Technology stack approved",
                "Implementation handoff ready",
              ].map((label, index) => (
                <li key={label} className={completed[index] ? "complete" : ""}>
                  <span>{completed[index] ? "✓" : `0${index + 1}`}</span>
                  {label}
                </li>
              ))}
            </ol>
            <div className="sidebar-context">
              <span className="eyebrow">TEAM CONTEXT</span>
              <p>
                <strong>{project.intake.available_hours}h</strong> available
              </p>
              <p>
                <strong>{project.intake.teammates.length}</strong>{" "}
                {project.intake.teammates.length === 1 ? "builder" : "builders"}
              </p>
              <p className="muted">
                {project.intake.teammates.map((m) => m.name).join(", ")}
              </p>
              {!config?.demo && (
                <p className="small muted">
                  Estimated AI spend: ${project.ai_cost.toFixed(3)} / $
                  {config?.cost_limit ?? "—"}
                  <br />
                  Search queries: {project.search_count}
                </p>
              )}
            </div>
            <p className="small muted">
              Your saved work stays in this browser&apos;s private workspace.
            </p>
          </aside>
          <main className="workspace-main">
            <nav className="workspace-nav" aria-label="Project sections">
              {sections.map(([key, label]) => (
                <Link
                  key={key}
                  href={`/projects/${id}/${key}`}
                  className={pathname.endsWith(`/${key}`) ? "active" : ""}
                  aria-current={
                    pathname.endsWith(`/${key}`) ? "page" : undefined
                  }
                >
                  {label}
                </Link>
              ))}
            </nav>
            <div className="workspace-content">
              {(config?.demo || project.context.demo) && (
                <div className="notice warning" role="status">
                  Demonstration mode · No live research or AI validation. Scores
                  and documents are illustrative.
                </div>
              )}
              {config &&
                !config.demo &&
                (!config.ai_configured || !config.research_configured) && (
                  <div className="notice warning">
                    Live generation needs{" "}
                    {(!config.ai_configured ? ["an AI provider"] : [])
                      .concat(
                        !config.research_configured ? ["Tavily search"] : [],
                      )
                      .join(" and ")}{" "}
                    configured on the server. Your project remains saved.
                  </div>
                )}
              {connectionError && (
                <div className="notice error" role="alert">
                  {connectionError}{" "}
                  <button
                    className="text-button"
                    onClick={() => void refresh()}
                  >
                    Reconnect
                  </button>
                </div>
              )}
              {error && (
                <div className="notice error" role="alert">
                  {error}{" "}
                  <button
                    className="text-button"
                    aria-label="Dismiss error"
                    onClick={() => setError("")}
                  >
                    ×
                  </button>
                </div>
              )}
              {notice && !busy && (
                <div className="notice success" role="status">
                  {notice}
                  <button
                    className="text-button"
                    aria-label="Dismiss saved notification"
                    onClick={() => setNotice("")}
                  >
                    ×
                  </button>
                </div>
              )}
              {project.active_job && (
                <div className="job-panel" role="status" aria-live="polite">
                  <div className="section-heading">
                    <strong>
                      <span className="working-dot" />{" "}
                      {active?.kind.replaceAll("_", " ") || "Operation"}{" "}
                      {active?.status === "running" ? "in progress" : "queued"}
                    </strong>
                    <span className="small muted">
                      Safe to navigate or return later
                    </span>
                  </div>
                  {active?.events.slice(-5).map((event, index) => (
                    <p key={`${event.at}-${index}`} className="small">
                      {event.message}
                    </p>
                  ))}
                  {config && !config.worker_enabled && (
                    <p className="notice warning">
                      The server worker is disabled. Start the worker to process
                      this saved operation.
                    </p>
                  )}
                </div>
              )}
              {!project.active_job && latest?.status === "failed" && (
                <div className="notice error" role="alert">
                  <div>
                    <strong>
                      {latest.kind.replaceAll("_", " ")} did not finish.
                    </strong>
                    <p>{latest.error}</p>
                  </div>
                  <button
                    className="btn btn-ghost"
                    disabled={busy}
                    onClick={() =>
                      void act(`/projects/${id}/jobs/${latest.id}/retry`, {
                        revision: project.revision,
                      })
                    }
                  >
                    Retry
                  </button>
                </div>
              )}
              {children}
            </div>
          </main>
        </div>
        <CommandPalette projectId={id} />
      </div>
    </Context.Provider>
  );
}
