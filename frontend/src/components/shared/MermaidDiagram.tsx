'use client';

import { useEffect, useRef, useState } from 'react';

interface MermaidDiagramProps {
  diagram: string;
  className?: string;
}

let mermaidInitialized = false;

export function cleanMermaid(code: string): string {
  if (!code) return '';
  
  let clean = code.trim();
  
  // 1. Remove markdown code block wrappers
  if (clean.includes('```')) {
    const match = clean.match(/```mermaid\s*([\s\S]*?)\s*```/) || clean.match(/```\s*([\s\S]*?)\s*```/);
    if (match) {
      clean = match[1].trim();
    } else {
      clean = clean.replace(/```mermaid/g, '').replace(/```/g, '').trim();
    }
  }
  
  // 2. Remove emojis
  clean = clean.replace(/[\u{1F300}-\u{1F9FF}]|[\u{1F600}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F1E6}-\u{1F1FF}]|[\u{1F900}-\u{1F9FF}]|[\u{1F300}-\u{1F5FF}]|[\u{1F600}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]|[\u{2600}-\u{26FF}]/gu, '');
  
  // 3. Fix unquoted labels containing parentheses or spaces
  // Double parenthesis: id((label)) -> id(("label"))
  clean = clean.replace(/\b(\w+)\s*\(\(([^"]+?)\)\)/g, (m, id, label) => {
    return `${id}(("${label.trim().replace(/"/g, "'")}"))`;
  });
  
  // Bracket parenthesis: id([label]) -> id(["label"])
  clean = clean.replace(/\b(\w+)\s*\(\[([^"]+?)\]\)/g, (m, id, label) => {
    return `${id}(["${label.trim().replace(/"/g, "'")}"])`;
  });
  
  // Parenthesis bracket: id[(label)] -> id[("label")]
  clean = clean.replace(/\b(\w+)\s*\[\(([^"]+?)\)\]/g, (m, id, label) => {
    return `${id}[("${label.trim().replace(/"/g, "'")}")]`;
  });
  
  // Square brackets: id[label] -> id["label"]
  clean = clean.replace(/\b(?!(?:subgraph|flowchart|graph|end|click|style|classDef|class|linkStyle)\b)(\w+)\s*\[([^"\r\n\]]+?)\]/g, (m, id, label) => {
    return `${id}["${label.trim().replace(/"/g, "'")}"]`;
  });
  
  // Parentheses: id(label) -> id("label")
  clean = clean.replace(/\b(?!(?:subgraph|flowchart|graph|end|click|style|classDef|class|linkStyle)\b)(\w+)\s*\(([^"\r\n)]+?)\)/g, (m, id, label) => {
    return `${id}("${label.trim().replace(/"/g, "'")}")`;
  });
  
  // Curly braces: id{label} -> id{"label"}
  clean = clean.replace(/\b(?!(?:subgraph|flowchart|graph|end|click|style|classDef|class|linkStyle)\b)(\w+)\s*\{([^"\r\n}]+?)\}/g, (m, id, label) => {
    return `${id}{"${label.trim().replace(/"/g, "'")}"}`;
  });
  
  // Ensure we start with a valid graph definition if not present
  const lines = clean.split('\n');
  const firstLine = lines[0] ? lines[0].trim() : '';
  if (!firstLine.startsWith('flowchart') && !firstLine.startsWith('graph') && !firstLine.startsWith('gantt') && !firstLine.startsWith('sequenceDiagram') && !firstLine.startsWith('classDiagram') && !firstLine.startsWith('stateDiagram') && !firstLine.startsWith('erDiagram')) {
    clean = 'flowchart TD\n' + clean;
  }

  return clean;
}

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

        const cleaned = cleanMermaid(diagram);
        const { svg } = await mermaid.render(idRef.current, cleaned);

        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
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
        {cleanMermaid(diagram)}
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
