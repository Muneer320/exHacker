"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type Artifact } from "@/services/api";
import IntakeForm from "./IntakeForm";
import { useStudio } from "./StudioProvider";

export function BriefPanel() {
  const { project, busy, act } = useStudio();
  const [editing, setEditing] = useState(false);
  if (editing)
    return (
      <div>
        <div className="section-heading">
          <h1>Update the project brief.</h1>
          <button
            className="btn btn-ghost"
            disabled={busy}
            onClick={() => setEditing(false)}
          >
            Cancel
          </button>
        </div>
        <div className="notice warning">
          Saving a changed brief resets idea and stack approvals and invalidates
          the current documents. Previous snapshots and conversations remain in
          History.
        </div>
        <IntakeForm
          initial={project.intake}
          submitLabel="Save updated brief"
          onSubmit={async (intake) => {
            if (
              await act(
                `/projects/${project.id}`,
                { revision: project.revision, intake },
                "PATCH",
              )
            )
              setEditing(false);
            else
              throw new Error(
                "The brief was not saved. Check the error above.",
              );
          }}
        />
      </div>
    );
  const next = project.context.documents
    ? ["chat", "Ask your assistant"]
    : project.context.stack_confirmed
      ? ["docs", "Open the documentation phase"]
      : project.context.selected_idea_id
        ? ["stack", "Review your technology stack"]
        : ["ideas", "Explore your ideas"];
  return (
    <div>
      <span className="eyebrow">THE PROJECT BRIEF</span>
      <div className="section-heading">
        <h1>{project.name}</h1>
        <button
          className="btn btn-ghost"
          disabled={busy}
          onClick={() => setEditing(true)}
        >
          Edit brief
        </button>
      </div>
      <div className="studio-card">
        <h2>What we&apos;re working toward</h2>
        <p className="preserve-lines">{project.intake.idea}</p>
      </div>
      <div className="stack-grid">
        <div className="studio-card">
          <span className="eyebrow">THE CONSTRAINTS</span>
          <h2>{project.intake.available_hours} hours</h2>
          <p>{project.intake.hackathon || "Hackathon name not supplied"}</p>
          <p>Platform: {project.intake.target_platform}</p>
          <p>Budget: {project.intake.budget || "Not specified"}</p>
        </div>
        <div className="studio-card">
          <span className="eyebrow">THE TEAM</span>
          {project.intake.teammates.map((member) => (
            <div key={member.name} className="team-summary">
              <strong>{member.name}</strong>
              <span className="small muted">
                {member.role || "Builder"} ·{" "}
                {member.hours_available || project.intake.available_hours}h
              </span>
              <p>
                {member.skills
                  .map((skill) => `${skill.technology} (${skill.proficiency})`)
                  .join(", ")}
              </p>
            </div>
          ))}
        </div>
      </div>
      {(
        [
          ["judging_criteria", "What the judges care about"],
          ["rules", "Rules"],
          ["required_technologies", "Required technologies"],
          ["preferred_technologies", "Preferred technologies"],
          ["excluded_technologies", "Technologies to avoid"],
          ["constraints", "Additional context"],
        ] as const
      )
        .filter(([key]) => project.intake[key])
        .map(([key, title]) => (
          <div className="studio-card" key={key}>
            <h2>{title}</h2>
            <p className="preserve-lines">{project.intake[key]}</p>
          </div>
        ))}
      <Link
        href={`/projects/${project.id}/${next[0]}`}
        className="btn btn-lime"
      >
        {next[1]} →
      </Link>
    </div>
  );
}

