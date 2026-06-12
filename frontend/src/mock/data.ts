// Mock data for the exHacker frontend
// Use this until the backend is stable

export const AGENTS = [
  {
    id: 'challenge_intelligence',
    name: 'Challenge Intelligence',
    description: 'Decodes the hackathon challenge and extracts key requirements.',
    color: '#06B6D4',
    icon: 'Target',
  },
  {
    id: 'problem_analysis',
    name: 'Problem Analyst',
    description: 'Analyzes stakeholders, pain points, and constraints.',
    color: '#8B5CF6',
    icon: 'Search',
  },
  {
    id: 'opportunity_discovery',
    name: 'Opportunity Planner',
    description: 'Identifies market gaps and strategic opportunities.',
    color: '#F59E0B',
    icon: 'TrendingUp',
  },
  {
    id: 'idea_generation',
    name: 'Idea Generator',
    description: 'Generates 5 diverse, validated project concepts.',
    color: '#EC4899',
    icon: 'Lightbulb',
  },
  {
    id: 'idea_validation',
    name: 'Idea Validator',
    description: 'Scores ideas across innovation, feasibility, and differentiation.',
    color: '#22C55E',
    icon: 'CheckCircle',
  },
  {
    id: 'tech_stack',
    name: 'Tech Stack Advisor',
    description: 'Recommends the optimal technology stack for speed and scalability.',
    color: '#3B82F6',
    icon: 'Layers',
  },
  {
    id: 'architecture',
    name: 'Solution Architect',
    description: 'Designs the full system architecture with component diagrams.',
    color: '#3B82F6',
    icon: 'GitBranch',
  },
  {
    id: 'build_accelerator',
    name: 'Build Accelerator',
    description: 'Creates a detailed build plan with milestones and priorities.',
    color: '#22C55E',
    icon: 'Zap',
  },
  {
    id: 'presentation',
    name: 'Presentation Agent',
    description: 'Generates compelling slide content and presentation flow.',
    color: '#A855F7',
    icon: 'Presentation',
  },
  {
    id: 'pitch',
    name: 'Pitch Coach',
    description: 'Crafts 30-second, 2-minute, and 5-minute pitches with Q&A prep.',
    color: '#F97316',
    icon: 'Mic',
  },
];

