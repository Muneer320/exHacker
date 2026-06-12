import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'exHacker — AI-Powered Hackathon Platform',
  description:
    'Turn any hackathon challenge into a winning project in minutes. AI agents analyze, research, ideate, architect, and pitch your solution.',
  keywords: ['hackathon', 'AI', 'LangGraph', 'agents', 'ideation', 'architecture'],
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
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
