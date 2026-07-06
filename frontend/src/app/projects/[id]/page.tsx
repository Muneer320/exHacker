'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Zap } from 'lucide-react';
import { getProject, Project } from '@/services/api';

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) return;
    getProject(projectId).then((res) => {
      if (res.success) {
        setProject(res.data.project);
      } else {
        setError(res.error?.message || 'Project not found.');
      }
      setLoading(false);
    });
  }, [projectId]);

  if (loading) {
    return (
      <div style={{ background: 'var(--color-app-bg)', minHeight: '100vh', color: 'var(--color-text-primary)', padding: '80px 24px' }}>
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          <div style={{ height: '32px', width: '200px', background: 'var(--color-surface-1)', borderRadius: '8px', marginBottom: '24px', animation: 'pulse-ring 2s ease-in-out infinite' }} />
          <div style={{ height: '200px', background: 'var(--color-surface-1)', borderRadius: '12px', animation: 'pulse-ring 2s ease-in-out infinite' }} />
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div style={{ background: 'var(--color-app-bg)', minHeight: '100vh', color: 'var(--color-text-primary)', padding: '80px 24px' }}>
        <div style={{ maxWidth: '900px', margin: '0 auto', textAlign: 'center', padding: '80px 24px' }}>
          <p style={{ fontSize: '32px', marginBottom: '16px' }}>🔍</p>
          <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>Project not found</h2>
          <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '24px' }}>
            {error || 'The project you\'re looking for doesn\'t exist.'}
          </p>
          <button
            onClick={() => router.push('/projects')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '10px 20px',
              borderRadius: '8px',
              border: '1px solid var(--color-border-default)',
              background: 'transparent',
              color: 'var(--color-text-secondary)',
              fontSize: '13px',
              cursor: 'pointer',
            }}
          >
            <ArrowLeft size={14} /> Back to Projects
          </button>
        </div>
      </div>
    );
  }

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
      {/* Top bar */}
      <div
        style={{
          borderBottom: '1px solid var(--color-border-default)',
          padding: '12px 24px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
        }}
      >
        <button
          onClick={() => router.push('/projects')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            padding: '6px 10px',
            borderRadius: '6px',
            border: 'none',
            background: 'transparent',
            color: 'var(--color-text-secondary)',
            fontSize: '13px',
            cursor: 'pointer',
          }}
        >
          <ArrowLeft size={14} /> Projects
        </button>

        <div style={{ width: '1px', height: '20px', background: 'var(--color-border-default)' }} />

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Zap size={14} color="var(--color-accent-400)" />
          <span style={{ fontWeight: 600, fontSize: '14px' }}>{project.name}</span>
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
        </div>
      </div>

      {/* Content */}
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '32px 24px' }}>
        {/* Idea card */}
        <div
          style={{
            padding: '24px',
            borderRadius: '12px',
            background: 'var(--color-surface-1)',
            border: '1px solid var(--color-border-default)',
            marginBottom: '24px',
          }}
        >
          <p style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>
            Original Idea
          </p>
          <p style={{ fontSize: '15px', color: 'var(--color-text-primary)', lineHeight: 1.6 }}>
            {project.idea}
          </p>
        </div>

        {/* Placeholder for future tabs — Research, Blueprint, Export */}
        {project.status === 'draft' && (
          <div
            style={{
              textAlign: 'center',
              padding: '64px 24px',
              border: '1px dashed var(--color-border-default)',
              borderRadius: '16px',
            }}
          >
            <p style={{ fontSize: '28px', marginBottom: '12px' }}>🚀</p>
            <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>
              Research pending
            </h3>
            <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '24px' }}>
              Research and blueprint features are coming soon.
            </p>
          </div>
        )}

        {project.status === 'processing' && (
          <div
            style={{
              textAlign: 'center',
              padding: '64px 24px',
              borderRadius: '16px',
              background: 'var(--color-surface-1)',
              border: '1px solid rgba(6,182,212,0.2)',
            }}
          >
            <div
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                border: '3px solid rgba(6,182,212,0.2)',
                borderTopColor: 'var(--color-info)',
                animation: 'spin 0.8s linear infinite',
                margin: '0 auto 16px',
              }}
            />
            <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>
              Processing
            </h3>
            <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>
              AI agents are analyzing your idea...
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
