"use client";

import { useEffect, useRef, useState } from "react";

export default function MermaidViewer({
  code,
  title,
}: {
  code: string;
  title?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [failure, setFailure] = useState<{
    code: string;
    message: string;
  } | null>(null);
  const trimmed = code?.trim() || "";
  const invalid =
    trimmed.length < 6
      ? "Diagram too short to render."
      : trimmed.length > 10000
        ? "Diagram too large to render inline."
        : null;
  const error = invalid || (failure?.code === code ? failure.message : null);
  useEffect(() => {
    if (!ref.current || invalid) return;
    let cancelled = false;
    ref.current.innerHTML = "";
    void import("mermaid")
      .then(async ({ default: mermaid }) => {
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: "strict",
          suppressErrorRendering: true,
          theme: "dark",
          themeVariables: {
            primaryColor: "#161616",
            primaryTextColor: "#f2f2f2",
            lineColor: "#3d7cf6",
            fontFamily: "Inter, sans-serif",
          },
        });
        const result = await mermaid.render(
          `mermaid-${crypto.randomUUID()}`,
          trimmed,
        );
        if (!cancelled && ref.current) ref.current.innerHTML = result.svg;
      })
      .catch((err) => {
        if (!cancelled)
          setFailure({
            code,
            message:
              err instanceof Error
                ? err.message
                : "Diagram could not be rendered.",
          });
      });
    return () => {
      cancelled = true;
    };
  }, [code, invalid, trimmed]);
  if (!trimmed) return null;
  return (
    <div className="studio-card">
      <span className="eyebrow">{title || "Diagram"}</span>
      {error ? (
        <div role="alert">
          <p className="error-text">{error}</p>
          <details>
            <summary>Show diagram source</summary>
            <pre className="markdown-source">{code}</pre>
          </details>
        </div>
      ) : (
        <div ref={ref} style={{ overflow: "auto", minHeight: 100 }} />
      )}
    </div>
  );
}
