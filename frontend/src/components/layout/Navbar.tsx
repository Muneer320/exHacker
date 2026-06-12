'use client';

import { Suspense } from 'react';
import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import { Zap, Activity, LayoutDashboard, GitBranch, Plus, Code2 } from 'lucide-react';

// ─── Inner component that uses search params ─────────────────────────────────
function NavbarInner() {
  const pathname = usePathname() || '';
  const searchParams = useSearchParams();
  const wId = searchParams.get('wId') || '';

  // Extract projectId if we are inside a project route
  const match = pathname.match(/\/(workflow|dashboard|ideas)\/([^/]+)/);
  const projectId = match ? match[2] : null;

  // Build query string to propagate wId
  const q = wId ? `?wId=${wId}` : '';

  const navLinks: { href: string; label: string; icon: React.ElementType }[] = [];

  if (projectId && projectId !== 'demo-finance-001') {
    navLinks.push(
      { href: `/workflow/${projectId}${q}`, label: 'Workflow', icon: Activity },
      { href: `/dashboard/${projectId}${q}`, label: 'Dashboard', icon: LayoutDashboard },
    );
  }

  return (
    <nav
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        height: '64px',
        background: 'rgba(5, 8, 22, 0.85)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 32px',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        {/* Logo */}
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
          <div
            style={{
              width: '32px', height: '32px',
              background: 'linear-gradient(135deg, #7C3AED, #06B6D4)',
              borderRadius: '8px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >
            <Zap size={16} color="#fff" />
          </div>
          <span
            style={{
              fontSize: '18px', fontWeight: 700,
              background: 'linear-gradient(135deg, #A855F7, #06B6D4)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            exHacker
          </span>
        </Link>

        {/* Context-aware Nav Links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname.startsWith(link.href.split('?')[0]);
            return (
              <Link
                key={link.href}
                href={link.href}
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px',
                  padding: '6px 14px', borderRadius: '8px',
                  fontSize: '14px', fontWeight: 500, textDecoration: 'none',
                  color: isActive ? '#A855F7' : 'rgba(255,255,255,0.6)',
                  background: isActive ? 'rgba(124,58,237,0.1)' : 'transparent',
                  border: `1px solid ${isActive ? 'rgba(124,58,237,0.25)' : 'transparent'}`,
                  transition: 'all 150ms ease-out',
                }}
              >
                <Icon size={14} />
                {link.label}
              </Link>
            );
          })}
        </div>

        {/* Right Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Link
            href="/demo"
            style={{
              display: 'flex', alignItems: 'center', gap: '6px',
              padding: '6px 14px', borderRadius: '8px', fontSize: '13px',
              fontWeight: 500, textDecoration: 'none',
              color: pathname === '/demo' ? '#A855F7' : 'rgba(255,255,255,0.5)',
              background: pathname === '/demo' ? 'rgba(124,58,237,0.1)' : 'transparent',
              border: '1px solid rgba(255,255,255,0.08)',
              transition: 'all 150ms ease-out',
            }}
          >
            <GitBranch size={13} />
            Demo
          </Link>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            title="View on GitHub"
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              width: '34px', height: '34px', borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.1)',
              color: 'rgba(255,255,255,0.45)', textDecoration: 'none',
              transition: 'all 150ms ease-out',
            }}
          >
            <Code2 size={15} />
          </a>
          <Link
            href="/new-project"
            style={{
              display: 'flex', alignItems: 'center', gap: '6px',
              padding: '8px 18px', borderRadius: '8px',
              fontSize: '13px', fontWeight: 600, textDecoration: 'none',
              background: 'linear-gradient(135deg, #7C3AED, #06B6D4)',
              color: '#fff',
              boxShadow: '0 0 15px rgba(124,58,237,0.3)',
              transition: 'all 150ms ease-out',
            }}
          >
            <Plus size={14} />
            New Project
          </Link>
        </div>
      </div>
    </nav>
  );
}

// ─── Skeleton shown while Suspense resolves ───────────────────────────────────
function NavbarSkeleton() {
  return (
    <nav
      style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
        height: '64px', background: 'rgba(5,8,22,0.85)',
        backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 32px', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: 'linear-gradient(135deg,#7C3AED,#06B6D4)' }} />
          <span style={{ fontSize: 18, fontWeight: 700, color: '#A855F7' }}>exHacker</span>
        </div>
        <div />
      </div>
    </nav>
  );
}

// ─── Export with Suspense boundary ───────────────────────────────────────────
export default function Navbar() {
  return (
    <Suspense fallback={<NavbarSkeleton />}>
      <NavbarInner />
    </Suspense>
  );
}
