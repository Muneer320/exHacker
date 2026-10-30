"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { Idea } from "@/services/api";
import { useStudio } from "./StudioProvider";

const label = (key: string) => key.replaceAll("_", " ");

export default function IdeasPanel() {
  const { project, busy, act, config } = useStudio();
  const router = useRouter();
  const [refineId, setRefineId] = useState<string | null>(null);
  const [prompt, setPrompt] = useState("");
  const [compare, setCompare] = useState(false);
  const ideas = project.context.ideas || [];
  const path = `/projects/${project.id}`;

  async function confirm(idea: Idea) {
    if (
      project.context.stack &&
      !window.confirm(
        "Changing the confirmed idea will invalidate the current stack and documents. Previous versions remain in History. Continue?",
      )
    )
      return;
    if (
      await act(`${path}/ideas/${idea.id}/confirm`, {
        revision: project.revision,
      })
    )
      router.push(`${path}/stack`);
  }
  async function regenerate() {
    if (
      ideas.length &&
      !window.confirm(
        "Develop a new set of ideas? On success, your current idea and stack approvals will reset. Previous versions remain in History.",
      )
    )
      return;
    await act(`${path}/jobs`, { kind: "ideas", revision: project.revision });
  }

  return (
    <div>
      <div className="section-heading">
        <div>
          <span className="eyebrow">01 / EXPLORE THE POSSIBILITIES</span>
          <h1>Find your unfair advantage.</h1>
          <p className="muted">
            Unconventional ideas, researched and challenged against your
            team&apos;s real constraints.
          </p>
        </div>
        <button
          className="btn btn-ghost"
          disabled={busy}
          onClick={() => void regenerate()}
        >
          {ideas.length ? "Develop new ideas" : "Develop five ideas"}
        </button>
      </div>
      {!ideas.length ? (
        <div className="empty-panel">
          <h2>
            {busy ? "Your first ideas are taking shape." : "Ready to explore."}
          </h2>
          <p className="muted">
            The studio generates candidates, researches similar products,
            critiques weaknesses, and revises the strongest five. Each completed
            round is saved.
          </p>
          {!busy && (
            <button
              className="btn btn-primary"
              onClick={() => void regenerate()}
            >
              Start the idea cycle →
            </button>
          )}
        </div>
      ) : (
        <>
          <div className="notice info">
            Scores are advisory estimates, not predictions of winning. Overall
            scores use visible weights; originality is capped when supporting
            evidence is missing. {project.context.rounds} evaluation rounds
            completed.
          </div>
          <div className="section-heading">
            <p className="small muted">
              {ideas.length} candidates · sorted by overall score
            </p>
            <button
              className="text-button"
              onClick={() => setCompare(!compare)}
            >
              {compare ? "Hide comparison" : "Compare all five"}
            </button>
          </div>
          {compare && (
            <div className="comparison-scroll">
              <table className="comparison-table">
                <thead>
                  <tr>
                    <th>Dimension</th>
                    {ideas.map((i) => (
                      <th key={i.id}>{i.title}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.keys(ideas[0].scores).map((key) => (
                    <tr key={key}>
                      <th>
                        {label(key)} (
                        {Math.round((config?.score_weights[key] || 0) * 100)}%)
                      </th>
                      {ideas.map((i) => (
                        <td key={i.id}>{i.scores[key]?.value ?? "—"}</td>
                      ))}
                    </tr>
                  ))}
                  <tr>
                    <th>Overall</th>
                    {ideas.map((i) => (
                      <td key={i.id}>
                        <strong>{i.overall}</strong>
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <th>Effort, person-hours</th>
                    {ideas.map((i) => (
                      <td key={i.id}>{i.effort_hours}</td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          )}
          <div className="idea-list">
            {ideas.map((idea, index) => (
              <article
                key={idea.id}
                className={`studio-card idea-card ${project.context.selected_idea_id === idea.id ? "selected" : ""}`}
              >
                <div className="idea-heading">
                  <div>
                    <span className="eyebrow">
                      DIRECTION 0{index + 1}{" "}
                      {project.context.selected_idea_id === idea.id
                        ? "· CONFIRMED"
                        : ""}
                    </span>
                    <h2>{idea.title}</h2>
                    <p className="muted">{idea.hook}</p>
                  </div>
                  <div className="overall-score">
                    <strong>{idea.overall}</strong>
                    <span>/ 100</span>
                  </div>
                </div>
                <p>{idea.solution}</p>
                <div className="feature-tags">
                  {idea.core_features.map((feature) => (
                    <span key={feature} className="feature-tag">
                      {feature}
                    </span>
                  ))}
                </div>
                <div className="score-grid">
                  {Object.entries(idea.scores).map(([key, score]) => (
                    <div key={key}>
                      <div className="score-label">
                        <span>{label(key)}</span>
                        <strong>{score.value}</strong>
                      </div>
                      <div className="score-track">
                        <div style={{ width: `${score.value}%` }} />
                      </div>
                      <details className="score-reason">
                        <summary>Why this score?</summary>
                        <p>{score.rationale}</p>
                      </details>
                    </div>
                  ))}
                </div>
                <div className="idea-meta">
                  <span>~{idea.effort_hours} person-hours</span>
                  <span>{idea.evidence_ids.length} supporting sources</span>
                  <span
                    className={
                      idea.evidence_status === "unverified"
                        ? "warning-text"
                        : "accent-lime"
                    }
                  >
                    {idea.evidence_status}
                  </span>
                </div>
                <details className="idea-details">
                  <summary>Problem, critique, risks & evidence</summary>
                  <h3>The problem</h3>
                  <p>{idea.problem}</p>
                  <h3>Who this is for</h3>
                  <p>{idea.target_users}</p>
                  <h3>What makes it different</h3>
                  <p>{idea.differentiation}</p>
                  <h3>Internal critique</h3>
                  <ul>
                    {idea.critique.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                  <h3>What improved</h3>
                  <ul>
                    {idea.changes_made.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                  <h3>Risks</h3>
                  {idea.risks.map((r) => (
                    <p key={r.risk}>
                      <strong>
                        {r.severity}: {r.risk}
                      </strong>
                      <br />
                      {r.mitigation}
                    </p>
                  ))}
                  <h3>Assumptions</h3>
                  <ul>
                    {idea.assumptions.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                  <h3>Explicit non-goals</h3>
                  <ul>
                    {idea.non_goals.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                  <h3>Demo journey</h3>
                  <p>{idea.demo_scenario}</p>
                  <h3>Supporting research</h3>
                  {idea.evidence_ids.length ? (
                    project.context.research?.sources
                      .filter((source) => idea.evidence_ids.includes(source.id))
                      .map((source) => (
                        <p key={source.id}>
                          <a
                            className="text-link"
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {source.title} ↗
                          </a>
                          <br />
                          <span className="small muted">{source.snippet}</span>
                        </p>
                      ))
                  ) : (
                    <p className="warning-text">
                      No supporting live evidence. Originality remains
                      unverified.
                    </p>
                  )}
                </details>
                <div className="card-actions">
                  <button
                    className="btn btn-lime"
                    disabled={
                      busy || project.context.selected_idea_id === idea.id
                    }
                    onClick={() => void confirm(idea)}
                  >
                    {project.context.selected_idea_id === idea.id
                      ? "Direction confirmed"
                      : "Choose this direction →"}
                  </button>
                  <button
                    className="btn btn-ghost"
                    disabled={busy}
                    onClick={() => {
                      setRefineId(refineId === idea.id ? null : idea.id);
                      setPrompt("");
                    }}
                  >
                    Refine with my own prompt
                  </button>
                </div>
                {refineId === idea.id && (
                  <form
                    className="refinement-form"
                    onSubmit={async (event) => {
                      event.preventDefault();
                      if (
                        await act(`${path}/jobs`, {
                          kind: "refine_idea",
                          revision: project.revision,
                          idea_id: idea.id,
                          prompt,
                        })
                      ) {
                        setRefineId(null);
                        setPrompt("");
                      }
                    }}
                  >
                    <label htmlFor={`refine-${idea.id}`}>
                      What would you change?
                    </label>
                    <textarea
                      id={`refine-${idea.id}`}
                      className="field"
                      required
                      minLength={5}
                      maxLength={4000}
                      rows={3}
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="Keep the core idea, but focus on rural students and make it work offline…"
                    />
                    <p className="small muted">
                      The revised idea goes through research, critique, and
                      scoring again. Confirm it when you&apos;re satisfied;
                      dependent approvals reset after a successful revision.
                    </p>
                    <button className="btn btn-primary" disabled={busy}>
                      Polish & rescore this idea →
                    </button>
                  </form>
                )}
              </article>
            ))}
          </div>
          {project.context.selected_idea_id && (
            <Link className="btn btn-primary" href={`${path}/stack`}>
              Continue to your technology stack →
            </Link>
          )}
        </>
      )}
    </div>
  );
}
