# exHacker — Complete User Journey Audit

> **Date:** 2026-07-07  
> **Persona:** First-time hackathon participant — technical, competitive, impatient. Has 36 hours to build something great. Found exHacker through a Google search or hackathon Discord. Knows nothing about the product.

---

## Step 0: Landing Page — First 30 Seconds

### What the user sees

Landing page loads with animated background orbs, a bold headline (BUILD YOUR HACKATHON IN MINUTES.), stats (7 specialists, 5 ideas, 10 docs), an input field, and a pipeline grid below.

### Pain points

| # | Pain Point | Severity |
|---|---|---|
| 1 | **The hero is impressive but tells the user nothing concrete.** "BUILD YOUR HACKATHON IN MINUTES" is aspirational but a first-time user has no mental model of what "your hackathon" means. Is this a no-code builder? A project generator? A strategy tool? | **High** |
| 2 | **Stats are abstract without context.** "7 Specialists" means nothing until you scroll down. The pipeline grid explains it but it's below the fold. First 30 seconds should answer: *What does this actually do?* | **High** |
| 3 | **No social proof.** No logos of hackathons where this has been used. No testimonials. No GitHub stars count. For a competitive user deciding between tools, this is a red flag. | **Medium** |
| 4 | **The animation stops.** The terminal types out lines progressively and then stops at the last line with a blinking cursor. A static final state after an animated start feels like it broke. | Low |
| 5 | **No "try a demo" button.** Users can't explore without committing their own idea. A "Watch Demo" or "Try Sample" would build trust before input. | Medium |

### Suggested improvements

| Fix | Effort | Impact |
|---|---|---|
| Add a sub-headline: *"Paste any hackathon challenge → Get a complete strategy, architecture, docs, and pitch — built by 7 AI specialists working together."* | 10m | High |
| Add hackathon logos or "Built for X" badges (Devpost, HackMIT, etc.) | 2h | Medium |
| Add a "Try Demo" button that pre-fills the input with a sample challenge | 1h | Medium |
| Loop the terminal animation or show a live "recent projects" ticker | 1h | Low |
| Move one pipeline card (e.g. Challenge Analyst) into the hero area | 1h | Medium |

---

## Step 1: Creating a Project — ~10 seconds

### What the user does

Types into the input field (or clicks an Example button), clicks "Start Free". The button changes to "Starting..." then redirects to the workspace.

### Pain points

| # | Pain Point | Severity |
|---|---|---|
| 6 | **No feedback during creation.** The button shows "Starting..." but no animation. On slow connections, the user might click again or wonder if it worked. | **High** |
| 7 | **Example buttons are hard to discover.** They're tiny (10px text), below the input, and look like secondary pills. A first-time user might miss them entirely. | Medium |
| 8 | **No field for challenge details.** The creation form takes only one `idea` field. The user might have a challenge statement, theme, track, time constraints — no way to provide them here. | **High** |
| 9 | **No success message before redirect.** The transition is instant — landing page → workspace. No "Project created!" confirmation. The user might not be sure it worked. | Medium |
| 10 | **URL changes without explanation.** The user goes from `/` to `/projects/[uuid]/overview`. If they notice the URL, they see a UUID — not a friendly name. | Low |

### Suggested improvements

| Fix | Effort | Impact |
|---|---|---|
| Add a brief loading overlay: "Creating your project..." with a progress bar | 1h | High |
| Increase example button size and add hover effect | 0.5h | Medium |
| Add expandable "More details" section to the creation form (challenge, theme, team size) | 2h | High |
| Show a toast "Project created!" after successful creation | 1h | Medium |
| Use project name/slug in URL instead of UUID  | 1h | Low |

---

## Step 2: Arriving at the Workspace — First 15 seconds

### What the user sees

A 2-column layout: PipelineSidebar (left, 280px) + WorkspaceContent (right). The sidebar shows 8 pipeline stages all "Queued". The overview shows project name, idea snippet, status badge, and 3 stat cards.

