# exHacker Frontend Audit — akshaj658/exHacker vs our codebase

> **Date:** 2026-07-07  
> **Reference:** https://github.com/akshaj658/exHacker  
> **Our frontend:** `/home/foaly/projects/exHacker/frontend/`

---

## Phase 1 — Repository Audit

### Overview

The reference frontend is a **purpose-built, single-page workflow app** with 5 pages and 8 components, totalling ~2,200 lines of code (mostly in `workflow/page.tsx` at 1,791 lines and `results/page.tsx` at 2,227 lines). It uses Next.js 16 with React 19, Tailwind CSS v4, and Google Fonts (Syne, Inter, JetBrains Mono).

### Strengths

| Area | Assessment |
|---|---|
| **Design System** | Excellent. Cohesive palette (Black, Blue #3d7cf6, Lime #c2ff4d, Sky #a8d8ff), Syne display font, polished CSS utility classes, animated background orbs, dot grid, noise texture |
| **Typography** | Premium. Clamp-based responsive sizing, clear hierarchy (`.d1`-`.d4`, `.body-*`), intentional letter-spacing |
| **Animations** | Purposeful. 4 animated background orbs with drifting keyframes, staggered fade-up entrances (`.anim-fade-up-*`), subtle grid fade, spin, pulse, glowPulse |
| **CSS Architecture** | Single-file CSS with well-organized sections: tokens, backgrounds, reset, typography, layout, buttons, forms, badges, cards, score bars, step sidebar, terminal, tab strip, animations, noise overlay, scrollbar, selection |
| **Workflow UX** | Pipeline visualization with step-by-step progress. Terminal-window esthetic for the "how it works" section. Clear human-in-the-loop checkpoint (step 05, "YOU") |
| **Loading states** | The `LoadingScreen` component with spinner, animated dots, and step label is better than our plain spinner |
| **Project creation form** | More comprehensive than ours. Challenge textarea with example buttons, hackathon name field, track/sponsor chip selectors |
| **Results view** | Tab-based results with 9 tabs (overview, ideas, rankings, winner, blueprint, slides, pitches, report, docs) |

### Weaknesses

| Area | Assessment |
|---|---|
| **Component organization** | Monolithic files. `workflow/page.tsx` (1,791 lines) and `results/page.tsx` (2,227 lines) contain dozens of inline components — no separation of concerns |
| **State management** | Pure `useState`/`sessionStorage` — no React Query, no context, no caching. Session persistence via raw `sessionStorage.setItem/getItem` scattered throughout |
| **Error handling** | Minimal. Basic try/catch in API calls, single error state per form, no error boundaries |
| **Empty states** | None. Pages assume data exists |
| **Loading states** | Only the one full-screen loading spinner. No skeleton loading, partial updates, or streaming |
| **Responsive design** | Minimal. Only `.hide-mobile` utility and `.container` padding breakpoint. No mobile-first consideration |
| **Accessibility** | None. No ARIA labels, no keyboard navigation, no focus management, no screen reader support |
| **Browser support** | Only modern Chrome/Edge/Safari/Firefox — no fallbacks for CSS custom properties |
| **Performance** | All CSS states in single file (no code splitting), inline styles everywhere (no CSS extraction), large component files |
| **Code quality** | Inconsistent naming, hardcoded strings mixed with logic, no TypeScript strict mode, no tests |
| **IdeaCard component** | Has its own color system (VOID, DEEP, SLATE, MINT, INK) that mismatches the main design system — inconsistent |
| **Routing** | No route transitions, no loading states between pages, direct `router.push` with no error recovery |
| **API client** | Thin fetch wrapper with no retry, no caching, no mock fallback, no request deduplication |
| **TypeScript** | `types/project.ts` is comprehensive but many components cast to `Record<string, unknown>` and use `as` |
| **Duplication** | ScoreBar, Label, DataPanel, BulletList micro-components are duplicated across `workflow` and `results` pages |
| **No custom hooks** | All logic lives in components — no extraction to hooks |
| **Magic numbers** | Inline pixel values everywhere — no spacing scale |

---

## Phase 2 — Design Comparison

### Per-component classification

| Component | Our Version | Their Version | Decision | Reasoning |
|---|---|---|---|---|
| **Design System / CSS** | ✅ Legacy purple, inline styles everywhere | ✅ Black/Blue/Lime/Sky, well-organized CSS | **ADOPT THEIRS** | Already partially adopted (globals.css v3). Their CSS is objectively better organized and more professional |
| **Landing Page** | ✅ Single-input hero | ✅ Full marketing page with pipeline visualization, terminal, stats, feature cards | **ADOPT THEIRS** | Their Hero.tsx is a complete, polished landing page that explains the product. Ours is too minimal |
| **Project Creation** | ✅ Single text input | ✅ Multi-field form with challenge + hackathon + tracks + sponsors | **MERGE** | Their form has better UX (example buttons, chips), but we need fewer fields for the MVP. Keep their form layout, use our simplified fields |
| **Navbar** | ✅ Basic React component | ✅ Same basic structure | **MERGE** | Both are similar. Their logo design (blue square + "ex/Hacker") is better. Keep our import structure |
| **Idea Cards** | ✅ Inline in page.tsx (rich) | ✅ Separate IdeaCard.tsx (different color system) | **MERGE** | Our 8-score format is richer and aligned with Product Bible. Their card layout and spacing is better. Merge their visual hierarchy with our score structure |
| **Results/Tabs Layout** | ✅ Inline tabs per page | ✅ Tab-based results page with 9 tabs | **ADOPT THEIRS** | Their results page tab system is more complete. We should use their tab structure extended with our specialist tabs |
| **Workflow Progress** | ❌ Missing | ✅ Pipeline step visualization with status indicators | **ADOPT THEIRS** | This is a core product feature we don't have. Their step sidebar is excellent |
| **Loading Screen** | ✅ Basic spinner | ✅ Full-screen with animated dots and step label | **MERGE** | Their animated dots pattern + our confidence tracking |
| **Architecture View** | ❌ Missing | ✅ BlueprintOutput with product vision, architecture diagram | **ADOPT THEIR PATTERN** | But fill with our S7 data schema |
| **API Client** | ✅ With mock fallback | ✅ Thin fetch wrapper | **KEEP OURS** | Our mock fallback and request function is more robust |
| **TypeScript Types** | ✅ Product Bible-aligned | ✅ Comprehensive but inconsistent | **KEEP OURS** | Our types match our backend contracts |
| **Routing** | ✅ `/projects/[id]` — tab based | ✅ `/generate` → `/workflow` → `/results` — page based | **KEEP OURS** | Our tab-per-project model is better for the 5-specialist architecture |

### Key Adoptions

1. **ADOPT** Their CSS design system (already done in `globals.css` v3) ✅
2. **ADOPT** Their landing page (Hero.tsx) — replace our minimal landing
3. **ADOPT** Their pipeline step visualization — add to our project workflow
4. **ADOPT** Their results tab structure — extend for our specialist tabs
5. **MERGE** Their project creation form — use their layout, our field set
6. **MERGE** Their loading states — animated dots, step labels
7. **MERGE** Their Navbar logo — blue square with "ex/Hacker"

### What We Keep

1. **KEEP** Our tab-per-project layout (better for multi-specialist navigation)
2. **KEEP** Our API client with mock fallback
3. **KEEP** Our TypeScript types (Product Bible aligned)
4. **KEEP** Our 8-dimension scoring format
5. **KEEP** Our challenge/competitor/documentation tab content
6. **KEEP** Our decision timeline tab

### What We Rebuild

1. **REBUILD** The landing page — adopt their Hero structure with our value proposition
2. **REBUILD** The results page — their 9-tab structure with our specialist content

---

## Phase 3 — Gap Analysis (vs Product Bible)

| Requirement | Our Frontend | Their Frontend | Gap |
|---|---|---|---|
| Challenge Intelligence | ✅ Tab exists | ❌ Part of problem_analyst output | Our tab is better |
| Research Dashboard | ✅ Tab exists | ❌ Missing | We lead |
| Competitor Analysis | ✅ Tab exists | ❌ Missing | We lead |
| Ideas (5 scored) | ✅ Inline in Directions tab | ✅ 10 ideas with ranking | Close |
| Architecture Blueprint | ❌ Missing | ✅ BlueprintOutput component | Theirs exists but uses different schema |
| Documentation Package | ❌ Missing | ❌ Only final_report | Both missing — but S13 exists on backend |
| Decision Timeline | ✅ Tab exists | ❌ Missing | We lead |
| Shared Memory | ❌ Missing | ❌ Missing | Both missing |
| Pipeline Visualization | ❌ Missing | ✅ Step sidebar with status | They lead |
| Export Downloads | ✅ Markdown+JSON | ❌ Only via report | We lead |
| Project Dashboard | ❌ Missing | ❌ Missing | Both missing |
| Keyboard Navigation | ❌ Missing | ❌ Missing | Both missing |
| Responsive Layout | 🟡 Partial | 🟡 Partial | Both weak |
| Accessibility | ❌ Missing | ❌ Missing | Both missing |
| Design System v3 | ✅ Adopted from theirs | ✅ Original | Tied |
| Loading Skeletons | ❌ Missing | ❌ Missing | Both missing |
| Streaming Generation | ❌ Missing | ❌ Missing | Both missing |
| Dark Theme | ✅ Always dark | ✅ Always dark | Tied |

**Summary:** We lead on 8/18 requirements (Challenge, Research, Competitors, Documentation, Timeline, Export, Types, Backend integration). They lead on 2/18 (Pipeline visualization, Landing page). 8/18 are missing from both.

---

## Phase 4 — Improvement Plan

### High Priority

1. **Pipeline Visualization** — Adopt their step-by-step workflow sidebar. Show our 5 specialist stages with status (pending, running, completed, failed). Each stage expandable to show output summary.

2. **Landing Page** — Replace our minimal input form with their Hero layout: headline, animated terminal, stats row, feature cards. Keep our creation form but use their styling.

3. **Results Tab System** — Adopt their 9-tab structure. Map our tabs: Overview, Challenge Intelligence, Research, Competitors, Ideas, Architecture, Documentation, Timeline, Export.

4. **Idea Cards** — Merge their card layout with our 8-score format. Their visual hierarchy (rank number, title, score ring) is better. Our score bars and feature tags are richer.

### Medium Priority

5. **Loading States** — Implement their animated dots pattern across all specialist loading states. Add step labels and estimated time.

6. **Navbar Redesign** — Their logo (blue square + "ex/Hacker") is more polished. Adopt it.

7. **Project Creation Form** — Adopt their two-column layout (form + filters). Keep our simplified field set.

8. **Empty States** — Add illustrations and guidance for every specialist tab when no data exists.

### Low Priority

9. **Keyboard Navigation** — Tab indexing, Enter to select ideas, Escape to close expandables.

10. **Responsive Layout** — Mobile breakpoints for project detail tabs, pipeline sidebar, and results view.

11. **Micro-interactions** — Hover scale on cards, button press effects, score bar entrance animations.

12. **Accessibility** — ARIA labels, focus management, screen reader announcements for status changes.

---

## Phase 5 — Migration Strategy

### Order of Operations

```
Step 1: Adopt Hero.tsx (replace our landing page)
  ├── Copy their Hero.tsx structure
  ├── Update value proposition text for our product
  ├── Import our Navbar instead of theirs
  └── Add our createProject API integration

Step 2: Adopt Navbar logo design
  ├── Blue square with "ex" / "Hacker" text
  └── Keep existing import structure

Step 3: Adopt loading screen pattern
  ├── Animated dots component
  ├── Step label + estimated time
  └── Reusable across all specialist calls

Step 4: Add pipeline visualization to project detail page
  ├── Sidebar with 5-7 stages
  ├── Status indicators
  ├── Expandable per-stage summaries
  └── Auto-highlights current stage

Step 5: Adopt results tab structure
  ├── Their tab bar component
  ├── Our specialist content per tab
  └── Smooth tab transitions

Step 6: Merge idea card designs
  ├── Their visual hierarchy (rank, title, score)
  ├── Our 8-dimension score bars
  ├── Our feature tags and effort estimate
  └── Expandable detail sections

Step 7: Project creation form merge
  ├── Their two-column layout
  ├── Their chip selectors for tracks
  ├── Our simplified field set
  └── Example buttons for quick start
```

### Risks

| Risk | Mitigation |
|---|---|
| **Landing page swap breaks URL paths** | Keep `/projects` routes intact. Landing page is `page.tsx` — swap content only |
| **Incompatible nav import paths** | Our Navbar is at `components/layout/Navbar.tsx`. Theirs is at `components/Navbar.tsx`. Keep our path, adopt their design |
| **CSS class name collisions** | Our globals.css v3 already uses their naming conventions. Verify no duplicate definitions |
| **Tab state lost on navigation** | Use URL search params instead of React state for tab selection |
| **Results page too large** | Keep our tab-per-project pattern. Don't adopt their monolithic results page — adopt only the tab component pattern |
| **Backend API contract mismatch** | Verify all API calls match our backend before merging any component |

### Estimated Effort

| Step | Effort | Risk |
|---|---|---|
| 1. Hero.tsx adoption | 1h | Low |
| 2. Navbar logo | 0.5h | Low |
| 3. Loading screen | 0.5h | Low |
| 4. Pipeline visualization | 2h | Medium |
| 5. Tab structure | 1.5h | Medium |
| 6. Idea cards merge | 2h | Medium |
| 7. Project form merge | 1h | Low |
| **Total** | **~8.5h** | |

---

## Phase 6 — Implementation (when approved)

Ready to begin when you give the go-ahead. Implementation order follows the migration strategy above — each step is a small, reversible commit. No backend changes required.