export function ResearchPanel() {
  const { project } = useStudio();
  const report = project.context.research;
  return (
    <div>
      <span className="eyebrow">THE EVIDENCE BEHIND THE IDEAS</span>
      <h1>Research you can inspect.</h1>
      <p className="muted">
        Sources are retrieved during the idea cycle. Search coverage is
        incomplete; a missing competitor does not prove originality.
      </p>
      {report?.warnings.map((warning) => (
        <div className="notice warning" key={warning}>
          {warning}
        </div>
      ))}
      {!report?.sources.length ? (
        <div className="empty-panel">
          <h2>No live evidence yet.</h2>
          <p className="muted">
            Run the idea cycle with live search configured to collect supporting
            sources.
          </p>
          <Link
            className="btn btn-primary"
            href={`/projects/${project.id}/ideas`}
          >
            Go to Ideas →
          </Link>
        </div>
      ) : (
        <>
          <p className="small muted">
            {report.sources.length} unique sources · {report.queries.length}{" "}
            queries
          </p>
          <div className="research-grid">
            {report.sources.map((source) => (
              <article className="studio-card" key={source.id}>
                <span className="eyebrow">{source.id}</span>
                <h2>
                  <a
                    className="text-link"
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {source.title} ↗
                  </a>
                </h2>
                <p>{source.snippet}</p>
                <details>
                  <summary>Search provenance</summary>
                  <p className="small">Query: {source.query}</p>
                  <p className="small muted">
                    Retrieved {new Date(source.retrieved_at).toLocaleString()}
                  </p>
                </details>
              </article>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export function HistoryPanel() {
  const { project, jobs } = useStudio();
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [snapshot, setSnapshot] = useState("");
  const [error, setError] = useState("");
  const [loadingId, setLoadingId] = useState("");
  useEffect(() => {
    let cancelled = false;
    api<{ artifacts: Artifact[] }>(`/projects/${project.id}/history`)
      .then((data) => {
        if (!cancelled) setArtifacts(data.artifacts);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [project.id, project.revision]);
  return (
    <div>
      <span className="eyebrow">SAVED DECISIONS & VERSIONS</span>
      <h1>See how the plan evolved.</h1>
      <p className="muted">
        Approvals, research rounds, generated artifacts, and operation failures
        are saved. Older versions remain inspectable after changes.
      </p>
      {error && (
        <div className="notice error" role="alert">
          {error}
        </div>
      )}
      <div className="stack-grid">
        <div>
          <h2>Project versions</h2>
          {!artifacts.length && (
            <p className="muted">Versions appear as operations complete.</p>
          )}
          {artifacts.map((artifact) => (
            <article className="history-entry" key={artifact.id}>
              <span className="eyebrow">REVISION {artifact.revision}</span>
              <strong>{artifact.kind.replaceAll("_", " ")}</strong>
              <span className="small muted">
                {new Date(artifact.created_at).toLocaleString()}
              </span>
              <button
                className="text-button"
                disabled={!!loadingId}
                onClick={async () => {
                  setLoadingId(artifact.id);
                  try {
                    const data = await api<{ content: unknown }>(
                      `/projects/${project.id}/history/${artifact.id}`,
                    );
                    setSnapshot(JSON.stringify(data.content, null, 2));
                  } catch (err) {
                    setError(
                      err instanceof Error
                        ? err.message
                        : "Could not load snapshot.",
                    );
                  } finally {
                    setLoadingId("");
                  }
                }}
              >
                {loadingId === artifact.id
                  ? "Loading…"
                  : "Inspect saved snapshot"}
              </button>
            </article>
          ))}
        </div>
        <div>
          <h2>Operation log</h2>
          {jobs.map((job) => (
            <article key={job.id} className="history-entry">
              <strong>
                {job.kind.replaceAll("_", " ")} · {job.status}
              </strong>
              <span className="small muted">
                {new Date(job.created_at).toLocaleString()} · {job.attempts}{" "}
                attempt(s)
              </span>
              {job.events.map((event, i) => (
                <p className="small" key={i}>
                  {event.message}
                </p>
              ))}
              {job.error && <p className="error-text">{job.error}</p>}
            </article>
          ))}
        </div>
      </div>
      {snapshot && (
        <div className="studio-card">
          <div className="section-heading">
            <h2>Saved snapshot</h2>
            <button className="text-button" onClick={() => setSnapshot("")}>
              Close
            </button>
          </div>
          <pre className="markdown-source">{snapshot}</pre>
        </div>
      )}
    </div>
  );
}
