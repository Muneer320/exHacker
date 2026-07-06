'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Zap, Plus, List } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();
  const isApp = pathname.startsWith('/projects') || pathname.startsWith('/app');

  if (isApp) return null; // App pages use sidebar navigation

  const navLinks = [
    { href: '/projects', label: 'Projects', icon: List },
    { href: '/projects/new', label: 'New Project', icon: Plus },
  ];

  return (
    <nav
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        height: '56px',
        background: 'rgba(5, 8, 22, 0.8)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderBottom: '1px solid var(--color-border-default)',
      }}
    >
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 24px',
          height: '100%',
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
              width: '28px',
              height: '28px',
              borderRadius: '7px',
              background: 'linear-gradient(135deg, var(--color-accent-500), var(--color-info))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Zap size={14} color="#fff" />
          </div>
          <span style={{ fontWeight: 700, fontSize: '16px' }}>exHacker</span>
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 14px',
                  borderRadius: '8px',
                  fontSize: '13px',
                  fontWeight: 500,
                  textDecoration: 'none',
                  color: isActive
                    ? 'var(--color-accent-400)'
                    : 'var(--color-text-secondary)',
                  background: isActive
                    ? 'rgba(124, 58, 237, 0.1)'
                    : 'transparent',
                  transition: 'all 150ms ease',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.background = 'rgba(255,255,255,0.04)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.background = 'transparent';
                  }
                }}
              >
                <Icon size={14} />
                {link.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
