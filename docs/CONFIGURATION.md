# Configuration

[Back to the project](../README.md)

Python loads the root `.env`, then `backend/.env`. Process environment variables take precedence. Unknown variables are ignored; incorrect types for recognized settings stop startup. Keep real `.env` files out of Git.

The Next.js server uses its own process environment or `frontend/.env.local`. The root Python `.env` does **not** automatically configure Next.js. Docker Compose supplies `BACKEND_URL` to the frontend explicitly.

## AI and research

| Variable | Default | Purpose |
| --- | --- | --- |
| `AI_MODEL` | `openai/gpt-4o-mini` | LiteLLM provider-qualified text model. Model access, context, output limits, and quality must be evaluated with your account. |
| `AI_API_KEY` | empty | Operator's key for the selected provider; takes priority over aliases. |
| `OPENAI_API_KEY` | empty | Alternative for an OpenAI or unprefixed OpenAI model. |
| `ANTHROPIC_API_KEY` | empty | Alternative when `AI_MODEL` starts with `anthropic/`. |
| `AI_BASE_URL` | unset | Administrator-controlled compatible endpoint. Never expose this as an unrestricted user input. |
| `TAVILY_API_KEY` | empty | Separate live web-search credential; an AI key does not replace it. |
| `AI_TIMEOUT_SECONDS` | `120` | Per-provider-call timeout, between 10 and 300 seconds. |
| `AI_MAX_OUTPUT_TOKENS` | `12000` | Global ceiling. Each stage also requests its own limit. Must fit the chosen model. |
| `AI_INPUT_USD_PER_MILLION` | `3.0` | Configured input pricing, **not a live price quote**. |
| `AI_OUTPUT_USD_PER_MILLION` | `15.0` | Configured output pricing, **not a live price quote**. |
| `LITELLM_LOCAL_MODEL_COST_MAP` | `true` | Uses LiteLLM's bundled public model metadata rather than fetching that map at import. Forwarded from Python settings before the first LiteLLM import, including native `.env` launches. This does not turn inference offline. |

Only operator-managed credentials exist today. The [BYOK assessment](BYOK.md) describes a proposed design awaiting approval. There is no user key form or session credential service yet.

The adapter passes a key directly to each LiteLLM call. No native web-search tools, model-side agents, or provider-hosted conversation IDs are required by the current workflow. JSON is validated by Pydantic with one repair attempt. A provider supporting ordinary text generation may still be unsuitable for the size and structure of the artifacts.

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
| `ENV` | `development` | `development`, `staging`, or `production`. Production requires provider credentials and explicit migrations; development/staging create missing studio tables. |
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
| `CAPTURE_README` | unset | `true` saves actual desktop screenshots to `docs/images/`. |
| `TEST_DATABASE_URL` | unset | Dedicated PostgreSQL URL ending in `_verification`; fixtures create and drop a unique schema per test. Otherwise tests use temporary SQLite databases. |

Do not use the verification credentials or Compose stack for public hosting.
