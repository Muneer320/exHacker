# exHacker Frontend Architecture

> **Status:** Active reference for all frontend implementation  
> **Version:** 1.0  
> **Design System:** v3 (Black · Blue · Lime · Sky)

---

## 1. Layout Hierarchy

```
RootLayout
├── AnimatedBackground (4 orbs + dot grid + noise)
├── Navbar (fixed top, 60px)
├── Shell
│   ├── PipelineSidebar (optional, project detail pages)
│   └── PageContent
│       ├── HeroSection (landing only)
│       ├── ProjectWorkspace (project detail only)
│       │   ├── TabBar
│       │   └── TabContent
│       └── StandardContent (other pages)
└── Footer (optional)
```

### Layout primitives

| Component | Purpose | When used |
|---|---|---|
| `RootLayout` | Fonts, background layers, global structure | Always |
| `Navbar` | Brand, navigation, actions | All pages |
| `Shell` | Two-column (sidebar + content) | Project detail pages |
| `PageContent` | Single-column padded | Landing, auth, settings |
| `PipelineSidebar` | Stage-by-stage progression | Project detail, new project |
| `ProjectWorkspace` | Tabs inside project detail | All `/projects/[id]` pages |
| `TabBar` | Horizontal tab strip | Inside workspace |
| `TabContent` | Renders active tab | Inside workspace |

---

## 2. Navigation Model

### Routes

```
/                         → Landing (Hero)
/projects                 → Project list dashboard
/projects/[id]            → Project workspace (default tab: overview)
/projects/[id]?tab=ideas  → Direct tab link
/generate                 → New project form (alternative entry)
```

### Tab Navigation (inside ProjectWorkspace)

```
overview      → Project summary, status, quick actions
challenge     → Challenge Intelligence (S1)
research      → Research Dashboard (S2)
competitors   → Competitor Analysis (S3)
ideas         → Idea Selection (S5)
architecture  → Architecture Blueprint (S7)
docs          → Documentation Package (S13)
timeline      → Decision Timeline
export        → Download package
```

Tab state is stored in URL search params (`?tab=ideas`) for shareable links and browser back support.

### Breadcrumb pattern

```
exHacker → Projects → Project Name → [Active Tab]
```

---

## 3. Page Hierarchy

```
Landing (/)
├── Hero headline
├── Terminal animation (pipeline preview)
├── Stats row (agents, ideas, scripts)
├── Feature cards
├── Creation form
│   ├── Challenge textarea + examples
│   ├── Theme/track selector
│   ├── Hackathon details (optional)
│   └── Submit button
└── Footer

Project List (/projects)
├── Project cards grid
│   ├── Title, idea preview, status badge
│   └── Created date, last activity
├── Empty state
└── Create new button

Project Workspace (/projects/[id])
├── Pipeline sidebar (optional, collapsible)
├── TabBar
└── Tab content (varies by tab)

Settings (/projects/[id]/settings) — future
Auth (/auth) — future
```

---

## 4. Shared Components

### Navigation
- `Navbar` — Fixed top bar with brand, nav links, actions
- `Sidebar` — Pipeline stage visualization (collapsible on mobile)

### Layout
- `Shell` — Two-column layout wrapper
- `Container` — Max-width centered content (.container)
- `Card` — Surface-1 background, border, padding
- `Section` — Section with title, icon, accent color
- `Grid` — CSS grid wrapper with gap

### Data Display
- `ScoreBar` — Thin animated progress bar with label
- `ScoreRadar` — Multi-axis score visualization
- `Badge` — Pill-shaped status indicator (blue, lime, sky variants)
- `Tag` — Feature/topic chip (clickable, active state)
- `StatusDot` — Animated dot for pipeline stage status
- `ConfidenceIndicator` — Colored confidence badge
- `DifficultyBar` — Colored difficulty visualization
- `EffortChip` — Estimated hours chip

### Feedback
- `Spinner` — Loading spinner (.spinner)
- `LoadingScreen` — Full-page loading with animated dots + step label
- `SkeletonCard` — Placeholder card during loading
- `ErrorBanner` — Error message with icon
- `EmptyState` — Empty state with illustration and action

### Interactive
- `Button` — Primary, lime, ghost variants
- `Field` — Text input/textarea (.field)
- `ChipSelect` — Multi-select chip group
- `Accordion` — Expandable section
- `Modal` — Overlay dialog
- `TerminalWindow` — Terminal esthetic container

### Specialist-Specific
- `PipelineStage` — Single stage in pipeline sidebar
- `IdeaCard` — Full idea card with scoring
- `IdeaComparisonTable` — Side-by-side comparison
- `ArchitectureDiagram` — Mermaid diagram viewer
- `DocumentViewer` — Markdown file browser + viewer
- `TimelineEntry` — Single decision journal entry
- `CompetitorCard` — Competitor profile card
- `ResearchCategory` — Category result group

---

## 5. Reusable Layout Primitives

### Spacing Scale

```
--space-xs:  4px
--space-sm:  8px
--space-md:  16px
--space-lg:  24px
--space-xl:  40px
--space-2xl: 64px
--space-3xl: 80px
```

