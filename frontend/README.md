# exHacker Frontend

Next.js 16 application for the exHacker hackathon co-pilot.

---

## App Architecture

```
src/
├── app/                    # Next.js App Router pages
│   ├── page.tsx            # Landing / hero
│   ├── generate/page.tsx   # Legacy generation flow
│   ├── new-project/page.tsx
│   ├── results/page.tsx
│   └── workflow/page.tsx   # 10-step HITL workflow
├── components/             # React components
│   ├── ui/                 # shadcn-style primitives
│   │   ├── badge.tsx
│   │   ├── card.tsx
│   │   ├── scroll-area.tsx
│   │   └── tabs.tsx
│   ├── agent-tabs.tsx      # Agent log inspector
│   ├── AnimatedBackground.tsx
│   ├── ChallengeForm.tsx
│   ├── Hero.tsx
│   ├── IdeaCard.tsx
│   ├── LoadingScreen.tsx
│   ├── Navbar.tsx
│   ├── PitchCard.tsx
│   └── ReportCard.tsx
├── lib/
│   ├── api.ts             # Backend API client
│   └── utils.ts           # cn() utility
├── types/
│   ├── index.ts           # Re-exports
│   └── project.ts         # TypeScript interfaces
├── stores/
│   └── index.ts           # State store scaffold
└── features/
    └── index.ts           # Feature module scaffold
```

---

## Routing

| Route | Page | Purpose |
|-------|------|---------|
| `/` | `page.tsx` | Landing page with hero |
| `/generate` | `generate/page.tsx` | Legacy one-shot generation |
| `/new-project` | `new-project/page.tsx` | New project form |
| `/results` | `results/page.tsx` | View generation results |
| `/workflow` | `workflow/page.tsx` | 10-step HITL workflow |

---

## State Management

State is managed through the backend HITL workflow API. The frontend fetches step data via API calls rather than maintaining local state. Scaffold files under `src/stores/` and `src/features/` are ready for future client-side state management.

---

## API Integration

All backend communication goes through `src/lib/api.ts`. The base URL is configured via `NEXT_PUBLIC_API_BASE_URL` environment variable (defaults to `http://localhost:8000`).

---

## Local Development

```bash
cd frontend
npm install
cp ../.env.example .env.local
# Edit .env.local: set NEXT_PUBLIC_API_BASE_URL if needed
npm run dev
```

---

## Build

```bash
npm run build
npm start
```

> Note: The `next build` currently requires `@tailwindcss/postcss` — ensure it's installed as a dev dependency.
