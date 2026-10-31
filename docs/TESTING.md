# Testing and verification

[Back to the project](../README.md)

Tests use disposable projects/databases and explicit offline fixtures. They never need paid API credentials. Provider adapters and research boundaries have controlled responses; these do not establish real-model quality. Container and browser tests exercise the actual API, database, worker, proxy, UI, and exports.

## Live testing with your API keys

Use the normal app to evaluate real providers. The automated suites below deliberately use synthetic credentials/responses, even when you have real keys configured locally.

### Configure local access

The normal Docker stack requires a repository-root `.env`. Copy the tracked template only if a private file does not already exist:

```powershell
# Repository root, PowerShell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

On macOS/Linux, copy `.env.example` to `.env` if it does not already exist. Python can alternatively read process environment variables. The separate offline verification stack requires no `.env` or paid keys.

Edit the root `.env` locally:

```dotenv
ENV=development
AI_ACCESS_MODE=byok
STUDIO_DEMO_MODE=false
TAVILY_API_KEY=replace-with-your-own-tavily-key
```

Tavily is operator-managed, so its key belongs in the private backend environment. Leave `AI_API_KEY` blank for BYOK. `AI_MODEL`, `AI_API_KEY` and provider aliases are optional operator-mode settings; they do not choose the model for a BYOK session. Enter your own OpenAI, Anthropic, Gemini, xAI or Groq API key through **Connect AI** in the browser. One provider key is sufficient to test a complete journey.

Keep `.env` out of Git. Do not paste keys into chat, issue reports, project briefs, screenshots or test fixtures. No frontend environment file is needed with the default same-origin proxy.

For a local test campaign creating more than three projects, optionally set `FREE_TIER_PROJECTS_PER_DAY=50` in `.env`. Keep a deliberate `STUDIO_COST_LIMIT` and check spending controls in your provider accounts: the app's conservative estimates are not a hard provider billing cap. AI and Tavily can each charge for the workflow's multiple calls, including repeated work after interruptions.

### Start the real app

```powershell
# Repository root
docker compose config --quiet
docker compose up --build --wait
```

Open **http://localhost:3000**. Choose **Connect AI**, select the provider/model, enter that provider's key and choose **Start AI session**. A session is checked by the provider on its first generation request. The key field clears after submission.

The separate app on **http://localhost:3200** is the offline verification stack. It will continue using fixtures regardless of the credentials in your local `.env`. A live run must have no demonstration-mode banner.

If you later change `.env`, run `docker compose up -d --wait` to apply the updated service environment. Stop the local app with `docker compose down`; leave off `-v` to keep your projects. Use one backend process with its embedded worker.

### Exercise the complete journey

Start with a concrete challenge, a 24- or 48-hour deadline, two teammates with different skills, and a judging rubric. For example: help rural students find mentors despite unreliable internet, with one React builder and one Python builder.

| Action | Verify |
| --- | --- |
| Research and generate ideas | Five distinct directions, eight score dimensions with rationales, useful critiques, and relevant competitor/source links that actually open. |
| Refine one idea with your prompt | The result preserves your requested direction and constraints, explains changes, and updates scoring. |
| Confirm a direction and review its stack | The proposed components fit the selected idea, team skills and available time. |
| Substitute a technology, such as PostgreSQL with Convex | The reviewed choices, components and data flow respect your substitution and disclose compatibility assumptions. |
| Confirm the stack and generate documentation | All ten Markdown files preview, copy and download. PRD, AGENTS, contracts and named tasks agree with the confirmed idea and stack. |
| Ask the assistant about task allocation and risks | Answers use the actual teammates, approved stack, deadline, research and documents. Reloading preserves the conversation. |
| Download the package and use it | A person or coding agent can follow PRD/AGENTS to build a small version without contradictory or missing instructions. |

Review output quality manually; successful JSON validation alone does not make an idea original or a specification useful. Check the provider and Tavily dashboards for real usage, latency, quota failures and charges. Begin with one complete journey, then repeat for every provider/model you intend to advertise, including briefs with tighter time budgets and beginner skill levels.

### Diagnose a failed generation

Tavily and the AI provider are separate services. Search usage confirms research ran; an initial AI call can succeed and a later critique fail when it includes candidates and research. The saved job events identify the failing stage.

Provider rejection errors include a numeric HTTP status without exposing raw provider messages or credentials. HTTP 413 means the request is too large; account token/request limits can be smaller than a model's advertised context window. Groq's free-plan allowance may not fit full research, document or chat context. Use account limits sufficient for the workflow or select another provider; retrying an unchanged oversized request does not increase its allowance. HTTP 429 indicates a cooldown/rate limit; the app respects short numeric Retry-After values and leaves longer waits for an explicit retry.

New idea jobs save candidates and completed research before critique. A retry of unchanged inputs within 24 hours reuses saved progress, including when the selected provider changes. Completed rounds also survive recovery. Older failed jobs created before these checkpoints were implemented may still need candidate regeneration and new searches if the cached queries do not match. An interrupted external call can still repeat and incur charges.

### Verify key lifecycle and recovery

| Check | Expected behavior |
| --- | --- |
| Switch providers between completed operations | Future operations use the newly selected session. Previous documents and history stay available. |
| Extend an older session | The current selected session stays selected. |
| Reload the browser | Saved work persists; reconnect a key for new operations because this tab's session references were in memory. |
| Remove a session during generation | Affected AI calls stop and the job pauses for credentials. Reconnect the original provider/model and resume, or cancel the paused job. |
| Restart the live backend with `docker compose restart backend` | RAM credentials are lost. Queued/recovered BYOK jobs request matching credentials again; saved artifacts remain readable. |
| Enter an invalid provider key | The first generation attempt fails safely or requests new credentials. No fabricated success, operator-key fallback or raw key should appear in the error. |

The default lease is 30 minutes and can be explicitly extended. To test short expiry, set `AI_LEASE_SECONDS=60` in your local `.env`, recreate the backend, then create a new session. Restore the usual duration afterward. Interrupted or resumed provider work may still incur charges; the automated recovery scripts below test the same application paths without paid calls.

## Backend

```sh
cd backend
uv sync --frozen --extra dev
uv run ruff check app tests migrations
uv run ruff format --check app tests migrations
uv run pytest -q
```

By default every test uses its own temporary SQLite database. No fixture drops or rewrites the configured application database. The migration test creates its own prototype row and proves it survives migration; schema comparison verifies the new tables match the models.

The PostgreSQL mode requires an explicit `TEST_DATABASE_URL` using `postgresql+asyncpg` and a database name ending in `_verification`. Every test gets a unique temporary schema; teardown drops only that schema. The verification Compose service configures this safely:

```sh
# Run from the repository root after starting the verification stack.
docker compose -p exhacker-verify -f compose.verify.yml run --rm --build backend-tests
```

The suite covers ownership, workflow gates, exact selected idea, refinement/invalidation, stack substitutions, reproducible Markdown exports, chat ordering/context, provider/schema failures, cost reservation races, live-search HTTP protocol and cache behavior, leases, superseded attempts, approval rollback, invalid team constraints, and both declared/chunked request-size limits.

## Frontend and browser

```sh
cd frontend
npm ci
npm run lint
npm run typecheck
npm run format:check
npm run build
npx playwright install chromium
npm test
```

`npm test` starts a real Uvicorn API on 8101 with a temporary SQLite database and builds/starts Next.js on 3100. Existing servers on these ports are not reused. Keep these ports free. Chromium tests cover the whole intake → five ideas → refinement → stack edit → docs/ZIP → saved chat journey, mobile overflow, workspace recovery/ownership/deletion, proxy size limits, visible service failure, and untrusted Markdown/Mermaid handling.

The Markdown trust-boundary test replaces one artifact response with deliberate malicious content; it does not replace the renderer or the preceding real project workflow. The service-outage test deliberately supplies a 503 response. These controlled tests are identified as such and do not masquerade as live inference.

### BYOK browser journeys

Run this separately from the demo suite, against the local disposable servers:

```sh
PLAYWRIGHT_BYOK=true npm test
```

```powershell
$env:PLAYWRIGHT_BYOK = 'true'
npm test
Remove-Item Env:PLAYWRIGHT_BYOK
```

This starts `tests.byok_server:app`, a development-only test module that replaces external provider/Tavily HTTP responses with fixtures. The real API, credential registry, background worker, adapters, database, proxy and UI execute normally. No production test switch or paid key is used. Tests inspect browser storage, key-field clearing, provider switching, renewal without changing the selected session, preserved documents and matching-session recovery.

### Test the real container frontend

First start the stack from the repository root:

```sh
docker compose -p exhacker-verify -f compose.verify.yml up --build --wait
```

Then run from `frontend`:

```sh
# macOS / Linux
PLAYWRIGHT_BASE_URL=http://127.0.0.1:3200 npm test
```

```powershell
# PowerShell
$env:PLAYWRIGHT_BASE_URL = 'http://127.0.0.1:3200'
npm test
Remove-Item Env:PLAYWRIGHT_BASE_URL
```

This uses the standalone frontend image, real proxy, containerized API, embedded worker, and PostgreSQL. Run browser suites sequentially: they share the `frontend/test-results` output directory. Never point tests at a valuable live installation.

## Runtime outage and recovery

```sh
python scripts/verify_docker.py --restart
```

The script requires the isolated `exhacker-verify` project in explicit demo mode. It creates real projects, validates ownership and stale writes, compares all ten downloaded Markdown files with their ZIP entries, checks two saved chat turns, stops the API and verifies proxy failure, starts a temporary worker-disabled API to accept a queued job, kills that process, and restarts the normal worker to recover the saved queue. Existing documents and chat must remain unchanged. This tests queued acceptance/recovery after process death; the backend suite separately tests expired running leases and stale-attempt publication.

The BYOK-specific process-death check is:

```sh
python scripts/verify_byok_restart.py
```

It only targets the default loopback ports and the `exhacker-verify` project. It queues a job with a synthetic key in a worker-disabled API, kills that process, and checks that an empty-registry worker pauses it before any external call. Matching reentry/resubmission is tested with the worker disabled and cancelled before inference. Prior saved artifacts must remain unchanged. These checks verify recovery behavior with synthetic credentials; they do not establish paid-provider access or model quality.

Only this verification API/container is deliberately interrupted. Do not run recovery and browser tests simultaneously. The script uses Python's standard library and requires the Docker CLI on PATH.

Stop without deleting data with `docker compose -p exhacker-verify -f compose.verify.yml down`. To intentionally remove **only the disposable verification database**, add `-v` with that same project/file. Do not use `-v` against a development or production project with valuable data.

## Screenshots and audits

Set `CAPTURE_README=true` alongside the external base URL when running the browser suite. The demo suite writes actual screenshots to `docs/images/hero.png` and `docs/images/workspace.png`. Running the BYOK suite with the same flag captures `docs/images/ai-session.png` before a key is entered. Review them visually before committing. The displayed workspace must keep its offline-mode notice; screenshots are not live-provider evaluation evidence.

`npm audit` checks the frontend dependency tree against current advisories. A clean result is time-specific. Python dependency audits can run with `uvx pip-audit`; use an isolated tool environment and inspect results rather than adding audit tools to runtime dependencies. Container OS advisories and hosted infrastructure require their own release review.

## CI

The workflow in `.github/workflows/ci.yml` blocks on backend lint/tests, frontend lint/types/build, both local demo/BYOK browser workflows, and a container job. The container job builds the real images, migrates PostgreSQL, runs the backend suite there, checks general and BYOK credential-loss recovery, and runs Chromium against the standalone frontend. Failure logs/traces are uploaded. No paid keys are supplied to pull requests.

Before shipping, evaluate real supported models with representative briefs, measure latency/spend, exercise actual provider failures and deployment restarts, test database backup restoration, and run representative load/concurrency checks. Do not replace these with offline fixture pass counts.
