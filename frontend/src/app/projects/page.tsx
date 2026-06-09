"use client";

import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useProjects } from "@/hooks/use-projects";

const statusStyles: Record<string, string> = {
  draft: "bg-muted text-muted-foreground",
  researching: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-800",
  idea_selection: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-800",
  completed: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800",
  failed: "bg-destructive/10 text-destructive border-destructive/20",
};

export default function ProjectsPage() {
  const { data: projects, isLoading, error } = useProjects();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-sm text-muted-foreground">Loading projects...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="rounded-lg border border-destructive/20 bg-destructive/5 px-6 py-4 text-center">
          <p className="text-destructive">Failed to load projects</p>
          <p className="mt-1 text-xs text-muted-foreground">Make sure the backend server is running on port 8000</p>
        </div>
      </div>
    );
  }

  return (
    <main className="mx-auto max-w-5xl px-4 py-12">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {projects?.length ? `${projects.length} project${projects.length === 1 ? "" : "s"} total` : "Create your first hackathon project"}
          </p>
        </div>
        <Link href="/projects/new">
          <Button className="rounded-full shadow-lg shadow-primary/20">New Project</Button>
        </Link>
      </div>

      {!projects?.length ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center gap-4 py-16">
            <div className="rounded-full bg-muted p-4">
              <svg className="h-8 w-8 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <p className="text-muted-foreground">No projects yet</p>
            <Link href="/projects/new">
              <Button variant="outline">Create Your First Project</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {projects.map((project, i) => (
            <Link
              key={project.id}
              href={`/projects/${project.id}`}
              className="animate-fade-in group"
              style={{ animationDelay: `${i * 0.05}s` }}
            >
              <Card className="transition-all duration-200 hover:border-primary/30 hover:shadow-md hover:shadow-primary/5">
                <CardContent className="flex items-center gap-4 p-5">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-primary/20 to-purple-500/20">
                    <span className="text-lg font-bold text-primary">
                      {project.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-3">
                      <span className="font-semibold group-hover:text-primary transition-colors">
                        {project.name}
                      </span>
                      <Badge
                        variant="outline"
                        className={`text-[10px] px-2 py-0 ${statusStyles[project.status] || ""}`}
                      >
                        {project.status === "idea_selection" ? "awaiting input" : project.status}
                      </Badge>
                    </div>
                    <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                      <span>Stage: {project.currentStage || "input"}</span>
                      <span>·</span>
                      <span>{project.durationHours}h hackathon</span>
                      <span>·</span>
                      <span>{(project.completedAgents?.length || 0)}/11 agents</span>
                    </div>
                  </div>
                  <svg
                    className="h-5 w-5 shrink-0 text-muted-foreground/50 transition-transform group-hover:translate-x-0.5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