### Container Widths

```
--container-sm:  640px
--container-md:  960px
--container-lg:  1280px
```

### Border Radius

```
--r-sm: 2px
--r-md: 4px
--r-lg: 8px
--r-xl: 12px
--r-full: 9999px
```

### z-index Scale

```
--z-background: 0
--z-content: 1
--z-sticky: 10
--z-navbar: 100
--z-modal: 1000
--z-toast: 1100
```

---

## 6. Design Tokens

All tokens are defined as CSS custom properties in `globals.css`:

```css
:root {
  /* Backgrounds */
  --black: #080808;
  --surface-0: #0e0e0e;
  --surface-1: #161616;
  --surface-2: #202020;
  --surface-3: #2c2c2c;

  /* Borders */
  --border: rgba(255,255,255,0.06);
  --border-mid: rgba(255,255,255,0.10);
  --border-strong: rgba(255,255,255,0.18);

  /* Text */
  --text-1: #f2f2f2;
  --text-2: #888888;
  --text-3: #444444;

  /* Accent */
  --blue: #3d7cf6;
  --blue-dim: rgba(61,124,246,0.12);
  --blue-light: #93c5fd;
  --lime: #c2ff4d;
  --lime-dim: rgba(194,255,77,0.10);
  --sky: #a8d8ff;
  --sky-dim: rgba(168,216,255,0.10);

  /* Semantics */
  --success: var(--lime);
  --warning: #f59e0b;
  --error: #ef4444;
  --info: var(--sky);
}
```

---

## 7. Animation System

### Entrance Animations

```css
.anim-fade-up   { animation: fadeUp 0.5s ease both; }
.anim-fade-up-1 { animation: fadeUp 0.5s 0.1s ease both; }
.anim-fade-up-2 { animation: fadeUp 0.5s 0.2s ease both; }
.anim-fade-up-3 { animation: fadeUp 0.5s 0.3s ease both; }
.anim-fade-up-4 { animation: fadeUp 0.5s 0.4s ease both; }
.anim-fade-up-5 { animation: fadeUp 0.5s 0.5s ease both; }
.anim-fade-in   { animation: fadeIn 0.4s ease both; }
```

### Micro-interactions

| Element | Interaction | Duration | Easing |
|---|---|---|---|
| Button hover | TranslateY(-1px) + box-shadow | 0.2s | ease |
| Button active | TranslateY(0) | 0.1s | ease |
| Card hover | Border-color brighten | 0.2s | ease |
| Chip toggle | Background + color switch | 0.15s | ease |
| Score bar | Width transition | 1s | cubic-bezier(.25,.8,.25,1) |
| Pipeline dot | Pulse animation (active) | 1.5s | infinite |
| Tab switch | Border-color transition | 0.15s | ease |
| Page entrance | fadeUp staggered | 0.5s | ease |

### Background Orbs

4 gradient blobs with independent drift animations (18s-28s cycles) for a living background effect.

---

## 8. Component Ownership

| Component | Owns | Data Source | State |
|---|---|---|---|
| `LandingPage` | Hero, stats, form | `createProject()` API | Input values, loading, error |
| `ProjectListPage` | Project cards grid | `listProjects()` API | Projects, loading, empty |
| `ProjectWorkspace` | Tabs, sidebar | URL params | Active tab, project data |
| `PipelineSidebar` | Stage list, statuses | Project status | Active stage, stage data |
| `ChallengeTab` | S1 output | `getChallengeAnalysis()` | Analysis data, loading |
| `ResearchTab` | S2 categories | `startResearchV2()` | Research data, loading |
| `CompetitorsTab` | Competitor cards | `getCompetitorAnalysis()` | Competitor data, loading |
| `IdeasTab` | Idea cards, comparison | `getIdeas()` | Ideas, selected, loading |
| `ArchitectureTab` | Diagrams, components | `getArchitecture()` | Blueprint, loading |
| `DocsTab` | File viewer, download | `getDocs()` | Files, active file, loading |
| `TimelineTab` | Decision entries | `getDecisions()` | Decisions, filter, loading |
| `ExportTab` | Format buttons, download | `downloadExport()` | Status |

### Data Flow

```
React Component
  │
  ▼
API Client (services/api.ts)
  ├── Try backend (fetch)
  └── Fallback to mock
      │
      ▼
  Component State (useState)
  │
  ▼
  Render with loading/error/empty/success states
```

No global state store. No React Context for data. Each component fetches its own data via the API client. This keeps components independent and prevents cascading re-renders.

URL search params (`?tab=ideas`) are the single source of truth for which tab is active — shareable, bookmarkable, browser-back compatible.

---

## 9. Implementation Order

```
Phase 1: Shell (Navbar, Layout, Routing, Hero)
Phase 2: Pipeline (PipelineSidebar, stage visualization)
Phase 3: Project Creation (form merge)
Phase 4: Idea Selection (card redesign)
Phase 5: Workspace (tab system, specialist content)
Phase 6: Architecture Viewer (diagrams, components)
Phase 7: Documentation Viewer (file browser, markdown)
Phase 8: Polish (motion, keyboard, accessibility, responsive)
```