export const DEMO_FINANCE_PROJECT = {
  id: 'demo-finance-001',
  name: 'FinanceAI — Student Money Coach',
  challenge:
    'Build an AI solution for improving financial literacy among students. The platform should help students understand budgeting, saving, and investing in a way that is engaging and actionable.',
  theme: 'Education & Finance',
  rules: ['Open source stack preferred', 'Must include an AI component', 'Mobile-first design'],
  team: { size: 4, skills: ['React', 'Python', 'ML', 'Design'], experience: 'Intermediate' },
  constraints: { duration: '48 hours', tools: 'Any', preferredTech: ['Next.js', 'FastAPI', 'OpenAI'] },
  
  research: {
    competitors: [
      { name: 'YNAB', description: 'Personal budgeting tool', strengths: ['Strong community', 'Proven model'], weaknesses: ['Paid only', 'Complex UI'] },
      { name: 'Mint', description: 'Free financial tracking', strengths: ['Free tier', 'Bank integration'], weaknesses: ['No AI', 'Ads-supported'] },
      { name: 'Khan Academy Finance', description: 'Education-focused finance', strengths: ['Free', 'Trusted brand'], weaknesses: ['Static content', 'No personalization'] },
    ],
    apis: [
      { name: 'Plaid API', purpose: 'Bank account connectivity', pricing: 'Freemium', docsUrl: 'https://plaid.com/docs' },
      { name: 'OpenAI API', purpose: 'AI financial coaching', pricing: 'Pay-per-use', docsUrl: 'https://platform.openai.com' },
      { name: 'Alpha Vantage', purpose: 'Stock market data', pricing: 'Free tier', docsUrl: 'https://alphavantage.co' },
    ],
    ossProjects: [
      { name: 'FinKit', stars: 2400, relevance: 'Financial calculation utilities', repoUrl: 'https://github.com/finkit' },
      { name: 'budget.js', stars: 890, relevance: 'Budget management logic', repoUrl: 'https://github.com/budgetjs' },
    ],
    insights: [
      '72% of students feel unprepared for real-world finances',
      'Gamification increases financial app retention by 3x',
      'AI-personalized advice shows 40% better habit formation',
    ],
  },

  ideas: [
    {
      id: 'idea-1',
      title: 'AI Finance Coach',
      tagline: 'A personalized AI advisor that learns your spending patterns and guides you.',
      scores: { innovation: 92, feasibility: 88, complexity: 65, differentiation: 90 },
      strengths: ['High personalization', 'Proven AI tech', 'Scalable'],
      weaknesses: ['Data privacy concerns', 'AI accuracy risk'],
      risks: ['Regulatory compliance', 'User trust building'],
      competitors: ['YNAB', 'Cleo AI'],
      apis: ['OpenAI', 'Plaid'],
    },
    {
      id: 'idea-2',
      title: 'Gamified Savings Platform',
      tagline: 'Turn saving money into a competitive game with friends.',
      scores: { innovation: 85, feasibility: 90, complexity: 55, differentiation: 82 },
      strengths: ['High engagement', 'Easy to build', 'Viral potential'],
      weaknesses: ['Novelty fades', 'Shallow financial education'],
      risks: ['User retention long-term'],
      competitors: ['Habitica (adapted)'],
      apis: ['Plaid', 'Firebase'],
    },
    {
      id: 'idea-3',
      title: 'Financial Habit Builder',
      tagline: 'Micro-habit coaching with AI nudges to build lasting financial behavior.',
      scores: { innovation: 78, feasibility: 92, complexity: 45, differentiation: 75 },
      strengths: ['Simple to use', 'Evidence-based', 'Low complexity'],
      weaknesses: ['Crowded market', 'Low wow factor'],
      risks: ['Low differentiation'],
      competitors: ['Streaks', 'Finhabits'],
      apis: ['OpenAI', 'Twilio'],
    },
    {
      id: 'idea-4',
      title: 'Student Budget Assistant',
      tagline: 'Voice-first budget assistant designed specifically for student life.',
      scores: { innovation: 88, feasibility: 75, complexity: 70, differentiation: 86 },
      strengths: ['Unique interface', 'Student-focused', 'Quick adoption'],
      weaknesses: ['Voice accuracy issues', 'Accessibility barriers'],
      risks: ['Voice privacy'],
      competitors: ['Alexa Finance Skills'],
      apis: ['Whisper API', 'Plaid'],
    },
    {
      id: 'idea-5',
      title: 'Career Planning Companion',
      tagline: 'Financial planning tied to career goals and salary milestones.',
      scores: { innovation: 80, feasibility: 82, complexity: 60, differentiation: 78 },
      strengths: ['Unique angle', 'Long-term value', 'Emotional hook'],
      weaknesses: ['Complex data', 'Longer build time'],
      risks: ['Scope creep'],
      competitors: ['LinkedIn Financial Tools'],
      apis: ['LinkedIn API', 'Bureau of Labor Statistics'],
    },
  ],

  selectedIdea: 'idea-1',

  architecture: {
    mermaidDiagram: `graph TB
    subgraph Frontend["🖥️ Frontend (Next.js)"]
      UI[React UI]
      State[Zustand Store]
    end
    subgraph Backend["⚙️ Backend (FastAPI)"]
      API[REST API]
      Agents[AI Agents]
      WF[LangGraph Engine]
    end
    subgraph Data["💾 Data Layer"]
      DB[(PostgreSQL)]
      Cache[(Redis)]
    end
    subgraph AI["🤖 AI Layer"]
      LLM[Groq / Gemini]
      Research[Tavily Search]
    end
    subgraph External["🔗 External"]
      Plaid[Plaid API]
      OAI[OpenAI API]
    end
    UI --> API
    API --> WF
    WF --> Agents
    Agents --> LLM
    Agents --> Research
    API --> DB
    API --> Cache
    Agents --> Plaid
    Agents --> OAI`,
    components: [
      { name: 'Next.js Frontend', type: 'frontend', tech: 'React 19, Tailwind CSS, Framer Motion' },
      { name: 'FastAPI Backend', type: 'backend', tech: 'Python 3.12, FastAPI, LangGraph' },
      { name: 'PostgreSQL', type: 'database', tech: 'PostgreSQL 15 + SQLAlchemy' },
      { name: 'Groq / Gemini', type: 'ai', tech: 'LLM providers with fallback chain' },
      { name: 'Tavily Search', type: 'ai', tech: 'Grounded web research API' },
      { name: 'Plaid API', type: 'external', tech: 'Bank connectivity and financial data' },
    ],
  },

  buildPlan: {
    milestones: [
      { day: 'Day 1', title: 'Foundation', tasks: ['Setup repos', 'Design system', 'DB schema', 'Auth flow'] },
      { day: 'Day 2', title: 'Core Features', tasks: ['AI coaching engine', 'Budget tracking', 'Plaid integration', 'User profiles'] },
      { day: 'Day 3', title: 'Intelligence', tasks: ['Personalization model', 'Gamification layer', 'Notification system', 'Analytics'] },
      { day: 'Day 4', title: 'Polish & Demo', tasks: ['UI polish', 'Demo data', 'Performance optimization', 'Presentation prep'] },
    ],
  },

  techStack: {
    frontend: [{ name: 'Next.js 15', reason: 'SSR + App Router for optimal performance' }, { name: 'Tailwind CSS', reason: 'Rapid UI development' }, { name: 'Framer Motion', reason: 'Premium animations' }],
    backend: [{ name: 'FastAPI', reason: 'High performance async Python' }, { name: 'LangGraph', reason: 'Stateful AI workflow orchestration' }, { name: 'SQLAlchemy', reason: 'Type-safe ORM' }],
    database: [{ name: 'PostgreSQL', reason: 'Reliable relational data' }, { name: 'Redis', reason: 'Caching and session management' }],
    ai: [{ name: 'Groq', reason: 'Fast LLM inference' }, { name: 'Gemini', reason: 'Fallback provider' }, { name: 'Tavily', reason: 'Grounded web research' }],
    infrastructure: [{ name: 'Docker', reason: 'Containerized deployment' }, { name: 'GitHub Actions', reason: 'CI/CD pipeline' }],
  },

  pitch: {
    thirtySecond: `Students are financially illiterate and existing tools are built for adults. FinanceAI is an AI-powered money coach that speaks student — understanding dorm budgets, part-time income, and future career goals. In a 48-hour hackathon, we built a fully functional platform that personalizes financial guidance using LangGraph agents, achieving 40% better habit formation than generic advice. This is what financial literacy should look like for Gen Z.`,
    twoMinute: `The problem is stark: 72% of students graduate without basic financial skills. Existing tools like YNAB and Mint are adult-focused, complex, and not designed for student realities.\n\nFinanceAI changes this. Our AI coach learns your spending patterns, adapts to your student lifestyle, and gives bite-sized, actionable guidance — not lectures.\n\nWhat we built: A Next.js frontend with real-time AI interactions, a FastAPI backend with a 10-agent LangGraph workflow, and Plaid integration for real financial data. The system can analyze a challenge, generate ideas, validate them with grounded research, design architecture, and pitch the solution — all in minutes.\n\nOur competitive advantage: We're the only student-first AI finance platform. Our AI doesn't just track — it coaches, nudges, and celebrates wins.\n\nWe're not building an app. We're building the financial confidence of the next generation.`,
    judgeQA: [
      { question: 'How is this different from existing apps?', answer: 'We are student-first — built for dorm budgets, part-time income, and future career planning. Competitors serve adults. We serve the next generation.' },
      { question: 'How will students trust AI with their money?', answer: 'We use read-only Plaid access. No money movement. All AI advice is clearly labeled. Users stay in control.' },
      { question: 'What is the monetization model?', answer: 'Freemium. Basic coaching free forever. Premium tier at $4.99/month for advanced insights and investment guidance.' },
      { question: 'Can this scale?', answer: 'Built on FastAPI + PostgreSQL + Redis. Stateless agents enable horizontal scaling. We can handle 100k users on Day 1 with standard cloud infrastructure.' },
    ],
  },

  overallScore: 92,
};

export const WORKFLOW_STAGES = [
  { id: 'challenge_intelligence', name: 'Challenge Intelligence', icon: 'Target' },
  { id: 'problem_analysis', name: 'Problem Analysis', icon: 'Search' },
  { id: 'opportunity_discovery', name: 'Research', icon: 'Globe' },
  { id: 'idea_generation', name: 'Idea Generation', icon: 'Lightbulb' },
  { id: 'idea_validation', name: 'Idea Validation', icon: 'CheckCircle' },
  { id: 'idea_selection', name: 'Idea Selection', icon: 'Star' },
  { id: 'architecture', name: 'Architecture', icon: 'GitBranch' },
  { id: 'build_plan', name: 'Build Plan', icon: 'Calendar' },
  { id: 'presentation', name: 'Presentation', icon: 'Monitor' },
  { id: 'pitch', name: 'Pitch Coach', icon: 'Mic' },
];
