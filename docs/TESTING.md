# Testing and verification

[Back to the project](../README.md)

Tests use disposable projects/databases and explicit offline fixtures. They never need paid API credentials. Provider adapters and research boundaries have controlled responses; these do not establish real-model quality. Container and browser tests exercise the actual API, database, worker, proxy, UI, and exports.

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
