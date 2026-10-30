"use client";

import { useState } from "react";
import Link from "next/link";
import MarkdownRenderer from "@/components/markdown/MarkdownRenderer";
import { download } from "@/services/api";
import { useStudio } from "./StudioProvider";

export default function DocumentsPanel() {
  const { project, busy, act } = useStudio();
  const [filename, setFilename] = useState("PRD.md");
  const [raw, setRaw] = useState(false);
  const [message, setMessage] = useState("");
  const [downloading, setDownloading] = useState(false);
  const docs = project.context.documents;
  const path = `/projects/${project.id}`;
  const active =
    docs?.files.find((file) => file.filename === filename) || docs?.files[0];
  async function save(all: boolean) {
    setDownloading(true);
    setMessage("");
    try {
      await download(
        all ? `${path}/export` : `${path}/documents/${active?.filename}`,
        all ? `exhacker-${project.id.slice(0, 8)}.zip` : active!.filename,
      );
      setMessage("Download ready.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Download failed.");
    } finally {
      setDownloading(false);
    }
  }

  return (
    <div>
      <div className="section-heading">
        <div>
          <span className="eyebrow">03 / THE IMPLEMENTATION HANDOFF</span>
          <h1>A plan you can build from.</h1>
          <p className="muted">
            Detailed requirements for humans. Specific instructions for agents.
            Every file is Markdown.
          </p>
        </div>
        {docs && (
          <button
            className="btn btn-lime"
            disabled={downloading}
            onClick={() => void save(true)}
          >
            {downloading ? "Preparing…" : "Download all .md files ↓"}
          </button>
        )}
      </div>
      {!project.context.stack_confirmed ? (
        <div className="empty-panel">
          <h2>Your stack needs approval.</h2>
          <p className="muted">
            Documentation must reflect choices you have confirmed.
          </p>
          <Link href={`${path}/stack`} className="btn btn-primary">
            Review the technology stack →
          </Link>
        </div>
      ) : !docs ? (
        <div className="empty-panel">
          <h2>
            {busy
              ? "Writing your implementation package…"
              : "Ready for a detailed handoff."}
          </h2>
          <p className="muted">
            The PRD covers requirements, user journeys, contracts, edge cases,
            tests, and an achievable build plan. AGENTS.md gives coding agents
            the project-specific rules.
          </p>
          <button
            className="btn btn-primary"
            disabled={busy}
            onClick={() =>
              void act(`${path}/jobs`, {
                kind: "documents",
                revision: project.revision,
              })
            }
          >
            Generate the Markdown package →
          </button>
        </div>
      ) : (
        <>
          <div className="section-heading">
            <p className="small muted">
              {docs.files.length} files · snapshot revision {docs.revision} ·{" "}
              {new Date(docs.generated_at).toLocaleString()}
            </p>
            <button
              className="text-button"
              disabled={busy}
              onClick={() =>
                void act(`${path}/jobs`, {
                  kind: "documents",
                  revision: project.revision,
                })
              }
            >
              Regenerate package
            </button>
          </div>
          {message && (
            <div className="notice info" role="status">
              {message}
            </div>
          )}
          <div className="document-browser">
            <nav className="document-files" aria-label="Generated documents">
              {docs.files.map((file) => (
                <button
                  key={file.filename}
                  className={file.filename === active?.filename ? "active" : ""}
                  onClick={() => setFilename(file.filename)}
                >
                  {file.filename}
                  <span>
                    {Math.ceil(
                      new TextEncoder().encode(file.content).length / 1024,
                    )}{" "}
                    KB
                  </span>
                </button>
              ))}
            </nav>
            <section className="document-preview">
              <div className="document-toolbar">
                <strong>{active?.filename}</strong>
                <button className="text-button" onClick={() => setRaw(!raw)}>
                  {raw ? "Preview" : "Markdown source"}
                </button>
                <button
                  className="text-button"
                  onClick={async () => {
                    try {
                      await navigator.clipboard.writeText(
                        active?.content || "",
                      );
                      setMessage(`${active?.filename} copied.`);
                    } catch {
                      setMessage(
                        "Clipboard permission was denied. Download the file or select its Markdown source to copy.",
                      );
                    }
                  }}
                >
                  Copy
                </button>
                <button
                  className="text-button"
                  disabled={downloading}
                  onClick={() => void save(false)}
                >
                  Download
                </button>
              </div>
              {active &&
                (raw ? (
                  <pre className="markdown-source">{active.content}</pre>
                ) : (
                  <div className="markdown-preview">
                    <MarkdownRenderer content={active.content} />
                  </div>
                ))}
            </section>
          </div>
          <div className="approval-panel">
            <div>
              <h2>Your project assistant is ready.</h2>
              <p className="muted">
                Ask about implementation, dividing work, trade-offs, or
                preparing for the judges.
              </p>
            </div>
            <Link href={`${path}/chat`} className="btn btn-primary">
              Talk to your assistant →
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
