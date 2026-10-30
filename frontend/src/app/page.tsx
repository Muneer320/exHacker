"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Navbar from "@/components/layout/Navbar";

const examples = [
  "Make financial literacy practical for first-year college students",
  "Connect rural students with STEM mentors despite unreliable internet",
  "Help small businesses reduce inventory waste",
];
const stages = [
  [
    "01",
    "Give us your context",
    "Your challenge, team skills, and time. A plan should fit the people who will build it.",
  ],
  [
    "02",
    "Challenge the obvious",
    "Explore unconventional ideas. Research the competition. Critique, revise, and rank the strongest five.",
  ],
  [
    "03",
    "Make it your own",
    "Choose a direction, refine it in your own words, and approve the technology choices.",
  ],
  [
    "04",
    "Leave ready to build",
    "Get a detailed PRD, AGENTS.md, and supporting Markdown. Keep a project-aware assistant beside your team.",
  ],
];

export default function Home() {
  const [idea, setIdea] = useState("");
  const router = useRouter();
  function start(event: React.FormEvent) {
    event.preventDefault();
    router.push(
      `/projects/new${idea.trim() ? `?idea=${encodeURIComponent(idea.trim())}` : ""}`,
    );
  }
  return (
    <>
      <Navbar />
      <main>
        <section className="landing-hero container">
          <span className="eyebrow">A PRODUCT STUDIO FOR HACKATHON TEAMS</span>
          <h1 className="d1">
            THINK
            <br />
            <span className="grad-blue">BEYOND</span>
            <br />
            THE OBVIOUS.
          </h1>
          <div className="hero-bottom">
            <div>
              <p className="body-lg">
                Your team has limited time.
                <br />
                Make the idea worth building.
              </p>
              <p className="muted">
                Research, critique, and refine five directions. Agree on a
                stack. Get an implementation handoff your team and coding agents
                can actually use.
              </p>
              <form onSubmit={start} className="hero-form">
                <label className="sr-only" htmlFor="starting-idea">
                  Your idea or challenge theme
                </label>
                <input
                  id="starting-idea"
                  className="field"
                  maxLength={6000}
                  value={idea}
                  onChange={(e) => setIdea(e.target.value)}
                  placeholder="Describe your idea or challenge theme…"
                />
                <button className="btn btn-lime">Build my strategy →</button>
              </form>
              <div className="feature-tags">
                {examples.map((example, index) => (
                  <button
                    className="chip"
                    key={example}
                    onClick={() => setIdea(example)}
                  >
                    Example {index + 1} ↗
                  </button>
                ))}
              </div>
              <p className="small muted">
                No account wall. You stay in control of the idea and technology
                decisions.
              </p>
            </div>
            <div className="workflow-preview" aria-label="The project workflow">
              <div className="term-bar">
                <span className="term-dot term-dot-r" />
                <span className="term-dot term-dot-y" />
                <span className="term-dot term-dot-g" />
                <span className="small muted">the path to a clear plan</span>
              </div>
              <div className="workflow-preview-body">
                {[
                  "Team context & constraints",
                  "Generate → research → critique → revise",
                  "Five scored directions",
                  "Your idea. Your refinements.",
                  "Technology choices you confirm",
                  "PRD.md + AGENTS.md + supporting docs",
                  "A project-aware team assistant",
                ].map((step, index) => (
                  <div key={step}>
                    <span
                      className={
                        index === 3 || index === 4
                          ? "accent-lime"
                          : "accent-blue"
                      }
                    >
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    {step}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
        <section className="landing-process">
          <div className="container">
            <span className="eyebrow">THE PROCESS</span>
            <h2 className="d3">
              Less guesswork.
              <br />
              <span className="accent-lime">More conviction.</span>
            </h2>
            <div className="process-grid">
              {stages.map(([number, title, description]) => (
                <article key={number}>
                  <span className="eyebrow">{number}</span>
                  <h3>{title}</h3>
                  <p className="muted">{description}</p>
                </article>
              ))}
            </div>
            <Link href="/projects/new" className="btn btn-primary">
              Start with your team →
            </Link>
          </div>
        </section>
        <footer className="landing-footer container">
          <Link href="/" className="brand">
            exHacker
          </Link>
          <span className="small muted">
            Built for the moment before you start building.
          </span>
          <a
            className="text-link"
            href="https://github.com/Muneer320/exHacker"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub ↗
          </a>
        </footer>
      </main>
    </>
  );
}
