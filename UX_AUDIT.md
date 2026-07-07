# exHacker — UX Audit & Product Polish Plan

> **Date:** 2026-07-07  
> **Audience:** Engineering Lead  
> **Context:** Product-ready audit before launch

---

## Summary

This audit covers **10 pages**, **15 components**, **6 navigation patterns**, **8 data states**, and **the design system**. 47 issues found. 8 critical, 14 high, 12 medium, 8 low, 5 nice-to-have.

---

## 1. Landing Page (`/`)

### Issues

| # | Issue | Severity | Details |
|---|---|---|---|
| L1 | **No favicon** | **High** | Browser tab shows Next.js default. Critical for first impression. |
| L2 | **Stats row bleeds on mobile** | **High** | Stats use `padding-right: 40px` with `border-right`. On <768px the last item clips into the container edge. No mobile breakpoint for stats. |
| L3 | **CTA input field missing focus on scroll-down** | Medium | The bottom CTA section uses `id="create-input"` but `scrollIntoView` and `document.getElementById("create-input")?.focus()` is hardcoded — works on first click only. |
| L4 | **grad-blue class applied to non-text elements** | Low | `.grad-blue` uses `background-clip: text` but is applied to SVG elements which won't render the gradient. |
| L5 | **No loading skeleton for project creation** | **High** | After clicking "Start Free", the page transitions without showing what's happening. Only a brief flash before redirect. |
| L6 | **Terminal animation stops after last line** | Low | The terminal typewriter stops at the final line with a static cursor. No looping or reset. |

### Strengths
- Bold typography hierarchy (d1–d4 scale)
- Live terminal animation creates immediate trust
- Pipeline grid with hover effects is engaging
- Stats row communicates capability instantly

---

## 2. Navigation & Shell

### Issues

| # | Issue | Severity | Details |
|---|---|---|---|
| N1 | **No back-button scroll restoration** | **High** | Browser back from `/projects/[id]/ideas` → `/projects` loses scroll position. Next.js router doesn't restore scroll by default. |
| N2 | **Legacy CSS tokens used in project detail** | **High** | `page.tsx` (layout.tsx) references `var(--color-app-bg)`, `var(--color-border-default)`, `var(--color-text-primary)`, `var(--color-text-secondary)`, `var(--color-text-tertiary)` — these are deprecated aliases. The components should use `var(--black)`, `var(--border)`, etc. directly. |
| N3 | **No loading skeleton on page transitions** | **High** | When navigating between workspace sections, the content area flashes empty before loading. No skeleton or shimmer. |
| N4 | **Pipeline sidebar width is fixed 280px** | Medium | No collapse or resize capability. On 1280px screens, sidebar consumes 22% of width leaving only 1000px for content. |
| N5 | **Workspace navigation has no active section indicator animation** | Low | The active tab changes instantly. No underline animation or color transition. |
| N6 | **No breadcrumbs** | Low | Navigating from `/projects` → `/projects/[id]/ideas` loses hierarchy. User can't tell "where they are" relative to the project. |

### Strengths
- PipelineSidebar with status icons and expandable details feels alive
- WorkspaceNavigation with emoji icons is visually distinctive
- Layout persists across route changes (URL-driven tabs)

---

## 3. Challenge Intelligence Page

### Issues

| # | Issue | Severity | Details |
|---|---|---|---|
| C1 | **No refresh/regenerate button once analysis exists** | Medium | After first analysis, there's no way to re-run. The analyze button disappears. |
| C2 | **Difficulty scores use plain numbers without context** | Low | Scores show as `0-100` but no legend for what each band means (0-30 = low, etc.). |
| C3 | **Hidden problems use accent="warning" but some are low severity** | Low | All hidden problems get the same warning styling regardless of actual impact. |
| C4 | **No loading skeleton** | Medium | Page shows `LoadingState` spinner while loading. Should show skeleton cards matching content shape. |

### Strengths
- Executive summary with blue accent line + gradient background is visually strong
- ScoreRow with ScoreBar provides clear visual hierarchy
- Opportunity areas as pills is clean and scannable