### Pain points

| # | Pain Point | Severity |
|---|---|---|
| 11 | **No "What now?" guidance.** The user has no idea what to click first. The pipeline shows "Queued" stages but none are actionable from the sidebar. | **Critical** |
| 12 | **Overview is too sparse.** Three stat cards (Status, Created, Specialists) don't communicate progress or what's possible. | **High** |
| 13 | **9 workspace tabs are overwhelming.** A first-time user sees 9 navigation items. Without knowing what each does, this is decision paralysis. | **High** |
| 14 | **Pipeline sidebar has no "start" action.** The sidebar is visual-only. Clicking a stage doesn't start it. The user has to navigate to the tab first. | Medium |
| 15 | **Back button confusion.** If user hits browser Back, they leave the project entirely (back to landing page). No warning about unsaved work. | Medium |

### Suggested improvements

| Fix | Effort | Impact |
|---|---|---|
| Add a "Quick Start" card on the overview: *"Start with Challenge Intelligence →"* | 2h | Critical |
| Add a tooltip/guide on first visit: *"Click Challenge to begin analyzing your brief"* | 2h | High |
| Group workspace tabs into phases: Analysis (Challenge, Research, Competitors) → Ideas (Ideas) → Build (Architecture, Docs, Timeline) → Export | 1h | High |
| Make pipeline sidebar items clickable to navigate to the corresponding tab | 1h | Medium |
| Add breadcrumb: Home → Projects → Project Name | 0.5h | Medium |

---

## Step 3: Challenge Intelligence — ~20 seconds

### What the user does

Clicks "Challenge" in the nav. Sees an empty state with "Analyze Challenge" button. Clicks it. Loading spinner appears. After ~5-15 seconds, the analysis appears: executive summary, core problem, difficulty, stakeholders, constraints, success criteria, opportunities, risks, and a recommended strategy.

### Pain points

| # | Pain Point | Severity |
|---|---|---|
| 16 | **Loading has no context.** The spinner says "Analyzing challenge..." but doesn't explain what's happening. The user might think it's stuck. | **High** |
| 17 | **Too much information at once.** The challenge page has 10+ sections. A first-time user seeing all of it at once might feel overwhelmed, not informed. | **High** |
| 18 | **No "generate" feedback.** After clicking the button, there's no indication of *what* is being generated or *how long* it will take. | Medium |
| 19 | **Sections are ordered by completeness, not importance.** Hidden Problems and Stakeholders appear before Opportunities and Strategy. The most important content (Strategy) is at the bottom. | Medium |
| 20 | **Success criteria weight bars could be misinterpreted.** `ScoreBar` shows a value out of 100, but without a legend, the user might not understand the scale. | Low |

### Suggested improvements

| Fix | Effort | Impact |
|---|---|---|
| Show a streaming/progress indicator during generation: "Analyzing constraints..." → "Identifying stakeholders..." → "Evaluating success criteria..." | 2h | High |
| Add a collapsible accordion pattern so sections can be expanded on demand | 1h | High |
| Reorder sections: Executive Summary → Strategy → Core Problem → Success Criteria → Everything else | 0.5h | Medium |
| Add "Analysis generated from 3 specialist outputs" subtitle | 0.2h | Low |

---

## Step 4: Research — ~30 seconds

### What the user does

Clicks "Research" tab. Research auto-starts (no user action). Loading spinner appears. Results appear with synthesis, category filters, results cards, technology recommendations, and risks.

### Pain points

| # | Pain Point | Severity |
|---|---|---|
| 21 | **Research auto-starts without asking.** The user might not be ready for research yet. They might want to modify the challenge first or skip research entirely. | **High** |
| 22 | **No per-category streaming.** The page loads all categories at once. The user doesn't know how many results each category has until everything finishes. | Medium |
| 23 | **Category filters scroll horizontally.** The filter bar can overflow on smaller screens with no scroll indicator. | Medium |
| 24 | **Category sections are long.** A category like "Existing Products" might have 20+ cards stacked vertically. No pagination or "show more/less". | Medium |
| 25 | **No export for research.** If the user finds valuable competitor intel, they can't save or export it separately. | Low |

