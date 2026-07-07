import type { Metadata } from 'next';
import './globals.css';
import AnimatedBackground from '@/components/AnimatedBackground';

export const metadata: Metadata = {
  title: 'exHacker — AI-Powered Hackathon Platform',
  description:
    'Turn any hackathon challenge into a winning project in minutes. AI agents analyze, research, ideate, architect, and pitch your solution.',
  keywords: ['hackathon', 'AI', 'agents', 'ideation', 'architecture'],
  openGraph: {
    title: 'exHacker — AI-Powered Hackathon Platform',
    description: 'Win hackathons with your AI team.',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        {/* Floating particle network background */}
        <AnimatedBackground />

        {/* Animated gradient orbs — behind all content */}
        <div className="bg-orb bg-orb-1" aria-hidden="true" />
        <div className="bg-orb bg-orb-2" aria-hidden="true" />
        <div className="bg-orb bg-orb-3" aria-hidden="true" />
        <div className="bg-orb bg-orb-4" aria-hidden="true" />
        <div className="bg-grid" aria-hidden="true" />

        {/* Page content sits above background layers */}
        <div className="page-content">{children}</div>
      </body>
    </html>
  );
}
