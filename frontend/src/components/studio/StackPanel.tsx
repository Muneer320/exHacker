"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { Stack } from "@/services/api";
import { useStudio } from "./StudioProvider";

export default function StackPanel() {
  const { project, busy, act } = useStudio();
  const router = useRouter();
  const [editing, setEditing] = useState<Stack | null>(null);
  const [feedback, setFeedback] = useState("");
  const stack = project.context.stack;
  const path = `/projects/${project.id}`;
  if (!project.context.selected_idea_id)
    return (
      <div className="empty-panel">
        <span className="eyebrow">02 / TECHNICAL DIRECTION</span>
        <h1>Choose the idea first.</h1>
        <p className="muted">
          The stack should serve your chosen product and your team&apos;s
          strengths.
        </p>
        <Link href={`${path}/ideas`} className="btn btn-primary">
          Review your ideas →
        </Link>
      </div>
    );

  return (
    <div>
      <div className="section-heading">
        <div>
          <span className="eyebrow">02 / TECHNICAL DIRECTION</span>
          <h1>Your stack. Your call.</h1>
          <p className="muted">
            See what belongs where, understand the trade-offs, and change the
            choices before you commit.
          </p>
        </div>
        {project.context.stack_confirmed && (
          <span className="badge badge-lime">Confirmed</span>
        )}
      </div>
      {!stack ? (
        <div className="empty-panel">
          <h2>
            {busy
              ? "Designing a stack for your idea…"
              : "Turn your idea into a technical plan."}
          </h2>
          <p className="muted">
            Recommendations consider individual skills, available time, and
            hackathon requirements.
          </p>
          <button
            disabled={busy}
            className="btn btn-primary"
            onClick={() =>
              void act(`${path}/jobs`, {
                kind: "stack",
                revision: project.revision,
              })
            }
          >
            Suggest my technology stack →
          </button>
        </div>
      ) : (
        <>
          <div className="studio-card">
            <p>{stack.summary}</p>
          </div>
          <div className="stack-grid">
            {(editing || stack).choices.map((choice, index) => (
              <article
                className="studio-card"
                key={`${choice.category}-${index}`}
              >
                <span className="eyebrow">{choice.category}</span>
                {editing ? (
                  <>
                    <label htmlFor={`technology-${index}`}>Technology</label>
                    <input
                      id={`technology-${index}`}
                      className="field"
                      required
                      minLength={2}
                      maxLength={200}
                      value={choice.technology}
                      onChange={(e) =>
                        setEditing((current) =>
                          current
                            ? {
                                ...current,
                                choices: current.choices.map((c, i) =>
                                  i === index
                                    ? { ...c, technology: e.target.value }
                                    : c,
                                ),
                              }
                            : null,
                        )
                      }
                    />
                  </>
                ) : (
                  <h2>{choice.technology}</h2>
                )}
                <p>{choice.purpose}</p>
                <p className="muted">{choice.rationale}</p>
                <details>
                  <summary>Alternatives & trade-offs</summary>
                  <p className="small">
                    Alternatives: {choice.alternatives.join(", ")}
                  </p>
                  <ul>
                    {choice.tradeoffs.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </details>
              </article>
            ))}
          </div>
          <div className="card-actions">
            {editing ? (
              <>
                <button
                  className="btn btn-primary"
                  disabled={
                    busy ||
                    editing.choices.some((c) => c.technology.trim().length < 2)
                  }
                  onClick={async () => {
                    if (
                      await act(
                        `${path}/stack`,
                        { revision: project.revision, stack: editing },
                        "PUT",
                      )
                    )
                      setEditing(null);
                  }}
                >
                  Apply changes & review compatibility
                </button>
                <button
                  className="btn btn-ghost"
                  disabled={busy}
                  onClick={() => setEditing(null)}
                >
                  Cancel edits
                </button>
              </>
            ) : (
              <button
                className="btn btn-ghost"
                disabled={busy}
                onClick={() => setEditing(structuredClone(stack))}
              >
                Edit technology choices
              </button>
            )}
          </div>
          <form
            className="studio-card"
            onSubmit={async (event) => {
              event.preventDefault();
              if (
                await act(`${path}/jobs`, {
                  kind: "stack",
                  revision: project.revision,
                  prompt: feedback,
                })
              )
                setFeedback("");
            }}
          >
            <label htmlFor="stack-feedback">
              Or describe the change you want
            </label>
            <textarea
              id="stack-feedback"
              className="field"
              rows={3}
              required
              minLength={5}
              maxLength={4000}
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Use Convex for the database and real-time backend. Keep React, and explain what changes in authentication and deployment."
            />
            <p className="small muted">
              The studio reviews related components and data flows together. A
              revised stack requires your confirmation again.
            </p>
            <button className="btn btn-primary" disabled={busy || !!editing}>
              Revise the stack →
            </button>
          </form>
          <div className="studio-card">
            <h2>How the pieces work together</h2>
            <div className="stack-grid">
              {stack.components.map((component) => (
                <div className="component-card" key={component.name}>
                  <h3>{component.name}</h3>
                  <p className="accent-blue small">{component.technology}</p>
                  <p>{component.responsibility}</p>
                  <p className="small muted">
                    Depends on: {component.depends_on.join(", ") || "None"}
                  </p>
                </div>
              ))}
            </div>
            <h3>Data flow</h3>
            <ol>
              {stack.data_flow.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ol>
          </div>
          <div className="studio-card">
            <h2>Compatibility & implementation risks</h2>
            <ul>
              {stack.compatibility_notes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
            {stack.risks.map((risk) => (
              <p key={risk.risk}>
                <strong>
                  {risk.severity}: {risk.risk}
                </strong>
                <br />
                {risk.mitigation}
              </p>
            ))}
          </div>
          {!project.context.stack_confirmed ? (
            <div className="approval-panel">
              <div>
                <h2>Ready to commit to this stack?</h2>
                <p className="muted">
                  The detailed PRD and agent instructions will use these exact
                  decisions.
                </p>
              </div>
              <button
                className="btn btn-lime"
                disabled={busy || !!editing}
                onClick={async () => {
                  if (
                    await act(`${path}/stack/confirm`, {
                      revision: project.revision,
                    })
                  )
                    router.push(`${path}/docs`);
                }}
              >
                Confirm stack & write documents →
              </button>
            </div>
          ) : (
            <Link href={`${path}/docs`} className="btn btn-lime">
              Open your implementation handoff →
            </Link>
          )}
        </>
      )}
    </div>
  );
}
