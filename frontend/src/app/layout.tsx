import type { Metadata } from "next";
import "./globals.css";
import "./studio.css";
import AnimatedBackground from "@/components/AnimatedBackground";
import AIProvider from "@/components/studio/AIProvider";

export const metadata: Metadata = {
  title: "exHacker | Hackathon Product Studio",
  description:
    "Research and refine hackathon ideas, confirm your technology stack, and build from a detailed PRD with your project-aware assistant.",
  keywords: ["hackathon", "AI", "agents", "ideation", "architecture"],
  openGraph: {
    title: "exHacker | Hackathon Product Studio",
    description:
      "Research five directions, review your stack, and build from a detailed Markdown handoff with a project-aware assistant.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" data-scroll-behavior="smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
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
        <AIProvider>
          <div className="page-content">{children}</div>
        </AIProvider>
      </body>
    </html>
  );
}
