# Configuration

[Back to the project](../README.md)

Python loads the root `.env`, then `backend/.env`. Process environment variables take precedence. Unknown variables are ignored; incorrect types for recognized settings stop startup. Keep real `.env` files out of Git.

The Next.js server uses its own process environment or `frontend/.env.local`. The root Python `.env` does **not** automatically configure Next.js. Docker Compose supplies `BACKEND_URL` to the frontend explicitly.

## AI and research

| Variable | Default | Purpose |
| --- | --- | --- |
| `AI_ACCESS_MODE` | `byok` | User RAM leases by default. `operator` explicitly uses server AI credentials. A BYOK job never falls back to them. |
| `AI_LEASE_SECONDS` | `1800` | RAM credential lifetime, 60–3600 seconds. Explicit extension starts a fresh interval; no automatic renewal. |
| `AI_MODEL` | `openai/gpt-6-luna` | Operator mode only. Provider-qualified native ID, including `groq/openai/gpt-oss-120b` for Groq. |
| `AI_API_KEY` | empty | Operator mode only; selected provider's credential. |
| `OPENAI_API_KEY` | empty | Operator OpenAI alias. |
| `ANTHROPIC_API_KEY` | empty | Operator Anthropic alias. |
| `AI_BASE_URL` | unset | Operator OpenAI Responses base URL only. Never used for BYOK; no user-supplied endpoints. |
| `TAVILY_API_KEY` | empty | Operator-managed live web search, required in both live modes. |
| `AI_TIMEOUT_SECONDS` | `120` | Per-call timeout, 10–300 seconds; BYOK also ends at lease expiry/revocation. |
| `AI_MAX_OUTPUT_TOKENS` | `12000` | Global output ceiling; each stage and catalog model may impose a lower limit. |
| `AI_INPUT_USD_PER_MILLION` | `3.0` | Operator input estimate. BYOK uses the captured catalog rate. |
| `AI_OUTPUT_USD_PER_MILLION` | `15.0` | Operator output estimate. BYOK uses the captured catalog rate. |

Use **Connect AI** in the UI to select a supported provider/model and supply a temporary key. Browser memory keeps only the opaque session reference after submission. The password field is cleared immediately. Nothing from the credential form enters the local intake draft. See [BYOK](BYOK.md) for lease limits, endpoints, model limitations, and restart recovery.

Request-scoped HTTPX adapters use fixed HTTPS provider endpoints and no shared authenticated-client cache. No native search tools or hosted conversation IDs are used. OpenAI/xAI Responses requests set `store: false`. JSON is validated by Pydantic with one repair attempt; protocol support does not establish model quality. Catalog models and conservative rates live in `backend/app/studio/providers.py`, reviewed against provider documentation on 2026-10-31. Review that snapshot when prices/models change; Gemini's current introductory price ends 2026-12-31.

## Workflow limits

| Variable | Default | Meaning |
| --- | --- | --- |
| `STUDIO_DEMO_MODE` | `false` | Explicit deterministic offline fixtures; prohibited with `ENV=production`. |
| `STUDIO_WORKER_ENABLED` | `true` | Start the embedded background worker. With `false`, accepted jobs remain queued. |
| `STUDIO_JOB_LEASE_SECONDS` | `300` | Worker claim lifetime; heartbeat renews it. Range 15–3600. |
| `STUDIO_IDEA_ROUNDS` | `2` | Research/critique cycles; 1–3. |
| `STUDIO_CONTEXT_CHAR_LIMIT` | `180000` | Full input character guard. Not a tokenizer or a guarantee of provider context compatibility. |
| `STUDIO_COST_LIMIT` | `5.0` | Per-project AI reservation/accounting ceiling using your configured rates. |
| `STUDIO_SEARCH_LIMIT` | `100` | Per-project query count, including attempted queries. Not a Tavily dollar limit. |
| `FREE_TIER_PROJECTS_PER_DAY` | `3` | Maximum currently retained projects created in the last 24 hours per workspace key. Deleting projects frees quota; this is not an abuse-resistant billing limit. |
| `MAX_PROJECTS_PER_USER` | `50` | Maximum retained projects per workspace key; no registered account is implied. |

Conservative cost is reserved before every attempt, then reconciled when token usage is returned. A failed or interrupted call can retain its reservation because the provider may have billed it. Reservations and operation retries do not guarantee exactly-once provider billing. Providers can price cached input, reasoning, or other features differently; these two rates are an estimate, not an invoice. Configure upstream spending limits too.

Research searches up to six queries concurrently per batch, keeps up to four results per query, filters unusable URLs, deduplicates sources, and caches a successful matching batch for 24 hours within the project. Partial failures are disclosed; total failure produces an error. An empty search is never replaced with fictional sources.

## Runtime

| Variable | Default | Meaning |
| --- | --- | --- |
| `ENV` | `development` | `development`, `staging`, or `production`. Production requires Tavily, plus AI credentials in operator mode, and explicit migrations. Development/staging apply Alembic migrations automatically. |
| `EXHACKER_DEBUG` | `false` | Parsed debug setting; no public exception-detail mode is enabled. Generic system `DEBUG` variables are ignored. |
| `LOG_LEVEL` | `INFO` | Python root logger level. Avoid debug logging in shared deployments. |
| `DATABASE_URL` | `sqlite+aiosqlite:///./exhacker.db` | Async SQLite or PostgreSQL connection. Relative SQLite paths are relative to the backend process's working directory. |
| `CORS_ORIGINS` | localhost ports 3000 | JSON array of allowed browser origins for direct API access. The normal same-origin proxy does not require browser-to-backend CORS. |
| `BACKEND_URL` | `http://127.0.0.1:8000` | **Frontend server only.** Backend origin, without `/api/v1`. Compose uses `http://backend:8000`. |
| `NEXT_PUBLIC_API_URL` | `/api/v1` | Optional build-time browser API base. Usually leave unset. Never put secrets here. |

`postgres://` and `postgresql://` are normalized to `postgresql+asyncpg://`. SQLite URLs are normalized similarly. For PostgreSQL TLS, supply an asyncpg-compatible connection configuration supported by the host; test it against the actual database. Do not assume a libpq-only `sslmode` URL works unchanged with asyncpg.

## Verification only

`compose.verify.yml` intentionally reads no real `.env` file. It supplies offline mode, a 15-second lease, a local PostgreSQL password, and an isolated verification database. Its defaults bind only to loopback:

| Variable | Default | Meaning |
| --- | --- | --- |
| `VERIFY_FRONTEND_PORT` | `3200` | Host port for the standalone frontend. |
| `VERIFY_BACKEND_PORT` | `8200` | Host port for the verification API. |
| `PLAYWRIGHT_BASE_URL` | unset | Test an already-running site instead of starting local servers. Use only a disposable demo installation. |
| `PLAYWRIGHT_BYOK` | unset | `true` runs BYOK browser journeys against a development-only synthetic provider server. Never a production fallback. |
| `CAPTURE_README` | unset | `true` saves actual desktop screenshots to `docs/images/`. |
| `TEST_DATABASE_URL` | unset | Dedicated PostgreSQL URL ending in `_verification`; fixtures create and drop a unique schema per test. Otherwise tests use temporary SQLite databases. |

Do not use the verification credentials or Compose stack for public hosting.
