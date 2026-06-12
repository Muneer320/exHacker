'use client';

import { useEffect, useRef, useState } from 'react';

interface MermaidDiagramProps {
  diagram: string;
  className?: string;
}

let mermaidInitialized = false;

export default function MermaidDiagram({ diagram, className }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [rendered, setRendered] = useState(false);
  const idRef = useRef(`mermaid-${Math.random().toString(36).slice(2)}`);

  useEffect(() => {
    if (!diagram) return;

    let cancelled = false;

    const renderDiagram = async () => {
      try {
        const mermaid = (await import('mermaid')).default;

        if (!mermaidInitialized) {
          mermaid.initialize({
            startOnLoad: false,
            theme: 'dark',
            themeVariables: {
              primaryColor: '#7C3AED',
              primaryTextColor: '#F1F5F9',
              primaryBorderColor: 'rgba(124,58,237,0.4)',
              lineColor: 'rgba(255,255,255,0.25)',
              secondaryColor: '#0B1020',
              tertiaryColor: '#111827',
              background: '#050816',
              mainBkg: '#0B1020',
              nodeBorder: 'rgba(255,255,255,0.1)',
              clusterBkg: 'rgba(255,255,255,0.03)',
              titleColor: '#A855F7',
              edgeLabelBackground: '#111827',
              fontSize: '14px',
            },
            flowchart: {
              htmlLabels: true,
              curve: 'basis',
              padding: 20,
            },
            securityLevel: 'loose',
          });
          mermaidInitialized = true;
        }

        if (!containerRef.current || cancelled) return;

        const { svg } = await mermaid.render(idRef.current, diagram.trim());

        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
          // Make the SVG responsive
          const svgEl = containerRef.current.querySelector('svg');
          if (svgEl) {
            svgEl.style.width = '100%';
            svgEl.style.height = 'auto';
            svgEl.style.maxWidth = '100%';
          }
          setRendered(true);
          setError(null);
        }
      } catch (err: any) {
        if (!cancelled) {
          console.warn('[MermaidDiagram] Render error:', err?.message || err);
          setError(err?.message || 'Failed to render diagram');
          setRendered(false);
        }
      }
    };

    renderDiagram();

    return () => {
      cancelled = true;
    };
  }, [diagram]);

  if (error || !diagram) {
    return (
      <pre
        style={{
          color: '#22C55E',
          whiteSpace: 'pre-wrap',
          overflow: 'auto',
          fontSize: '13px',
          lineHeight: 1.7,
          fontFamily: '"Fira Code", "JetBrains Mono", monospace',
          margin: 0,
          opacity: 0.85,
        }}
      >
        {diagram}
      </pre>
    );
  }

  return (
    <div className={className}>
      {!rendered && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            color: 'rgba(255,255,255,0.4)',
            fontSize: '13px',
            padding: '12px 0',
          }}
        >
          <div
            style={{
              width: '14px',
              height: '14px',
              border: '2px solid rgba(124,58,237,0.3)',
              borderTopColor: '#7C3AED',
              borderRadius: '50%',
              animation: 'spin 0.8s linear infinite',
            }}
          />
          Rendering diagram...
        </div>
      )}
      <div
        ref={containerRef}
        style={{
          display: rendered ? 'block' : 'none',
          width: '100%',
          overflowX: 'auto',
        }}
      />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
