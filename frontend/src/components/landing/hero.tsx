import Link from "next/link";

import { Button } from "@/components/ui/button";

export function Hero() {
  return (
    <section className="relative flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center overflow-hidden px-4 text-center">
      <div className="absolute inset-0 bg-gradient-hero" />
      <div className="relative">
        <div className="mb-6 inline-block rounded-full border bg-muted/50 px-4 py-1.5 text-xs font-medium text-muted-foreground backdrop-blur-sm">
          Multi-Agent Hackathon OS — Built with LangGraph + Groq
        </div>
        <h1 className="animate-fade-in text-5xl font-bold tracking-tight sm:text-7xl">
          Your Autonomous
          <br />
          <span className="bg-gradient-to-r from-primary via-purple-500 to-cyan-500 bg-clip-text text-transparent">
            Hackathon Co-Founder
          </span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl animate-fade-in animation-delay-200 text-lg text-muted-foreground">
          Transform challenge statements into execution-ready project blueprints
          in minutes. Research, validate, plan, and architect your hackathon
          project — all before you write a single line of code.
        </p>
        <div className="mt-8 flex animate-fade-in animation-delay-300 items-center justify-center gap-4">
          <Link href="/projects/new">
            <Button size="lg" className="h-12 rounded-full px-8 text-base shadow-lg shadow-primary/20">
              Create New Hackathon Project
            </Button>
          </Link>
          <Link href="/projects">
            <Button variant="outline" size="lg" className="h-12 rounded-full px-8 text-base">
              View Projects
            </Button>
          </Link>
        </div>
        <div className="mt-16 grid animate-fade-in animation-delay-500 grid-cols-3 gap-8 text-center">
          {[
            { value: "11", label: "AI Agents" },
            { value: "5s", label: "Avg. Response Time" },
            { value: "100%", label: "Free to Use" },
          ].map((stat) => (
            <div key={stat.label}>
              <div className="text-3xl font-bold text-primary">{stat.value}</div>
              <div className="mt-1 text-sm text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
