"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import MarkdownRenderer from "@/components/markdown/MarkdownRenderer";
import { api, type Message } from "@/services/api";
import { useStudio } from "./StudioProvider";

export default function ChatPanel() {
  const { project, busy, act } = useStudio();
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState("");
  const end = useRef<HTMLDivElement>(null);
  const path = `/projects/${project.id}`;
  useEffect(() => {
    let cancelled = false;
    api<{ messages: Message[] }>(`${path}/chat`)
      .then((data) => {
        if (!cancelled) {
          setMessages(data.messages);
          setError("");
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [path, project.revision]);
  useEffect(() => {
    end.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [messages.length]);
  if (!project.context.documents)
    return (
      <div className="empty-panel">
        <span className="eyebrow">04 / YOUR PROJECT ASSISTANT</span>
        <h1>Give your assistant the full picture.</h1>
        <p className="muted">
          Finish the confirmed plan and documentation first so answers use a
          coherent project context.
        </p>
        <Link href={`${path}/docs`} className="btn btn-primary">
          Complete the handoff →
        </Link>
      </div>
    );
  return (
    <div>
      <div className="section-heading">
        <div>
          <span className="eyebrow">04 / YOUR PROJECT ASSISTANT</span>
          <h1>Keep your team moving.</h1>
          <p className="muted">
            Your idea, research, stack, documents, team skills, hackathon, and
            time constraints—in one conversation.
          </p>
        </div>
      </div>
      <div className="notice info">
        Answers use the latest saved project context. Chat is advisory; use
        Ideas and Tech stack to change approved decisions.
      </div>
      {error && (
        <div className="notice error" role="alert">
          {error}
        </div>
      )}
      <div
        className="chat-conversation"
        aria-label="Project conversation"
        aria-live="polite"
      >
        {!messages.length && (
          <div className="empty-panel">
            <h2>What does the team need next?</h2>
            <div className="suggested-questions">
              {[
                "How should we split the work based on our skills?",
                "What should we cut if we have half the time?",
                "Walk us through the riskiest integration.",
                "Help us prepare a concise demo and pitch.",
              ].map((question) => (
                <button
                  key={question}
                  className="suggested-question"
                  onClick={() => setDraft(question)}
                >
                  {question} ↗
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((message) => (
          <article className={`chat-message ${message.role}`} key={message.id}>
            <div className="section-heading">
              <strong>{message.role === "user" ? "You" : "exHacker"}</strong>
              <span className="small muted">
                Context revision {message.context_revision}
              </span>
            </div>
            <MarkdownRenderer content={message.content} />
          </article>
        ))}
        {project.active_job && (
          <p className="muted" role="status">
            An operation is in progress. Your conversation is saved.
          </p>
        )}
        <div ref={end} />
      </div>
      <form
        className="chat-composer"
        onSubmit={async (event) => {
          event.preventDefault();
          if (
            await act(`${path}/chat`, {
              revision: project.revision,
              message: draft,
            })
          )
            setDraft("");
        }}
      >
        <label htmlFor="chat-question" className="small">
          Ask your project assistant
        </label>
        <textarea
          id="chat-question"
          className="field"
          rows={3}
          required
          maxLength={6000}
          value={draft}
          disabled={busy}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Ask about your build plan, decisions, task allocation, or hackathon preparation…"
        />
        <div className="section-heading">
          <span className="small muted">
            Conversation history persists with the project.
          </span>
          <button className="btn btn-lime" disabled={busy || !draft.trim()}>
            {busy ? "Working…" : "Send message →"}
          </button>
        </div>
      </form>
    </div>
  );
}
