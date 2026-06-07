import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    title: "Challenge Intelligence",
    description: "Analyze themes, tracks, resources, and evaluation criteria to understand the challenge landscape.",
  },
  {
    title: "Opportunity Discovery",
    description: "Identify high-impact opportunities, market gaps, and technical leverage points.",
  },
  {
    title: "Idea Validation",
    description: "Research competitors, existing solutions, and APIs to validate and score project ideas.",
  },
  {
    title: "Solution Architecture",
    description: "Generate complete project blueprints with features, architecture, and database design.",
  },
  {
    title: "Build Acceleration",
    description: "Create implementation-ready prompts for Cursor, Claude, Lovable, and Bolt.",
  },
  {
    title: "Pitch Preparation",
    description: "Generate presentations, demos, and pitch materials tailored to judges and evaluation criteria.",
  },
];

export function Features() {
  return (
    <section className="px-4 py-24">
      <div className="mx-auto max-w-6xl">
        <h2 className="mb-12 text-center text-3xl font-bold">
          Everything You Need to Win
        </h2>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.title}>
              <CardHeader>
                <CardTitle className="text-lg">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
