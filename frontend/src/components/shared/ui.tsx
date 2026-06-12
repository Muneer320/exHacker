'use client';

import React from 'react';

// ============================================================
// StatusBadge
// ============================================================
type Status = 'running' | 'completed' | 'waiting' | 'failed' | 'idle';

export function StatusBadge({ status }: { status: Status }) {
  const cfg: Record<Status, { label: string; color: string; bg: string; border: string; dot?: string }> = {
    running: { label: 'Running', color: '#3B82F6', bg: 'rgba(59,130,246,0.12)', border: 'rgba(59,130,246,0.3)', dot: '#3B82F6' },
    completed: { label: 'Complete', color: '#22C55E', bg: 'rgba(34,197,94,0.12)', border: 'rgba(34,197,94,0.3)' },
    waiting: { label: 'Waiting', color: '#F59E0B', bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.3)' },
    failed: { label: 'Failed', color: '#EF4444', bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.3)' },
    idle: { label: 'Idle', color: 'rgba(255,255,255,0.3)', bg: 'rgba(255,255,255,0.04)', border: 'rgba(255,255,255,0.08)' },
  };
  const s = cfg[status];
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '3px 10px',
        borderRadius: '99px',
        fontSize: '12px',
        fontWeight: 500,
        color: s.color,
        background: s.bg,
        border: `1px solid ${s.border}`,
      }}
    >
      {status === 'running' && (
        <span
          style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            background: s.dot,
            display: 'inline-block',
            animation: 'pulse-ring 1.5s ease-in-out infinite',
          }}
        />
      )}
      {s.label}
    </span>
  );
}

// ============================================================
// LoadingState
// ============================================================
export function LoadingDots() {
  return (
    <span style={{ display: 'inline-flex', gap: '4px', alignItems: 'center' }}>
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          style={{
            width: '5px',
            height: '5px',
            borderRadius: '50%',
            background: '#7C3AED',
            display: 'inline-block',
            animation: `dot-pulse 1.4s ease-in-out infinite`,
            animationDelay: `${i * 0.16}s`,
          }}
        />
      ))}
    </span>
  );
}

export function SkeletonBlock({ width = '100%', height = '16px', style = {} }: { width?: string; height?: string; style?: React.CSSProperties }) {
  return (
    <div
      className="skeleton"
      style={{ width, height, borderRadius: '6px', ...style }}
    />
  );
}

// ============================================================
// EmptyState
// ============================================================
export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '16px',
        padding: '60px 32px',
        textAlign: 'center',
      }}
    >
      {icon && (
        <div
          style={{
            width: '56px',
            height: '56px',
            borderRadius: '16px',
            background: 'rgba(124,58,237,0.1)',
            border: '1px solid rgba(124,58,237,0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#7C3AED',
          }}
        >
          {icon}
        </div>
      )}
      <div>
        <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#F1F5F9', marginBottom: '8px' }}>{title}</h3>
        <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.45)', maxWidth: '320px', lineHeight: 1.6 }}>{description}</p>
      </div>
      {action}
    </div>
  );
}

// ============================================================
// ScoreBar  
// ============================================================
export function ScoreBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div style={{ marginBottom: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
        <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.6)' }}>{label}</span>
        <span style={{ fontSize: '13px', fontWeight: 600, color }}>{value}</span>
      </div>
      <div style={{ height: '4px', borderRadius: '2px', background: 'rgba(255,255,255,0.06)', overflow: 'hidden' }}>
        <div
          style={{
            height: '100%',
            width: `${value}%`,
            borderRadius: '2px',
            background: color,
            transition: 'width 0.8s cubic-bezier(0.16,1,0.3,1)',
          }}
        />
      </div>
    </div>
  );
}
