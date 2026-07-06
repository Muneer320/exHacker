'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Plus, ArrowRight, Zap } from 'lucide-react';
import { listProjects, Project } from '@/services/api';

export default function ProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listProjects().then((res) => {
      if (res.success) {
        setProjects(res.data.projects);
      }
      setLoading(false);
    });
  }, []);

  const statusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'var(--color-text-tertiary)';
      case 'processing': return 'var(--color-info)';
      case 'ready': return 'var(--color-success)';
      case 'archived': return 'var(--color-text-disabled)';
      default: return 'var(--color-text-tertiary)';
    }
  };

  return (
    <div style={{ background: 'var(--color-app-bg)', minHeight: '100vh', color: 'var(--color-text-primary)' }}>
      {/* Minimal top bar */}
      <div
        style={{
          borderBottom: '1px solid var(--color-border-default)',
          padding: '16px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <Link
          href="/"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            textDecoration: 'none',
            color: 'var(--color-text-primary)',
          }}
        >
          <div
            style={{
              width: '24px',
              height: '24px',
              borderRadius: '6px',
              background: 'linear-gradient(135deg, var(--color-accent-500), var(--color-info))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Zap size={12} color="#fff" />
          </div>
          <span style={{ fontWeight: 700, fontSize: '15px' }}>exHacker</span>
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={() => router.push('/')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 16px',
              borderRadius: '8px',
              border: '1px solid var(--color-border-default)',
              background: 'transparent',
              color: 'var(--color-text-secondary)',
              fontSize: '13px',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            <Plus size={14} />
            New Project
          </button>
        </div>
      </div>

      {/* Content */}
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '48px 24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '4px' }}>Projects</h1>
        <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '32px' }}>
          {loading ? 'Loading...' : `${projects.length} project${projects.length !== 1 ? 's' : ''}`}
        </p>

        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                style={{
                  height: '80px',
                  borderRadius: '12px',
                  background: 'var(--color-surface-1)',
                  border: '1px solid var(--color-border-default)',
                  animation: 'pulse-ring 2s ease-in-out infinite',
                }}
              />
            ))}
          </div>
        ) : projects.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              padding: '80px 24px',
              border: '1px dashed var(--color-border-default)',
              borderRadius: '16px',
            }}
          >
            <p style={{ fontSize: '32px', marginBottom: '16px' }}>✨</p>
            <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
              No projects yet
            </h2>
            <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '24px' }}>
              Your first project is one idea away.
            </p>
            <Link
              href="/"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 24px',
                borderRadius: '8px',
                background: 'var(--color-accent-500)',
                color: '#fff',
                fontSize: '14px',
                fontWeight: 600,
                textDecoration: 'none',
              }}
            >
              Start Building <ArrowRight size={16} />
            </Link>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {projects.map((project) => (
              <Link
                key={project.id}
                href={`/projects/${project.id}`}
                style={{
                  display: 'block',
                  padding: '16px 20px',
                  borderRadius: '12px',
                  background: 'var(--color-surface-1)',
                  border: '1px solid var(--color-border-default)',
                  textDecoration: 'none',
                  color: 'inherit',
                  transition: 'border-color 150ms ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(124,58,237,0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--color-border-default)';
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '4px' }}>
                      {project.name}
                    </h3>
                    <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', lineHeight: 1.4 }}>
                      {project.idea.length > 100
                        ? project.idea.slice(0, 100) + '...'
                        : project.idea}
                    </p>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0, marginLeft: '16px' }}>
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: '99px',
                        fontSize: '11px',
                        fontWeight: 500,
                        background: `${statusColor(project.status)}15`,
                        color: statusColor(project.status),
                        textTransform: 'capitalize',
                      }}
                    >
                      {project.status}
                    </span>
                    <ArrowRight size={14} color="var(--color-text-tertiary)" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