---

## 4. Research Dashboard

### Issues

| # | Issue | Severity | Details |
|---|---|---|---|
| R1 | **No search within results** | **High** | 10 categories with potentially 100+ results. No way to filter or search for specific findings. |
| R2 | **Category filters are single-select only** | Medium | User can only view one category at a time. No multi-select or "compare categories" mode. |
| R3 | **Results load all at once** | Medium | No pagination or lazy loading. If research returns 200 results, everything renders immediately. |
| R4 | **No "generate research" button if empty** | Medium | Empty state has no action button. User needs to navigate elsewhere to trigger research. |
| R5 | **No confidence visual scale** | Low | Confidence percentages show as text pills but no visual bar or color gradient to make them scannable. |

### Strengths
- Category filter chips with active state are clean
- Synthesis card with opportunities + gaps is the strongest section
- Technology recommendations grid is useful

---

## 5. Competitor Analysis

### Issues

| # | Issue | Severity | Details |
|---|---|---|---|
| CP1 | **Competitor cards lack visual hierarchy** | Medium | Strengths/weaknesses/missing features are all similar-sized pills. Hard to scan which is most important. |
| CP2 | **No comparison matrix visualization** | **High** | The spec calls for "innovation heatmap" and "white-space map". Currently just text cards. |
| CP3 | **Innovation breakdown shows as ScoreRows** | Medium | 10+ rows in a 2-column grid is information-dense. Could use radar/spider chart for faster scanning. |
| CP4 | **No competitor count badge on cards** | Low | Each card should show which category they belong to (Product, Startup, OSS, etc.) from research. |

### Strengths
- Gap analysis grid with color-coded sections (patterns=blue, white space=lime, pain points=red)
- Quick wins section is immediately actionable
- Warnings with alternatives is the most differentiated section

---

## 6. Ideas Page (Flagship)

### Issues

| # | Issue | Severity | Details |
|---|---|---|---|
| I1 | **No comparison mode** | **Critical** | Users see 5 idea cards one after another. No way to compare two ideas side-by-side or in a table. The most important decision in the product has no comparison tool. |
| I2 | **No keyboard shortcuts for selection** | **High** | Pressing `1`-`5` should select idea 1-5. `Enter` to confirm. `Escape` to close expanded. None exist. |
| I3 | **Selection doesn't scroll to top** | Medium | After selecting an idea, the page doesn't scroll to the top or show a confirmation. The selected state is subtle. |
| I4 | **No "generate more ideas" button** | Medium | If user doesn't like any of the 5 ideas, there's no way to regenerate. |
| I5 | **Score bars lack entrance animation** | Low | Score bars use CSS transition but don't animate on page load. They appear instantly. |
| I6 | **No favorite/pin functionality** | Low | Users can't "shortlist" ideas before making a final decision. No intermediate state between "view" and "select". |
| I7 | **No comparison table** | Medium | The spec calls for "best for beginners", "best chance of winning", "fastest to build" comparisons. Currently just individual cards. |

### Strengths
- 7 score bars per card with overall ring provides rich data at a glance
- Expandable sections (problem, solution, differentiation, demo, risks) reduce cognitive load
- Feature tags with color coding (green=core, yellow ✱=stretch) are scannable
- Overall score color-coding (green≥80, yellow≥60, red<60) is intuitive

---

## 7. Architecture Page (Flagship)

### Issues

| # | Issue | Severity | Details |
|---|---|---|---|
| A1 | **Mermaid diagrams show raw source code, not rendered** | **Critical** | Mermaid blocks display as terminal-style code blocks. Users cannot see the actual diagram. Need Mermaid renderer (mermaid.js). |
| A2 | **No zoom/pan on diagrams** | Medium | When Mermaid rendering is added, users should be able to zoom and pan. |
| A3 | **Component cards lack technology badges** | Medium | Components have name + purpose but no clear technology stack badge. Should show framework, database, etc. at a glance. |
| A4 | **No download/export for architecture** | Low | Architecture is view-only. No way to download as PDF or share as image. |
| A5 | **API contracts are basic text** | Low | Method badges (GET/POST) + path. No request/response body examples. No curl examples. |

