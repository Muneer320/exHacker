import type { Metadata } from "next";
import "./globals.css";
import AnimatedBackground from "../components/AnimatedBackground";

export const metadata: Metadata = {
  title: "exHacker — AI-Powered Hackathon Strategy Engine",
  description:
    "Turn any hackathon challenge into a complete winning playbook. 9 AI agents. 10 ranked ideas. Full solution blueprint, pitch deck, and 3 pitch scripts.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        {/* ── Animated background layers (fixed, behind all content) ── */}
        <AnimatedBackground />
        <div className="bg-grid"    aria-hidden="true" />
        <div className="bg-orb bg-orb-1" aria-hidden="true" />
        <div className="bg-orb bg-orb-2" aria-hidden="true" />
        <div className="bg-orb bg-orb-3" aria-hidden="true" />
        <div className="bg-orb bg-orb-4" aria-hidden="true" />

        {/* ── Page content (sits above background layers) ── */}
        <div className="page-content">
          {children}
        </div>
      </body>
    </html>
  );
}
