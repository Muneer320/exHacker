import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    title: "Challenge Intelligence",
    description: "Analyze themes, tracks, resources, and evaluation criteria to understand the challenge landscape.",
    gradient: "from-violet-500/10 to-transparent",
    icon: "🎯",
  },
  {
    title: "Opportunity Discovery",
    description: "Identify high-impact opportunities, market gaps, and technical leverage points.",
    gradient: "from-cyan-500/10 to-transparent",
    icon: "💡",
  },
  {
    title: "Idea Validation",
    description: "Research competitors, existing solutions, and APIs to validate and score project ideas.",
    gradient: "from-amber-500/10 to-transparent",
    icon: "✅",
  },
  {
    title: "Solution Architecture",
    description: "Generate complete project blueprints with features, architecture, and database design.",
    gradient: "from-emerald-500/10 to-transparent",
    icon: "🏗️",
  },
  {
    title: "Build Acceleration",
    description: "Create implementation-ready prompts for Cursor, Claude, Lovable, and Bolt.",
    gradient: "from-rose-500/10 to-transparent",
    icon: "⚡",
  },
  {
    title: "Pitch Preparation",
    description: "Generate presentations, demos, and pitch materials tailored to judges and evaluation criteria.",
    gradient: "from-blue-500/10 to-transparent",
    icon: "🎤",
  },
];

export function Features() {
  return (
    <section className="relative px-4 py-24">
      <div className="absolute inset-0 bg-gradient-radial opacity-50" />
      <div className="relative mx-auto max-w-6xl">
        <h2 className="mb-4 text-center text-4xl font-bold">
          Everything You Need to Win
        </h2>
        <p className="mx-auto mb-12 max-w-xl text-center text-muted-foreground">
          Eleven specialized AI agents work together to take your hackathon project from idea to execution.
        </p>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, i) => (
            <Card
              key={feature.title}
              className="group relative overflow-hidden border-border/50 transition-all duration-300 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5"
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 transition-opacity duration-300 group-hover:opacity-100`} />
              <CardHeader className="relative">
                <div className="mb-2 text-2xl">{feature.icon}</div>
                <CardTitle className="text-lg">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent className="relative">
                <p className="text-sm leading-relaxed text-muted-foreground">
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
