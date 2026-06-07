# Pre-Deployment Checklist

Use this checklist before deploying to any environment (staging or production).

---

## Environment Configuration

- [ ] `.env` file created from `.env.example` with no placeholder values
- [ ] `ENVIRONMENT` set to `production` (not `development`)
- [ ] `DEBUG` set to `false`
- [ ] `LOG_LEVEL` set to `WARNING` or `INFO` (not `DEBUG`)
- [ ] `CORS_ORIGINS` contains the exact frontend URL(s) — no wildcards
- [ ] `DATABASE_URL` points to the production database (not localhost)
- [ ] `DATABASE_SYNC_URL` matches the async URL for Alembic compatibility
- [ ] `API_PREFIX` is consistent with load balancer / reverse proxy config

---

## Secrets Management

- [ ] No secrets committed to version control (check with `git diff --cached`)
- [ ] All API keys stored in platform secrets manager (Railway/Render/Vercel)
- [ ] `OPENAI_API_KEY` not hardcoded in any file
- [ ] `XAI_API_KEY` stored as a secret, not in `.env` in CI
- [ ] `GEMINI_API_KEY` stored as a secret
- [ ] `DATABASE_URL` does not contain the password in source code
- [ ] `SENTRY_DSN` uses the production DSN (if enabled)
- [ ] `.env` file added to `.gitignore` (verify: `cat .gitignore | grep .env`)
- [ ] No accidentally committed API keys (`git log -p | grep sk-` — should return nothing)

---

## Database

- [ ] Migrations have been run against production database
- [ ] Migration state is current (`alembic heads` shows a single head)
- [ ] Database backups configured (Supabase/Neon auto-backup enabled)
- [ ] Connection pooling configured (`pgbouncer=true` for Supabase)
- [ ] `DATABASE_POOL_SIZE` set appropriately for the production database limits
- [ ] `DATABASE_MAX_OVERFLOW` does not exceed database connection limits
- [ ] Database is accessible from the deployment platform (firewall rules checked)
- [ ] SSL/TLS required for database connections (`sslmode=require` for Neon)

### Migration Verification

```bash
cd backend
uv run alembic check          # No pending migrations
uv run alembic current        # Shows expected revision
```

---

## Backups

- [ ] Automated database backups enabled (Supabase: 7-day retention by default)
- [ ] Backup schedule confirmed (daily at minimum)
- [ ] Backup restoration tested or documented process exists
- [ ] Point-in-time recovery configured (if available on the plan)

---

## Monitoring

- [ ] Health check endpoint responds correctly: `GET /api/v1/health`
- [ ] Uptime monitor configured (BetterStack, Pingdom, or built-in)
- [ ] Error tracking configured (Sentry DSN in environment variables)
- [ ] Log drain or log aggregation configured (BetterStack Logs, Grafana)
- [ ] Cost tracking endpoints accessible: `GET /api/v1/debug/costs`
- [ ] LLM provider fallback verified — kill one API key, confirm fallback works
- [ ] Alert notifications configured (email, Slack, etc.)

---

## HTTPS

- [ ] HTTPS enforced on the frontend (Vercel: automatic)
- [ ] HTTPS enforced on the backend (Railway/Render: automatic with custom domain)
- [ ] HTTP → HTTPS redirect configured
- [ ] SSL certificate valid (not expired)
- [ ] HSTS headers set (optional but recommended)
- [ ] No mixed content warnings (HTTPS page loading HTTP resources)

---

## Domain Configuration

- [ ] Custom domain configured (if applicable)
- [ ] DNS A/AAAA records or CNAME pointing to the deployment platform
- [ ] Domain propagation verified (`dig yourdomain.com`)
- [ ] SSL certificate issued for the custom domain
- [ ] `CORS_ORIGINS` updated to include the custom domain
- [ ] `NEXT_PUBLIC_API_URL` updated to use the custom domain
- [ ] Redirect from `www.yourdomain.com` → `yourdomain.com` (or vice versa)

---

## Rollback Strategy