### Suggested improvements

| Fix | Effort | Impact |
|---|---|---|
| Run research on demand (button) instead of auto-start, with a "pre-filled from challenge" note | 2h | High |
| Show per-category progress during loading: "Found 12 products, 8 APIs..." | 1h | Medium |
| Limit card display to 5 per category with "Show all N results" toggle | 1h | Medium |
| Add "Copy research summary" button | 0.5h | Low |

---

## Step 5: Competitors — ~20 seconds

### What the user does

Clicks "Competitors" tab. Auto-loads competitor analysis. Shows competitor profiles, gap analysis grid, quick wins, innovation breakdown, and warnings.

### Pain points

| # | Pain Point | Severity |
|---|---|---|
| 26 | **No trigger action.** Like research, this auto-runs. User might not understand what triggered it. | Medium |
| 27 | **Competitor profiles are dense.** Each card has target users, business model, strengths, weaknesses, missing features, and tech stack. In a list of 6+ competitors, this is a lot of text. | **High** |
| 28 | **Gap analysis is just text.** Patterns, white space, pain points, and "avoid" are text lists. No visual map or heatmap. | Medium |
| 29 | **Innovation breakdown uses ScoreRows.** 10+ rows in a 2-column grid is information-dense. A radar chart would be faster to scan. | Medium |

### Suggested improvements

| Fix | Effort | Impact |
|---|---|---|
| Limit competitor profile to 3 visible lines with expand/collapse | 1h | High |
| Replace innovation ScoreRows with a radar/spider chart component | 3h | Medium |
| Add a "Key Takeaways" box at the top summarizing the most important findings | 0.5h | Medium |
| Color-code competitor market maturity (early, growing, mature, declining) | 0.5h | Low |

---

## Step 6: Ideas — The Most Important Decision (~60 seconds)

### What the user does

Clicks "Ideas" tab. 5 idea cards appear with score bars, feature tags, and expandable details. User scrolls through cards. Optionally clicks "Compare Ideas" to open comparison table. Clicks "Select This Direction" on the chosen idea.

### Pain points

| # | Pain Point | Severity |
|---|---|---|
| 30 | **No "Generate Ideas" button in empty state.** If ideas haven't been generated, the empty state says "Run the Idea Generator..." but has no actionable button. | **Critical** |
| 31 | **Expanding a card is not obvious.** Cards have a subtle cursor:pointer but no visual indicator that they're expandable. A first-time user might not try clicking. | **High** |
| 32 | **No confirmation after selection.** After clicking "Select This Direction", the card shows "Selected" but there's no toast, animation, or congratulations. The user might not be sure it registered. | **High** |
| 33 | **Cards are too long.** With all 7 score bars, elevator pitch, and feature tags, each card is ~200px visible before expanding. Scrolling through 5 of them is tiring. | Medium |
| 34 | **Comparison mode is hidden.** The "Compare Ideas" button is small text below the page title. A user in a hurry might miss it entirely. | Medium |
| 35 | **No keyboard shortcuts.** User can't press 1-5 to select. Can't press Enter to confirm. Can't press Escape to close expandable. | Medium |
| 36 | **No score explanation.** The overall score is a number (e.g. 85) with color coding, but no explanation of *how* it's calculated or *what it means*. | Low |

### Suggested improvements

| Fix | Effort | Impact |
|---|---|---|
| Add "Generate Ideas" button to empty state that triggers generation with loading feedback | 0.5h | Critical |
| Add a subtle "▼ Click to expand" label on collapsed cards | 0.2h | High |
| Show a toast/celebration when an idea is selected | 1h | High |
| Show only 3-4 most important score bars by default, with "Show all 10 scores" toggle | 1h | Medium |
| Make "Compare" a prominent button with visible badge count | 0.5h | Medium |
| Add keyboard shortcut hints (1-5) on card headers | 0.5h | Medium |