### Strengths
- Trade-off cards with pros/cons columns are excellent
- Architecture review with weak points + failure modes is honest and builds trust
- Scalability grid (hackathon version vs production) shows foresight

---

## 8. Documentation Browser

### Issues

| # | Issue | Severity | Details |
|---|---|---|---|
| D1 | **Custom markdown renderer is incomplete** | **Critical** | The custom renderer lacks: images, nested lists, link rendering, horizontal rules, checked task lists, HTML passthrough. Code blocks don't have syntax highlighting. |
| D2 | **No table of contents** | **High** | Long documents like PRD and README have no TOC. Users can't jump to sections. |
| D3 | **No search within document** | **High** | Users can't Cmd+F to find content within a document. The browser's native find works but doesn't include hidden markdown syntax. |
| D4 | **No mobile-responsive sidebar** | Medium | The 200px sidebar is fixed. On tablets and mobile, it consumes too much space. |
| D5 | **No "download all" button in toolbar** | Medium | "Download all" exists on the Exports page but not in the documentation toolbar where users naturally look for it. |
| D6 | **No "generating" state for incomplete files** | Medium | Docs that haven't been generated show "This document hasn't been generated yet" but no button to trigger generation. |
| D7 | **Sidebar doesn't show file sizes** | Low | Each file's size in KB would help users understand document scope. |
| D8 | **No copy button on code blocks** | Low | Individual code blocks don't have a copy-to-clipboard button. Only the full document. |

### Strengths
- GitHub-style sidebar with renders properly
- Generation status indicators (✓) on each file
- Copy + download in toolbar is well-positioned
- Code blocks wrapped in terminal-window pattern look polished

---

## 9. Decision Timeline

### Issues

| # | Issue | Severity | Details |
|---|---|---|---|
| T1 | **No scroll-to-top on filter change** | Medium | Switching category filters keeps scroll position, potentially showing an empty viewport. |
| T2 | **Expand animation is instant** | Low | Expand/collapse has no transition. Jumpy. |
| T3 | **No empty state icon** | Low | Empty state is just text. Could use an illustration. |
| T4 | **No "clear all filters" button** | Low | With a filter active, there's no quick way to clear it other than clicking "All". |

### Strengths
- Timeline nodes with icons and category colors are visually clear
- Expandable rationale with alternatives is the strongest feature
- Filter chips work well

---

## 10. Exports Page

### Issues

| # | Issue | Severity | Details |
|---|---|---|---|
| E1 | **No download progress indicator** | Medium | After clicking download, the button shows "Downloading..." but no progress bar. |
| E2 | **ZIP format as "coming soon" is visible but non-functional** | Low | If ZIP isn't implemented yet, consider hiding it or making it clearly a future feature. |

### Strengths
- Clean card layout with format descriptions
- Document checklist is useful for setting expectations
- File count badges help users understand what they're getting

---

## 11. Global & Design System

### Issues

| # | Issue | Severity | Details |
|---|---|---|---|
| G1 | **No focus ring on any interactive element** | **Critical** | No `:focus-visible` styles on buttons, links, inputs, sidebar items. Keyboard users cannot navigate. |
| G2 | **No keyboard shortcuts (Ctrl+K, 1-5, Escape)** | **Critical** | Power users have no way to navigate efficiently. No command palette. |
| G3 | **No reduced-motion support** | **High** | No `@media (prefers-reduced-motion)` queries. Animation-heavy background orbs continue on low-motion devices. |
| G4 | **No toast/notification system** | **High** | Actions like selecting an idea, downloading a file, or copying text have no confirmation feedback. |
| G5 | **No skeleton loaders** | **High** | All pages use a full-screen spinner instead of skeleton cards matching content shape. |
| G6 | **No page transition animation** | Medium | Navigating between `/projects/[id]/ideas` → `/projects/[id]/architecture` has no animation. Content appears instantly. |
| G7 | **Spacing is inconsistent** | Medium | Some sections use 20px padding, others 24px. Some cards use 14px, others 16px. No single spacing scale is enforced. |
| G8 | **Emoji icons across OS inconsistencies** | Low | Pipeline stage icons (🧠, 🔍, 🎯, 💡) render differently on macOS vs Windows vs Linux. |
| G9 | **No responsive breakpoints for workspace** | **High** | The workspace layout with PipelineSidebar + content assumes >1280px width. Below that, the sidebar overflows or content becomes unusably narrow. |
| G10 | **Legacy CSS tokens still in use** | Medium | Several files reference `var(--color-*)` tokens instead of the new `var(--surface-*)`, `var(--border-*)`, `var(--text-*)` tokens. |