- [ ] Previous working Docker image tagged and available
- [ ] Railway/Render: deployment history reviewed — manual rollback possible
- [ ] Vercel: instant rollback available from deployment history
- [ ] Database migration is reversible (downgrade script exists)
- [ ] Rollback procedure documented:

### Rollback Procedure

```bash
# Railway
railway rollback            # Rolls back to previous deployment

# Render
# Dashboard > Deployments > Rollback to previous

# Vercel
# Dashboard > Deployments > ... > Promote to Production (previous deployment)

# Database (if migration caused the issue)
cd backend
uv run alembic downgrade -1  # Revert last migration
```

---

## Disaster Recovery Plan

### Scenario 1: Database Corruption

1. Restore from the most recent backup
2. Verify data integrity with health checks
3. Redeploy backend to clear connection pool
4. Verify API responses are normal

### Scenario 2: LLM Provider Outage

1. The `auto` fallback chain handles this — verify by checking `/debug/providers`
2. If all cloud providers are down, switch to `LLM_PROVIDER=ollama` with a local Ollama instance
3. Update the environment variable and redeploy

### Scenario 3: Full Platform Outage (Railway/Vercel)

1. Have a backup deployment on a second platform (e.g., Render if Railway is down)
2. Update DNS/CORS to point to the backup
3. Redeploy frontend with updated `NEXT_PUBLIC_API_URL`

### Scenario 4: Security Breach

1. Rotate all API keys immediately
2. Rotate database password
3. Check deployment logs for unauthorized access
4. Reset cost tracker: `POST /api/v1/debug/costs/reset`
5. Review Sentry/error logs for suspicious activity

---

## Security

- [ ] `SENTRY_DSN` does not expose secrets in Sentry error logs
- [ ] File upload validation implemented (if `UPLOAD_DIR` is used)
- [ ] Export directory is not publicly accessible
- [ ] API rate limiting considered (if high traffic expected)
- [ ] Input validation on all API endpoints (FastAPI/Pydantic handles this)
- [ ] No sensitive data in URL parameters
- [ ] Authentication/authorization considered (if enabling user-specific features)

---

## Performance

- [ ] Database indexes created for frequent query patterns
- [ ] Connection pool size appropriate for the database tier
- [ ] Frontend static assets are optimized (Next.js handles this)
- [ ] API response times measured and acceptable
- [ ] Cold start time acceptable (free tiers: 3-10s expected)
- [ ] No memory leaks in agent workflow execution

### Verify Performance

```bash
# Test health endpoint response time
curl -w "%{time_total}s\n" -o /dev/null https://your-backend.com/api/v1/health

# Simulate a project generation
curl -X POST https://your-backend.com/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"challenge": "Build an AI app"}'
```

---

## Final Verification

- [ ] Frontend loads without console errors
- [ ] Backend health check returns `{"status": "ok"}`
- [ ] LLM calls succeed (submit a challenge, verify response)
- [ ] Database queries succeed (check project creation in UI)
- [ ] CORS not blocking requests (check browser DevTools)
- [ ] Environment variables are all correctly set
- [ ] `/.well-known/` endpoints respond (if applicable)

### Smoke Test

```bash
# 1. Health check
curl https://your-backend.com/api/v1/health

# 2. Cost/debug endpoint (should not expose sensitive data)
curl https://your-backend.com/api/v1/debug/costs

# 3. CORS check
curl -H "Origin: https://your-frontend.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS \
  https://your-backend.com/api/v1/projects \
  -v 2>&1 | grep -i "access-control"

# 4. Full flow (if possible via CLI)
```

---

## Post-Deployment

- [ ] Monitor logs for first 24 hours
- [ ] Verify cost tracking at `/debug/costs` after first day of usage
- [ ] Set a calendar reminder to review free tier usage weekly
- [ ] Document the deployed URLs and credentials in a secure location
- [ ] Share the deployment URL with stakeholders/testers

---

## Quick Reference: Deployment Commands

```bash
# Verify environment
cd backend && uv run alembic current

# Run migrations
uv run alembic upgrade head

# Check migration status
uv run alembic check

# Run tests
uv run pytest

# Run linters
uv run ruff check . && uv run mypy app

# Build frontend
cd frontend && npm run build
```
