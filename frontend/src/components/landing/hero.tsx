import Link from "next/link";

import { Button } from "@/components/ui/button";

export function Hero() {
  return (
    <section className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center px-4 text-center">
      <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
        Your Autonomous
        <br />
        <span className="text-primary">Hackathon Co-Founder</span>
      </h1>
      <p className="mt-6 max-w-2xl text-lg text-muted-foreground">
        Transform challenge statements into execution-ready project blueprints
        in minutes. Research, validate, plan, and architect your hackathon
        project — all before you write a single line of code.
      </p>
      <div className="mt-8 flex gap-4">
        <Link href="/projects/new">
          <Button size="lg">Create New Hackathon Project</Button>
        </Link>
        <Link href="/projects">
          <Button variant="outline" size="lg">
            View Projects
          </Button>
        </Link>
      </div>
    </section>
  );
}
