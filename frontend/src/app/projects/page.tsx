"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { accessKey, api, restoreAccessKey, type Project } from "@/services/api";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [showAccess, setShowAccess] = useState(false);
  const [key, setKey] = useState("");
  const [deleting, setDeleting] = useState("");
  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api<{ projects: Project[] }>("/projects");
      setProjects(data.projects);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load projects.");
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    let cancelled = false;
    api<{ projects: Project[] }>("/projects")
      .then((data) => {
        if (!cancelled) setProjects(data.projects);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);
  return (
    <main className="studio-container">
      <header className="section-heading">
        <Link href="/" className="brand">
          <span className="brand-mark">ex</span>Hacker
        </Link>
        <Link href="/projects/new" className="btn btn-lime">
          + New project
        </Link>
      </header>
      <div className="projects-heading">
        <span className="eyebrow">YOUR PRIVATE WORKSPACE</span>
        <h1>Ideas worth following through.</h1>
        <p className="muted">
          Pick up where you left off. Every research round, decision, and
          document stays with its project.
        </p>
      </div>
      <button
        className="text-button"
        onClick={() => setShowAccess(!showAccess)}
      >
        Workspace access & recovery
      </button>
      {showAccess && (
        <section className="studio-card">
          <h2>Keep access to your projects.</h2>
          <p className="muted">
            This anonymous workspace belongs to a secret key stored in this
            browser. Save it privately to restore access on another device.
            Anyone with this key can access your projects.
          </p>
          <button
            className="btn btn-ghost"
            onClick={async () => {
              try {
                await navigator.clipboard.writeText(accessKey());
                setNotice("Workspace key copied. Store it privately.");
              } catch {
                setError(
                  "Clipboard unavailable. Enable clipboard permission and retry.",
                );
              }
            }}
          >
            Copy my workspace key
          </button>
          <form
            onSubmit={(event) => {
              event.preventDefault();
              try {
                restoreAccessKey(key);
                setKey("");
                setNotice("Workspace key restored.");
                void load();
              } catch (err) {
                setError(err instanceof Error ? err.message : "Invalid key.");
              }
            }}
          >
            <label htmlFor="restore-key">Restore another workspace</label>
            <input
              id="restore-key"
              className="field"
              type="password"
              required
              pattern="[0-9a-f]{64}"
              maxLength={64}
              autoComplete="off"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="Paste your saved workspace key"
            />
            <button className="btn btn-ghost">Restore workspace</button>
          </form>
        </section>
      )}
      {notice && (
        <div className="notice success" role="status">
          {notice}
        </div>
      )}
      {error && (
        <div className="notice error" role="alert">
          {error}
          <button className="text-button" onClick={() => void load()}>
            Retry
          </button>
        </div>
      )}
      {loading ? (
        <div className="empty-panel" role="status">
          Loading your projects…
        </div>
      ) : !error && !projects.length ? (
        <div className="empty-panel">
          <h2>Your next project starts with a question.</h2>
          <p className="muted">
            Bring a challenge or an early idea. Leave with a direction your team
            can build.
          </p>
          <Link href="/projects/new" className="btn btn-primary">
            Create your first project →
          </Link>
        </div>
      ) : (
        <div className="project-list">
          {projects.map((project) => (
            <article className="studio-card project-list-card" key={project.id}>
              <Link
                className="project-card-link"
                href={`/projects/${project.id}`}
              >
                <div className="section-heading">
                  <h2>{project.name}</h2>
                  <span className="badge badge-blue">
                    {project.active_job
                      ? "Working"
                      : project.state.replaceAll("_", " ")}
                  </span>
                </div>
                <p className="muted">{project.intake.idea.slice(0, 220)}</p>
                <p className="small muted">
                  {project.intake.teammates.length} builder(s) ·{" "}
                  {project.intake.available_hours}h · Updated{" "}
                  {new Date(project.updated_at).toLocaleDateString()}
                </p>
              </Link>
              <button
                className="text-button danger-button"
                disabled={!!project.active_job || !!deleting}
                onClick={async () => {
                  if (
                    !window.confirm(
                      `Permanently delete “${project.name}” and all its research, documents, and conversations?`,
                    )
                  )
                    return;
                  setDeleting(project.id);
                  try {
                    await api(
                      `/projects/${project.id}?revision=${project.revision}`,
                      "DELETE",
                    );
                    await load();
                  } catch (err) {
                    setError(
                      err instanceof Error
                        ? err.message
                        : "Could not delete project.",
                    );
                  } finally {
                    setDeleting("");
                  }
                }}
              >
                {deleting === project.id ? "Deleting…" : "Delete project"}
              </button>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