---

## Step 7: Architecture — ~30 seconds

### What the user does

Clicks "Architecture" tab. System overview appears, component cards, rendered Mermaid diagrams, database entities, API contracts, trade-offs, architecture review, and scalability info.

### Pain points

| # | Pain Point | Severity |
|---|---|---|
| 37 | **Architecture might not exist yet.** If the user navigates here before generating architecture, they see a loading state that never resolves. | **High** |
| 38 | **Mermaid diagrams don't fit the viewport.** Complex diagrams overflow the content area. No zoom, pan, or fullscreen. | **High** |
| 39 | **Database entities are hard to scan.** Fields are listed monospace with PK/UNIQUE indicators but no visual grouping or relationship lines. | Medium |
| 40 | **API contracts lack examples.** Method + path is shown but no request/response body examples, no curl commands, no error codes. | Medium |
| 41 | **Trade-off cards are dense.** Decision, rationale, alternatives, pros, and cons all in one card. Can be overwhelming with 5+ trade-offs. | Medium |

### Suggested improvements

| Fix | Effort | Impact |
|---|---|---|
| Add a "Generate Architecture" button with clear loading state | 0.5h | High |
| Add zoom/pan controls to Mermaid diagrams (fullscreen modal) | 3h | High |
| Add field type badges (string, int, boolean) with color coding to database view | 1h | Medium |
| Add curl examples to API contracts | 2h | Medium |
| Make trade-off cards collapsible with expand/collapse toggle | 1h | Medium |

---

## Step 8: Documentation — ~30 seconds

### What the user does

Clicks "Docs" tab. Sidebar with 10 files loads. Active file renders in main panel. User clicks between files to browse documentation.

### Pain points

| # | Pain Point | Severity |
|---|---|---|
| 42 | **No "Generate Documentation" button.** If docs don't exist, the sidebar shows all files as unavailable. No way to trigger generation from this page. | **Critical** |
| 43 | **Sidebar doesn't show file sizes or word counts.** The user can't estimate how long each doc is before reading. | Medium |
| 44 | **No progress indicator for generation.** If docs are being generated, there's no per-file progress. | Medium |
| 45 | **Table of contents not auto-generated.** Long documents require scrolling to find sections. | Medium |
| 46 | **No "Download All" in the toolbar.** Download is only on the Exports page. User has to navigate away to download everything. | Medium |

### Suggested improvements

| Fix | Effort | Impact |
|---|---|---|
| Add "Generate All Documentation" button at the top of the sidebar | 0.5h | Critical |
| Show file size (KB) in the sidebar next to each file name | 0.2h | Medium |
| Show generation progress as files are completed (streaming approach) | 2h | Medium |
| Auto-generate a table of contents from headings and make it sticky | 2h | Medium |
| Add "Download All" to the documentation toolbar | 0.5h | Medium |

---

## Step 9: Timeline — ~15 seconds

### What the user does

Clicks "Timeline" tab. Sees decision journal entries in chronological order with filter chips.

### Pain points

| # | Pain Point | Severity |
|---|---|---|
| 47 | **Empty timeline is unhelpful.** "No decisions recorded yet. Decisions appear automatically as specialists complete their work." — but the user doesn't know which specialists have run. | Medium |
| 48 | **Entries require clicking to expand.** No summary-level data visible. User has to click every entry to see details. | Medium |
| 49 | **No search within timeline.** With 20+ decisions, filtering by text is not possible. | Low |

### Suggested improvements

| Fix | Effort | Impact |
|---|---|---|
| Show which specialists have completed vs pending in the empty state | 0.5h | Medium |
| Show first 2 lines of each entry without requiring expand | 0.2h | Medium |
| Add text search input for filtering entries | 0.5h | Low |

---

## Step 10: Exports — ~15 seconds

### What the user does

