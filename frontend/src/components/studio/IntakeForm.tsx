"use client";

import { useEffect, useState } from "react";
import { ApiError, emptyIntake, type Intake, type Skill } from "@/services/api";

export default function IntakeForm({
  initial,
  onSubmit,
  submitLabel = "Research & develop my ideas",
  draftKey,
}: {
  initial?: Intake;
  onSubmit: (value: Intake) => Promise<void>;
  submitLabel?: string;
  draftKey?: string;
}) {
  const [value, setValue] = useState<Intake>(() => {
    if (draftKey && typeof window !== "undefined") {
      try {
        const saved = JSON.parse(localStorage.getItem(draftKey) || "null");
        if (
          saved &&
          Array.isArray(saved.teammates) &&
          saved.teammates.every((member: { skills?: unknown }) =>
            Array.isArray(member.skills),
          )
        ) {
          return {
            ...structuredClone(emptyIntake),
            ...saved,
            ...(initial?.idea ? { idea: initial.idea } : {}),
          };
        }
      } catch {
        /* Ignore a corrupt browser draft. */
      }
    }
    return initial || structuredClone(emptyIntake);
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<ApiError["fields"]>([]);
  useEffect(() => {
    if (draftKey) localStorage.setItem(draftKey, JSON.stringify(value));
  }, [value, draftKey]);
  function update<K extends keyof Intake>(key: K, next: Intake[K]) {
    setValue((v) => ({ ...v, [key]: next }));
  }
  function member(index: number, field: string, next: unknown) {
    setValue((v) => ({
      ...v,
      teammates: v.teammates.map((m, i) =>
        i === index ? { ...m, [field]: next } : m,
      ),
    }));
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setFieldErrors([]);
    try {
      await onSubmit(value);
      if (draftKey) localStorage.removeItem(draftKey);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not save the project.",
      );
      if (err instanceof ApiError) setFieldErrors(err.fields);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="intake-form">
      <fieldset disabled={busy}>
        <div className="studio-card">
          <span className="eyebrow">01 / THE CHALLENGE</span>
          <label htmlFor="idea">
            Your idea or challenge theme <span className="required">*</span>
          </label>
          <textarea
            id="idea"
            className="field"
            required
            minLength={10}
            maxLength={6000}
            rows={4}
            value={value.idea}
            onChange={(e) => update("idea", e.target.value)}
            placeholder="What problem do you want to solve, or what is the hackathon asking for?"
          />
          <div className="form-grid">
            <div>
              <label htmlFor="project-name">
                Project name <span className="optional">optional</span>
              </label>
              <input
                id="project-name"
                className="field"
                maxLength={160}
                value={value.name}
                onChange={(e) => update("name", e.target.value)}
                placeholder="We can name it later"
              />
            </div>
            <div>
              <label htmlFor="available-hours">
                Time available, in hours <span className="required">*</span>
              </label>
              <input
                id="available-hours"
                className="field"
                required
                type="number"
                min={1}
                max={720}
                step="0.5"
                value={value.available_hours}
                onChange={(e) =>
                  update("available_hours", Number(e.target.value))
                }
              />
            </div>
          </div>
        </div>

        <div className="studio-card">
          <div className="section-heading">
            <div>
              <span className="eyebrow">02 / YOUR TEAM</span>
              <h2>Build around your strengths.</h2>
            </div>
            <span className="badge badge-blue">
              {value.teammates.length}{" "}
              {value.teammates.length === 1 ? "builder" : "builders"}
            </span>
          </div>
          <p className="muted">
            Include yourself. Skills and proficiency shape feasibility,
            technology choices, and task assignments.
          </p>
          {value.teammates.map((teammate, index) => (
            <div key={index} className="teammate-card">
              <div className="section-heading">
                <strong>Builder {index + 1}</strong>
                {value.teammates.length > 1 && (
                  <button
                    type="button"
                    className="text-button"
                    aria-label={`Remove builder ${index + 1}`}
                    onClick={() =>
                      update(
                        "teammates",
                        value.teammates.filter((_, i) => i !== index),
                      )
                    }
                  >
                    Remove
                  </button>
                )}
              </div>
              <div className="form-grid">
                <div>
                  <label htmlFor={`name-${index}`}>
                    Name <span className="required">*</span>
                  </label>
                  <input
                    id={`name-${index}`}
                    className="field"
                    required
                    maxLength={80}
                    value={teammate.name}
                    onChange={(e) => member(index, "name", e.target.value)}
                  />
                </div>
                <div>
                  <label htmlFor={`role-${index}`}>Preferred role</label>
                  <input
                    id={`role-${index}`}
                    className="field"
                    maxLength={120}
                    value={teammate.role}
                    onChange={(e) => member(index, "role", e.target.value)}
                    placeholder="Frontend, design, AI…"
                  />
                </div>
              </div>
              {teammate.skills.map((skill, skillIndex) => (
                <div className="skill-row" key={skillIndex}>
                  <div>
                    <label htmlFor={`skill-${index}-${skillIndex}`}>
                      Language or framework <span className="required">*</span>
                    </label>
                    <input
                      id={`skill-${index}-${skillIndex}`}
                      className="field"
                      required
                      maxLength={80}
                      value={skill.technology}
                      onChange={(e) =>
                        member(
                          index,
                          "skills",
                          teammate.skills.map((s, i) =>
                            i === skillIndex
                              ? { ...s, technology: e.target.value }
                              : s,
                          ),
                        )
                      }
                      placeholder="Python, React, Figma…"
                    />
                  </div>
                  <div>
                    <label htmlFor={`level-${index}-${skillIndex}`}>
                      Proficiency
                    </label>
                    <select
                      id={`level-${index}-${skillIndex}`}
                      className="field"
                      value={skill.proficiency}
                      onChange={(e) =>
                        member(
                          index,
                          "skills",
                          teammate.skills.map((s, i) =>
                            i === skillIndex
                              ? {
                                  ...s,
                                  proficiency: e.target
                                    .value as Skill["proficiency"],
                                }
                              : s,
                          ),
                        )
                      }
                    >
                      <option value="beginner">Beginner</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="advanced">Advanced</option>
                    </select>
                  </div>
                  {teammate.skills.length > 1 && (
                    <button
                      type="button"
                      className="text-button"
                      aria-label={`Remove skill ${skillIndex + 1} for builder ${index + 1}`}
                      onClick={() =>
                        member(
                          index,
                          "skills",
                          teammate.skills.filter((_, i) => i !== skillIndex),
                        )
                      }
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
              <div className="form-grid" style={{ marginTop: 12 }}>
                <button
                  type="button"
                  className="btn btn-ghost"
                  disabled={teammate.skills.length >= 20}
                  onClick={() =>
                    member(index, "skills", [
                      ...teammate.skills,
                      { technology: "", proficiency: "intermediate" },
                    ])
                  }
                >
                  + Add skill
                </button>
                <div>
                  <label htmlFor={`capacity-${index}`}>
                    Personal availability, hours{" "}
                    <span className="optional">optional</span>
                  </label>
                  <input
                    id={`capacity-${index}`}
                    className="field"
                    type="number"
                    min={0.5}
                    max={value.available_hours}
                    step="0.5"
                    placeholder={`Up to ${value.available_hours}h`}
                    value={teammate.hours_available ?? ""}
                    onChange={(e) =>
                      member(
                        index,
                        "hours_available",
                        e.target.value ? Number(e.target.value) : null,
                      )
                    }
                  />
                </div>
              </div>
            </div>
          ))}
          <button
            type="button"
            className="btn btn-ghost"
            disabled={value.teammates.length >= 12}
            onClick={() =>
              update("teammates", [
                ...value.teammates,
                {
                  name: "",
                  role: "",
                  skills: [{ technology: "", proficiency: "intermediate" }],
                  hours_available: null,
                },
              ])
            }
          >
            + Add teammate
          </button>
        </div>

        <details className="studio-card">
          <summary>
            <span className="eyebrow">03 / ADDITIONAL CONTEXT</span>
            <h2>Give your ideas an advantage.</h2>
            <span className="muted">
              Optional details · expand to add judging criteria, rules, and
              preferences
            </span>
          </summary>
          <div className="form-grid">
            {(
              [
                ["hackathon", "Hackathon name"],
                ["target_platform", "Target platform"],
                [
                  "required_technologies",
                  "Required technologies / sponsor requirements",
                ],
                ["preferred_technologies", "Technologies you prefer"],
                ["excluded_technologies", "Technologies to avoid"],
                ["budget", "Budget and paid-service constraints"],
              ] as [keyof Intake, string][]
            ).map(([key, label]) => (
              <div key={key}>
                <label htmlFor={key}>{label}</label>
                <input
                  id={key}
                  className="field"
                  maxLength={
                    key === "hackathon"
                      ? 200
                      : key === "target_platform"
                        ? 120
                        : key === "budget"
                          ? 300
                          : 1000
                  }
                  value={String(value[key])}
                  onChange={(e) => update(key, e.target.value)}
                />
              </div>
            ))}
          </div>
          {(
            [
              ["judging_criteria", "Judging rubric and evaluation priorities"],
              ["rules", "Hackathon rules"],
              ["constraints", "Other constraints or context"],
            ] as [keyof Intake, string][]
          ).map(([key, label]) => (
            <div key={key}>
              <label htmlFor={key}>{label}</label>
              <textarea
                id={key}
                className="field"
                rows={3}
                maxLength={4000}
                value={String(value[key])}
                onChange={(e) => update(key, e.target.value)}
              />
            </div>
          ))}
        </details>
        {error && (
          <div className="notice error" role="alert">
            {error}
            {fieldErrors.length > 0 && (
              <ul>
                {fieldErrors.map((err, i) => (
                  <li key={i}>
                    {err.field}: {err.message}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
        <div className="form-actions">
          <p className="muted">
            You choose the idea and approve the stack before documentation is
            written.
          </p>
          <button type="submit" className="btn btn-lime" disabled={busy}>
            {busy ? "Saving your project…" : submitLabel} →
          </button>
        </div>
      </fieldset>
    </form>
  );
}
