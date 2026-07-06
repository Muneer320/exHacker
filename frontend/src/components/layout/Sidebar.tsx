'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Zap, FolderKanban, Plus, Settings, ChevronLeft, ChevronRight } from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Projects', href: '/app/projects', icon: FolderKanban },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={`sidebar ${collapsed ? 'sidebar-collapsed' : ''}`}>
      {/* Logo */}
      <div style={{
        padding: collapsed ? '16px 12px' : '16px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        borderBottom: '1px solid var(--color-border-default)',
      }}>
        <div style={{
          width: '28px',
          height: '28px',
          borderRadius: '7px',
          background: 'linear-gradient(135deg, #7C3AED, #06B6D4)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}>
          <Zap size={14} color="white" />
        </div>
        {!collapsed && (
          <span style={{ fontWeight: 700, fontSize: '16px', color: '#F1F5F9' }}>exHacker</span>
        )}
      </div>

      {/* Navigation */}
      <nav style={{
        flex: 1,
        padding: collapsed ? '12px 0' : '12px 8px',
        display: 'flex',
        flexDirection: 'column',
        gap: '2px',
      }}>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: collapsed ? '10px 18px' : '8px 12px',
                borderRadius: 'var(--radius-md)',
                fontSize: '14px',
                fontWeight: isActive ? 600 : 400,
                color: isActive ? '#A855F7' : 'rgba(255,255,255,0.5)',
                background: isActive ? 'rgba(124,58,237,0.1)' : 'transparent',
                textDecoration: 'none',
                transition: 'all 150ms ease',
                justifyContent: collapsed ? 'center' : 'flex-start',
              }}
            >
              <Icon size={18} />
              {!collapsed && item.label}
            </Link>
          );
        })}
      </nav>

      {/* New Project Button */}
      <div style={{ padding: collapsed ? '8px 0' : '8px 12px' }}>
        <Link
          href="/app/projects/new"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: collapsed ? '10px 18px' : '10px 16px',
            borderRadius: 'var(--radius-md)',
            background: '#7C3AED',
            color: 'white',
            fontSize: '14px',
            fontWeight: 600,
            textDecoration: 'none',
            justifyContent: collapsed ? 'center' : 'flex-start',
            transition: 'filter 150ms ease',
          }}
          onMouseEnter={(e) => { e.currentTarget.style.filter = 'brightness(1.15)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.filter = 'none'; }}
        >
          <Plus size={16} />
          {!collapsed && 'New Project'}
        </Link>
      </div>

      {/* Settings */}
      <div style={{
        padding: collapsed ? '8px 0' : '8px 12px',
        borderTop: '1px solid var(--color-border-default)',
      }}>
        <Link
          href="/app/settings"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: collapsed ? '10px 18px' : '8px 12px',
            borderRadius: 'var(--radius-md)',
            fontSize: '14px',
            color: 'rgba(255,255,255,0.4)',
            textDecoration: 'none',
            justifyContent: collapsed ? 'center' : 'flex-start',
          }}
        >
          <Settings size={16} />
          {!collapsed && 'Settings'}
        </Link>
      </div>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        style={{
          position: 'absolute',
          right: '-12px',
          top: '50%',
          width: '24px',
          height: '24px',
          borderRadius: '50%',
          background: '#0B1020',
          border: '1px solid rgba(255,255,255,0.06)',
          color: 'rgba(255,255,255,0.3)',
          cursor: 'pointer',
          display: collapsed ? 'none' : 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transform: 'translateY(-50%)',
          zIndex: 50,
        }}
      >
        <ChevronLeft size={12} />
      </button>
    </aside>
  );
}