Clicks "Exports" tab. Sees format cards: Markdown, JSON, ZIP (coming soon). Clicks "Download Markdown" — triggers API download.

### Pain points

| # | Pain Point | Severity |
|---|---|---|
| 50 | **No download preview.** User has no idea what the file contains before downloading. | Medium |
| 51 | **Download progress is invisible.** Button says "Downloading..." but no percentage or bytes indicator. | Medium |
| 52 | **ZIP coming soon is visible but useless.** The card takes up space but doesn't work. Consider hiding it or making it a disabled card with a clear "notify me" option. | Low |
| 53 | **No "Download All" as single command.** User has to download Markdown and JSON separately. | Medium |

### Suggested improvements

| Fix | Effort | Impact |
|---|---|---|
| Add file size estimate for each format before download | 0.5h | Medium |
| Show download progress with a thin progress bar | 1h | Medium |
| Replace "Coming Soon" with either working ZIP or a hidden card | 0.2h | Low |
| Add "Download All" option that packages everything | 1h | Medium |

---

## Global Issues (Across All Steps)

### Missing foundational UX infrastructure

| # | Pain Point | Severity | Effort |
|---|---|---|---|
| G1 | **No toast/notification system.** Any action (create, select, download, error) has zero feedback. User never knows if their action succeeded. | **Critical** | 2h |
| G2 | **No command palette (Ctrl+K).** Power users can't navigate efficiently. 9 tabs × 5 actions = 45 potential commands with no shortcut. | **High** | 3h |
| G3 | **No keyboard shortcuts.** Ideas 1-5, Enter, Escape, Ctrl+S, Ctrl+E — none exist. | **High** | 1h |
| G4 | **No skeleton loaders.** Every page uses a spinner. User can't anticipate page structure before content loads. | **High** | 2h |
| G5 | **No page transitions.** Navigating between tabs is instant — no animation, no perceived performance improvement. | Medium | 1h |
| G6 | **No breadcrumb navigation.** User can't tell where they are: Home → Projects → [Name] → Ideas. | Medium | 0.5h |
| G7 | **Pipeline sidebar doesn't update dynamically.** Stages stay "queued" even when content exists. No sync between completed work and pipeline status. | **High** | 2h |

### Information architecture issues

| # | Pain Point | Severity | Effort |
|---|---|---|---|
| G8 | **9 tabs with no grouping.** A new user sees 9 seemingly equal options. No visual priority. | **High** | 1h |
| G9 | **Sections ordered inconsistently.** Some pages put the most important content at the top (Challenge: Executive Summary). Others bury it (Architecture: System overview is correct). Review all pages. | Medium | 0.5h |
| G10 | **No progress indicator for the project overall.** No "3 of 8 stages complete" anywhere visible. | **High** | 1h |

---

## The 5 Most Critical Fixes (Ranked by User Impact)

| Rank | Issue | Current State | Fix | Effort |
|---|---|---|---|---|
| 1 | **No "Generate Ideas" button in empty state** | User sees empty state with no action | Add button that triggers generation with progress | 0.5h |
| 2 | **No "Generate Documentation" button** | Sidebar shows unavailable files with no trigger | Add generate button at top of sidebar | 0.5h |
| 3 | **No toast/notification system** | All actions have zero feedback | Add toast provider + hook | 2h |
| 4 | **No skeleton loaders** | All pages use spinner | Add Skeleton component + wire into pages | 2h |
| 5 | **No "What now?" guidance on first visit** | Overview is 3 stat cards with no next step | Add Quick Start card with guided path | 2h |

**Total for 5 most critical:** 7 hours

---

## The "Effortless" Metric

The user journey currently has **53 identified pauses** — moments where a user would hesitate, wonder, or feel uncertain.

Target: Reduce pauses to fewer than **10** for the core path (Create → Challenge → Ideas → Architecture → Export).

The 5 fixes above would eliminate **~20 pauses** immediately by providing clear actions, feedback, and guidance at every decision point.
