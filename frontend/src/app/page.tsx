"use client";

import React from "react";

export default function LandingPage() {
  return (
    <div className="flex-1 bg-zinc-950 text-zinc-50 font-sans selection:bg-indigo-500 selection:text-white relative overflow-hidden flex flex-col justify-between min-h-screen">
      {/* Background gradients for premium aesthetic */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-900/20 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-purple-900/20 blur-[120px] pointer-events-none" />

      {/* Premium Header / Navbar */}
      <header className="sticky top-0 z-50 border-b border-zinc-800/50 bg-zinc-950/70 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center font-bold text-black text-lg shadow-lg shadow-indigo-500/20">
              eX
            </div>
            <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
              exHacker
            </span>
          </div>

          <div className="flex items-center space-x-4">
            <div className="hidden sm:flex items-center space-x-2 bg-zinc-900/80 border border-zinc-800 px-3 py-1 rounded-full text-xs text-zinc-400">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>System: Ready</span>
            </div>
            <a
              href="https://github.com/muneer320/exHacker-hackArena"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-zinc-400 hover:text-white transition-colors duration-200"
              id="link-github"
            >
              GitHub
            </a>
          </div>
        </div>
      </header>

      {/* Main Hero & Content Section */}
      <main className="max-w-7xl mx-auto px-6 py-20 flex-1 flex flex-col justify-center relative z-10">
        <div className="text-center max-w-3xl mx-auto space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 bg-indigo-500/10 border border-indigo-500/30 px-3 py-1.5 rounded-full text-xs text-indigo-400 font-medium">
            <span>🚀 Hackathon Season Co-Pilot</span>
          </div>

          {/* Hero Heading */}
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-none">
            The Multi-Agent
            <span className="block mt-2 bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Hackathon Co-Pilot
            </span>
          </h1>

          {/* Subtext */}
          <p className="text-zinc-400 text-lg sm:text-xl font-normal leading-relaxed">
            Transform raw challenge statements into structured, build-ready roadmaps, validated competitor research, technical architectures, presentation slides, and pitches in under 5 minutes.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <button
              id="btn-create-project"
              onClick={() => {
                alert("Project creation flow starting shortly...");
              }}
              className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-semibold rounded-xl transition-all duration-300 transform hover:scale-[1.02] shadow-lg shadow-indigo-500/20 cursor-pointer"
            >
              Start Analysis Workflow
            </button>
            <button
              id="btn-load-demo"
              onClick={() => {
                alert("Loading pre-computed project demo...");
              }}
              className="w-full sm:w-auto px-8 py-4 bg-zinc-900 border border-zinc-850 hover:bg-zinc-850 text-zinc-300 hover:text-white font-semibold rounded-xl transition-all duration-300 cursor-pointer"
            >
              Showcase Demo Project
            </button>
          </div>
        </div>

        {/* Workflow Overview Visualizer */}
        <div className="mt-28 space-y-8">
          <div className="text-center">
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">The 10-Stage Planning Engine</h2>
            <p className="text-zinc-400 text-sm mt-2">Specialized AI agents collaborating behind the scenes through shared state.</p>
          </div>

          {/* Pipeline grid with glassmorphism */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-6">
            {workflowStages.map((stage, idx) => (
              <div 
                key={idx}
                className="group p-6 bg-zinc-900/40 border border-zinc-800/60 rounded-2xl hover:border-zinc-700/60 transition-all duration-300 backdrop-blur-sm relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-bl from-indigo-500/5 to-purple-500/5 rounded-bl-full pointer-events-none group-hover:from-indigo-500/10 group-hover:to-purple-500/10 transition-colors duration-300" />
                <div className="flex items-center space-x-3 mb-3">
                  <span className="text-xs font-mono text-zinc-500 bg-zinc-800 px-2.5 py-0.5 rounded-full">
                    Stage 0{idx + 1}
                  </span>
                  <span className="text-xs text-indigo-400 font-semibold uppercase tracking-wider">
                    {stage.category}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-zinc-100 group-hover:text-indigo-400 transition-colors duration-200">
                  {stage.title}
                </h3>
                <p className="text-zinc-400 text-sm mt-2 leading-relaxed">
                  {stage.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Premium Footer */}
      <footer className="border-t border-zinc-900 bg-zinc-950 py-10 text-center text-xs text-zinc-500 relative z-10">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 exHacker. Created for high-velocity builders.</p>
          <div className="flex space-x-4">
            <span className="text-zinc-600">v2.0 Architecture</span>
            <span className="text-zinc-600">|</span>
            <span className="text-zinc-400">Main Branch</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

const workflowStages = [
  {
    category: "Analyze",
    title: "Challenge Intelligence",
    description: "Parses hackathon rules, themes, constraints, and sponsor resource guides automatically."
  },
  {
    category: "Analyze",
    title: "Problem Analyst",
    description: "Identifies stakeholders, outlines pain points, and defines target MVP success metrics."
  },
  {
    category: "Ideate",
    title: "Opportunity Planner",
    description: "Evaluates market whitespace and maps out technical levers for differentiation."
  },
  {
    category: "Ideate",
    title: "Idea Generator",
    description: "Synthesizes inputs to generate 3-5 distinct project concepts tailored to team skills."
  },
  {
    category: "Research",
    title: "Idea Validator",
    description: "Researches competitors, APIs, and GitHub repos to score feasibility and novelty."
  },
  {
    category: "Build",
    title: "Tech Stack Advisor",
    description: "Recommends a buildable, deployable set of tech languages customized to constraints."
  },
  {
    category: "Build",
    title: "Solution Architect",
    description: "Generates high-level system diagrams, entity designs, database schemas, and endpoints."
  },
  {
    category: "Build",
    title: "Build Accelerator",
    description: "Provides modular implementation tasks and code generation prompts to speed up setup."
  },
  {
    category: "Present",
    title: "Presentation & Pitch",
    description: "Outputs complete slides structure, talking scripts, narratives, and mock Q&As."
  }
];