---

## 12. Prioritized Roadmap

### Phase 1: Foundation (Critical / High) — ~10h

| Priority | Issue | Effort | Impact |
|---|---|---|---|
| 1 | **G1: Focus ring on all elements** | 1h | Accessibility baseline. Legal/UX blocker. |
| 2 | **A1: Mermaid rendering** | 2h | Architecture page is broken without diagrams. |
| 3 | **D1: Standard markdown library** | 2h | Documentation renderer is incomplete. |
| 4 | **I1: Idea comparison mode** | 2h | Most important decision needs comparison. |
| 5 | **G2: Keyboard shortcuts** | 1h | Ctrl+K palette, 1-5 for ideas. |
| 6 | **G5: Skeleton loaders** | 2h | All pages need skeleton states. |

### Phase 2: Experience (High / Medium) — ~8h

| Priority | Issue | Effort | Impact |
|---|---|---|---|
| 7 | **G3: Reduced motion** | 0.5h | Accessibility + device performance. |
| 8 | **G4: Toast notifications** | 1.5h | Action feedback for all operations. |
| 9 | **R1: Search within results** | 1h | Research is unusable with 100+ results. |
| 10 | **L5: Loading skeleton for creation** | 0.5h | First-run experience matters. |
| 11 | **N3: Skeleton on page transitions** | 1h | Professional feel during navigation. |
| 12 | **G9: Responsive workspace** | 2h | Tablets and smaller laptops. |
| 13 | **G6: Page transitions** | 0.5h | Route change animations. |

### Phase 3: Polish (Medium) — ~6h

| Priority | Issue | Effort | Impact |
|---|---|---|---|
| 14 | **I2: Keyboard shortcuts for ideas** | 0.5h | Power user feature. |
| 15 | **D2: Table of contents** | 1h | Document navigation. |
| 16 | **N2: Migrate legacy tokens** | 1h | Code health. |
| 17 | **CP2: Competition matrix visualization** | 2h | Visual gap analysis. |
| 18 | **L1: Favicon** | 0.5h | Branding. |
| 19 | **G7: Spacing audit** | 1h | Visual consistency. |

### Phase 4: Delight (Low / Nice-to-have) — ~4h

| Priority | Issue | Effort | Impact |
|---|---|---|---|
| 20 | **I6: Favorite/pin ideas** | 1h | Selection workflow. |
| 21 | **I7: Comparison table** | 1h | Decision making. |
| 22 | **D8: Code block copy buttons** | 0.5h | Developer UX. |
| 23 | **I5: Score bar entrance animation** | 0.5h | Delight. |
| 24 | **G8: SVG icons over emoji** | 1h | Cross-platform consistency. |

---

## 13. Mockups / Major Redesigns

### Mermaid Rendering (A1)

Replace the current code-block approach with a `mermaid.js` live renderer:

```
┌─ Current ─────────────────────┐    ┌─ Target ─────────────────────┐
│ ┌ term-bar ──────────────────┐│    │ ┌ term-bar ──────────────────┐│
│ │ ● ● ●  mermaid            ││    │ │ ● ● ●  diagram             ││
│ └────────────────────────────┘│    │ └────────────────────────────┘│
│ graph TD                      │    │                               │
│   A[User] --> B[Next.js]     │    │    ┌────┐    ┌────────┐       │
│   B --> C[FastAPI]           │    │    │User│───▶│Next.js │       │
│   C --> D[PostgreSQL]        │    │    └────┘    └────────┘       │
│                               │    │                  │            │
│ (Raw source code)             │    │                  ▼            │
└───────────────────────────────┘    │             ┌────────┐       │
                                     │             │PostgreSQL      │
                                     │             └────────┘       │
                                     │  (Rendered SVG, interactive) │
                                     └──────────────────────────────┘
```

