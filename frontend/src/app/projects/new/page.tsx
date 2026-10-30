"use client";

import { Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import dynamic from "next/dynamic";
import { api, emptyIntake, type Project } from "@/services/api";
import { useAI } from "@/components/studio/AIProvider";

const IntakeForm = dynamic(() => import("@/components/studio/IntakeForm"), {
  ssr: false,
  loading: () => <p role="status">Loading your saved brief…</p>,
});

function NewProject() {
  const router = useRouter();
  const ai = useAI();
  const params = useSearchParams();
  return (
    <main className="studio-container intake-container">
      <div className="section-heading">
        <Link href="/" className="brand">
          <span className="brand-mark">ex</span>Hacker
        </Link>
        <Link href="/projects" className="text-link">
          Your projects →
        </Link>
      </div>
      <header className="intake-heading">
        <span className="eyebrow">START WITH THE PEOPLE AND THE PROBLEM</span>
        <h1>
          A better brief.
          <br />
          <span className="accent-blue">A stronger starting point.</span>
        </h1>
        <p className="muted">
          Tell us what you&apos;re working toward, who&apos;s building, and how
          much time you have. We&apos;ll take it from there.
        </p>
      </header>
      {ai.config && !ai.config.demo && ai.config.access_mode === "byok" && (
        <div className="notice">
          <div>
            <strong>
              {ai.session
                ? `Ready with ${ai.session.provider} · ${ai.session.model}`
                : "Connect your AI before generating ideas."}
            </strong>
            <p className="small muted">
              Your project brief is saved as a draft on this device. API keys
              belong only in AI session settings.
            </p>
          </div>
          <button className="btn btn-ghost" onClick={() => ai.open()}>
            {ai.session ? "Manage AI session" : "Connect API key"}
          </button>
        </div>
      )}
      <IntakeForm
        initial={{
          ...structuredClone(emptyIntake),
          idea: params.get("idea") || "",
        }}
        draftKey="exhacker.intake.v2"
        onSubmit={async (intake) => {
          const project = await api<Project>("/projects", "POST", intake);
          router.push(`/projects/${project.id}/ideas`);
        }}
      />
    </main>
  );
}

export default function Page() {
  return (
    <Suspense
      fallback={
        <main className="studio-container">Loading the project brief…</main>
      }
    >
      <NewProject />
    </Suspense>
  );
}
