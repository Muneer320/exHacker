"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useCreateProject } from "@/hooks/use-projects";

interface FormData {
  name: string;
  challenge_statements: string;
  duration_hours: number;
  team_size: number;
  experience_level: string;
  skills: string;
  tracks: string;
  datasets: string;
  apis: string;
  evaluation_criteria: string;
  notes: string;
}

export default function NewProjectPage() {
  const router = useRouter();
  const createProject = useCreateProject();
  const { register, handleSubmit, formState: { isSubmitting } } = useForm<FormData>({
    defaultValues: {
      duration_hours: 24,
      team_size: 4,
      experience_level: "intermediate",
    },
  });

  const onSubmit = async (data: FormData) => {
    const payload = {
      name: data.name,
      challenge_statements: data.challenge_statements
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean),
      duration_hours: Number(data.duration_hours),
      team_size: Number(data.team_size),
      experience_level: data.experience_level,
      skills: data.skills.split(",").map((s) => s.trim()).filter(Boolean),
      tracks: data.tracks.split(",").map((s) => s.trim()).filter(Boolean),
      datasets: data.datasets.split(",").map((s) => s.trim()).filter(Boolean),
      apis: data.apis.split(",").map((s) => s.trim()).filter(Boolean),
      documentation_links: [],
      evaluation_criteria: data.evaluation_criteria
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean),
      notes: data.notes || undefined,
    };

    try {
      const project = await createProject.mutateAsync(payload);
      router.push(`/projects/${project.id}`);
    } catch {
      // Error handled by mutation
    }
  };

  return (
    <main className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="mb-8 text-3xl font-bold">New Hackathon Project</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Project Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Project Name</label>
              <input
                {...register("name", { required: true })}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="My Hackathon Project"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Challenge Statements</label>
              <textarea
                {...register("challenge_statements", { required: true })}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                rows={4}
                placeholder="Enter challenge statements (one per line)"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Duration (hours)</label>
                <select
                  {...register("duration_hours")}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value={12}>12 hours</option>
                  <option value={24}>24 hours</option>
                  <option value={36}>36 hours</option>
                  <option value={48}>48 hours</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Team Size</label>
                <input
                  {...register("team_size")}
                  type="number"
                  min={1}
                  max={10}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Experience Level</label>
              <select
                {...register("experience_level")}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Skills (comma-separated)</label>
              <input
                {...register("skills")}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="frontend, backend, ai"
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Hackathon Context (Optional)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Sponsor Tracks</label>
              <input
                {...register("tracks")}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="Generative AI, Agentic AI"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Evaluation Criteria</label>
              <textarea
                {...register("evaluation_criteria")}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                rows={3}
                placeholder="innovation, technical complexity, impact"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Available APIs</label>
              <input
                {...register("apis")}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="OpenAI, Twilio, Stripe"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Available Datasets</label>
              <input
                {...register("datasets")}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="Dataset names (comma-separated)"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Additional Notes</label>
              <textarea
                {...register("notes")}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                rows={3}
                placeholder="Any additional context..."
              />
            </div>
          </CardContent>
        </Card>

        {createProject.error && (
          <p className="text-sm text-destructive">
            Failed to create project. Please try again.
          </p>
        )}

        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? "Creating..." : "Start Analysis"}
        </Button>
      </form>
    </main>
  );
}