### Idea Comparison Mode (I1)

Side-by-side view triggered by "Compare" button:

```
┌─ Selected Ideas ─────────────────────────────────────────────────────┐
│ [✓] Penny               [ ] SaveQuest   [ ] HabitFinance            │
│ [ ] SplitWise AI        [ ] FinLit                                  │
│                                                                      │
│ ┌── Compare 2 ─────────────────────────────────────────────────────┐ │
│ │ ┌─ Penny ───────────────────┐ ┌─ SaveQuest ──────────────────┐  │ │
│ │ │ Innovation:  85 ████████  │ │ Innovation:  72 ████████    │  │ │
│ │ │ Feasibility: 75 ████████  │ │ Feasibility: 85 ████████    │  │ │
│ │ │ Judge:       90 ████████  │ │ Judge:       78 ████████    │  │ │
│ │ │ ┌──────────────────────┐  │ │ ┌──────────────────────┐   │  │ │
│ │ │ │ Tech: Next.js,       │  │ │ │ Tech: React Native,  │   │  │ │
│ │ │ │ FastAPI, GPT-4       │  │ │ │ Firebase, Stripe     │   │  │ │
│ │ │ └──────────────────────┘  │ │ └──────────────────────┘   │  │ │
│ │ └──────────────────────────┘ └──────────────────────────┘   │ │
│ └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Skeleton Loaders (G5)

Replace spinner with content-shaped skeletons:

```
┌─ Loading Challenge Page ────────────────────────────────────────────┐
│ ┌─ Card (shimmer) ────────────────────────────────────────────────┐│
│ │ ════════════════════  (title bar, 60% width)                   ││
│ │ ════════════════════════════════  (content block 1)            ││
│ │ ══════════════  (content block 2)                              ││
│ │ ════════════════════════  (content block 3)                    ││
│ └─────────────────────────────────────────────────────────────────┘│
│ ┌─ Grid skeleton ────────────────────────────────────────────────┐│
│ │ ┌── Card ──┐ ┌── Card ──┐                                     ││
│ │ │ ════════ │ │ ════════ │  (two column shimmer blocks)         ││
│ │ │ ═══      │ │ ═══      │                                     ││
│ └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

---

## 14. Effort Summary

| Phase | Issues | Hours | Type |
|---|---|---|---|
| 1 — Foundation | 6 | 10h | Critical/High — ships product |
| 2 — Experience | 7 | 8h | High/Medium — product quality |
| 3 — Polish | 6 | 6h | Medium — consistency |
| 4 — Delight | 5 | 4h | Low/Nice — surprise |
| **Total** | **24** | **28h** | |

---

## 15. Quick Wins (<2h each)

1. **Favicon** (0.5h) — Brand asset
2. **Focus ring on all elements** (1h) — Accessibility
3. **Keyboard shortcuts** (1h) — Power users
4. **Reduced motion media query** (0.5h) — Accessibility
5. **Page transition animations** (0.5h) — Route changes
6. **Mermaid live renderer** (2h) — Architecture page
7. **Markdown renderer switch to library** (2h) — Documentation
8. **Toast notification system** (1.5h) — Feedback
9. **Skeleton loader component** (2h) — All pages

---

## 16. Recommended First Implementation

The highest-impact single change is **Mermaid rendering** (A1). Without it, the Architecture page — one of two flagship pages — shows raw source code instead of visual diagrams. This communicates "unfinished product" more than any other issue.

Second: **Markdown renderer** (D1). The custom renderer is a maintenance burden and lacks essential features (images, links, syntax highlighting). Third: **Focus ring + keyboard shortcuts** (G1, G2) for accessibility baseline.

Estimated: 5h for all three. Ready to begin when approved.
