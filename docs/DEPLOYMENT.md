# Deployment and operations

[Back to the project](../README.md)

The frontend runs as a standalone Next.js Node server. The FastAPI backend needs a persistent process because it owns an embedded background worker. Use one Uvicorn worker initially and PostgreSQL for a public installation. Hosted infrastructure, paid-provider quality, and load under a real workload remain release checks; a green local container run is not proof of those properties.

## Local Docker evaluation

With Docker Compose v2 available:

```sh
docker compose -p exhacker-verify -f compose.verify.yml up --build --wait
```

Open <http://localhost:3200>. This runs the standalone frontend, backend, PostgreSQL 16, and an initial Alembic migration. No `.env` or real key is used. The UI and documents explicitly identify offline demonstration mode. The verification database has its own named volume; normal development data is not shared. Only loopback ports 3200 and 8200 are published; PostgreSQL is internal.

For the separate local live/development stack, copy `.env.example` to `.env`, supply real operator credentials, and run:

```sh
docker compose up --build --wait
```

Open <http://localhost:3000>. This stack persists SQLite at `/data/exhacker.db` in `studio-data`, overriding the root `.env` database URL. **The default Compose file is for local evaluation, not production PostgreSQL hosting.** Do not try to change that database merely by editing `.env` while keeping the overriding Compose environment unchanged.

Both runtime images use non-root users. The backend image has a `tests` target with development tools; the default final target contains runtime dependencies. The frontend contains the standalone server plus its static/public assets.

## Production setup

1. Provision PostgreSQL with a private/restricted network, backups, and tested TLS settings. Establish a restore procedure before accepting user data.
2. Configure backend process secrets: `ENV=production`, `STUDIO_DEMO_MODE=false`, `DATABASE_URL`, `AI_MODEL`, the selected AI credential, `TAVILY_API_KEY`, and verified pricing/budget limits. Provider keys are operator-managed in the current release; user BYOK is still a proposal.
3. Back up existing data, then run migrations once as a release job using the same application image and database configuration:

   ```sh
   cd backend
   uv sync --frozen
   uv run alembic upgrade head
   ```

4. Start the backend:

   ```sh
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
   ```

5. Build/run `Dockerfile.frontend` or deploy the frontend to a compatible Next.js host. Set server-side `BACKEND_URL` to the reachable backend **origin**. Keep `NEXT_PUBLIC_API_URL` unset for the same-origin proxy. The proxy adds `/api/v1` itself.
6. Put HTTPS and request/rate/concurrency limits in front of the public frontend. Restrict direct backend access where practical. Configure exact CORS origins only if browsers must call the API directly.
7. Verify readiness, a real paid workflow, exports, ownership, provider failure, and recovery on that installation. Run a representative load test before scaling or publishing throughput claims.

Do not run the verification Compose file in production. Production rejects demo mode and absent provider configuration, but a nonempty API-key string is not proof of valid provider access. Startup does not send billable validation calls.

### Container commands

```sh
docker build -f Dockerfile.backend -t exhacker-backend .
docker build -f Dockerfile.frontend -t exhacker-frontend .
```

Supply backend configuration through the host's secret mechanism or a protected environment file. Run `alembic upgrade head` as a one-off command before the backend service, then run the normal image command. Set the frontend container's `BACKEND_URL` to a DNS name reachable **inside that container**; `127.0.0.1` points to the frontend container itself. `Dockerfile.frontend` starts `node server.js` from the standalone output; copied `.next/static` and `public` are required.

## Health, recovery, and observability

| Endpoint / signal | Meaning |
| --- | --- |
| `GET /health` or `/api/v1/health` | Process responds; not a provider or database check. |
| `GET /ready` | Can query the studio project schema; exposes whether the worker is enabled. |
| Job events/status | Saved operation progress, failures, and retry attempts. No fabricated percentages. |
| `ai_cost`, `search_count` | Configured-rate accounting and attempted search count; not provider invoices. |

Watch database errors, queue age, repeatedly expired leases, failure rates, duration, budget exhaustion, and provider throttling. Readiness does not prove model quality or continuously test an inference call. A disabled worker can leave healthy API requests accepting queued jobs; only disable it intentionally.

Graceful shutdown requeues the worker's current owned job. Abrupt shutdown requires lease expiry before a running job can be reclaimed. Recovery can repeat paid work; do not advertise exactly-once external calls. Keep the application alive long enough to shut down cleanly and use deployment readiness gates.

Production logging is structured JSON. Do not enable verbose HTTP, provider SDK tracing, request body capture, or session replay around sensitive data. Application exception traces may contain project data from failed persistence operations; treat operational logs as sensitive and apply an appropriate retention/access policy.

## Migrations and data

Development and staging create missing `studio_*` tables automatically. Production never automatically applies DDL. The initial migration creates four additive tables or adopts the matching development studio schema. Old prototype tables are not rewritten or assigned to anonymous workspaces. Test restoration and migration on a copy before touching valuable data.

Keep the database across container recreation. `docker compose down` stops services without deleting named volumes. Adding `-v` deletes the named volumes for that Compose project; use it only for deliberately disposable verification data. There is no application-level soft-delete or undo for project deletion.

## Release boundaries

Anonymous workspace keys provide resource isolation, not registered accounts, team collaboration, account recovery, or reliable abuse prevention. New keys can bypass per-workspace quotas. Public launch requires perimeter controls and a deliberate account/abuse policy. [SECURITY.md](../SECURITY.md) describes the current privacy model; [BYOK.md](BYOK.md) describes a proposed change that has not shipped.
