# Verification evidence

Verified locally on **2026-10-31**. This records observed behavior and known limits; it is not a production certification or a claim that remote CI has already run this uncommitted work.

## Results

| Check | Result / scope |
| --- | --- |
| Backend SQLite suite | **34 passed** in isolated temporary databases. |
| Backend PostgreSQL suite | **34 passed** in the Linux test image, using a unique schema per test in PostgreSQL 16. |
| Container builds | Backend and standalone frontend built from locked dependencies on Linux, without host `.venv`, `node_modules`, or `.next` artifacts. |
| Compose startup | PostgreSQL, Alembic migration, backend, and frontend started successfully and reached their applicable completion/health gates. |
| Default SQLite Compose path | Passed the same HTTP workflow using the default Compose services with an isolated environment-file/port override and a new SQLite volume; the disposable test stack was removed afterward. |
| Browser against Docker | **6 passed** in Chromium: complete persisted workflow, proxy limits, workspace restore/delete, Markdown safety/diagrams, mobile layout, and service failure. |
| Browser against native servers | **6 passed** with the local Uvicorn/SQLite API and a freshly built Next.js server; document copy also verified with Windows clipboard line-ending normalization. |
| Runtime HTTP workflow | Passed: selection of a specific candidate, ownership, stale-edit rejection, all ten Markdown downloads matching ZIP entries, reproducible ZIP, and two ordered chat turns. |
| Outage/recovery | Passed: stopped API returns proxy 503; a worker-disabled API accepts a real queued job, is killed with SIGKILL, and the normal worker recovers the queue. Previously saved documents/chat remain unchanged. |
| Static checks | Ruff lint/format, ESLint, TypeScript, Prettier, and production Next.js build passed. |
| Frontend dependency audit | `npm audit` reports **0 known vulnerabilities** for the locked tree at verification time. |
| Python dependency audit | **Open finding:** 13 advisories in transitive `filelock` 3.32.7. See below. The local editable application package is not a published PyPI package and is skipped by the package advisory scanner. |
| Screenshots | Captured from the running application and visually inspected. Offline fixture labels are retained. |
| Documentation | Relative Markdown links checked; all five Mermaid diagrams from the README, architecture, and BYOK proposal rendered in the real browser renderer. |

Runtime images were built with Node.js 22 and Python 3.12.16. Backend inference adapter tests also run natively on Python 3.12. A third-party Pydantic warning about a TypedDict `ReadOnly` qualifier is emitted by the updated provider dependency; it does not fail the suite and is not suppressed.

## Bugs and configuration issues addressed

- Idea/stack approval previously committed before enqueueing the next job. Both now share a transaction, with regression tests proving queue failures preserve the prior revision and documents.
- Request-size checks previously relied on `Content-Length` or buffered the full proxy request. The proxy and API now bound actual streamed bytes before processing, including chunked requests.
- Research cache lookup previously checked only the newest cache row. Matching batches can now be reused after other searches, reducing unnecessary requests and budget consumption. Tested on SQLite and PostgreSQL.
- Model-generated Markdown images could trigger automatic external requests. They now render as deliberate external links; raw HTML/scripts and unsafe link protocols are checked in Chromium.
- Invalid Mermaid input is contained in the document's error panel instead of injecting an extra global error diagram. Real README/architecture/BYOK diagrams are also exercised by the browser trust-boundary test.
- Backend containers now run as a non-root user with a writable data directory; both runtime image user identities were inspected.
- Docker context exclusions cover nested `.env` files, private PEM files, database journals, logs, and temporary/export artifacts.
- Compatible dependency upgrades addressed frontend advisories and Python HTTP/TLS-related findings, including the CA bundle. An unused frontend dependency set was removed. No advisory-ignore flags were added.
- The optional local LiteLLM public metadata setting now works for native `.env` launches as well as process/Docker environments.

## Remaining Python advisory constraint

The current upstream LiteLLM 1.106.6 distribution declares `filelock>=3.16.1,<4.0`. The locked 3.32.7 release still has 13 advisories whose fixes require the 4.x line (most require 4.2.1). The [filelock maintainer's advisory](https://github.com/tox-dev/filelock/security/advisories/GHSA-v4x8-3wr5-3wq8) documents one representative local filesystem/symlink/journal attack and the 4.2.1 fix.

These findings involve local lock-file paths, permissions, shared writable directories, and platform-specific lock behavior. exHacker does not expose a remote lock-path API, and runtime images run as a non-root user with a private home/cache and no shared user-controlled cache mount. Those deployment properties reduce relevant attack opportunities; they do **not** patch the dependency or make its audit result clean.

No forced constraint override, downgrade, vendored patch, or scanner suppression has been applied. Resolution needs an upstream-supported dependency update or a separately reviewed compatibility/maintenance decision. Treat this as an open release dependency review, especially for shared-user hosts, user-controlled cache mounts, or deployments that add other local users. The application should not be described as having a clean Python security audit.

## What the tests do not prove

The full UI and worker journeys deliberately use explicit offline fixtures. Provider request/response and Tavily protocol tests use controlled boundaries. **No paid live AI or research request was made.** This verifies wiring, persistence, constraints, error handling, and rendering; it does not validate real-model originality, evidence quality, generated document quality, latency, provider account access, or actual billing.

Queued acceptance/recovery after process death is tested end to end. Expired running leases and superseded publication are tested in the backend suite. Unattended recovery can repeat external work; exactly-once inference billing is not established.

Still required before a public release:

- Resolve or explicitly review the remaining upstream filelock constraint and scan actual runtime OS images.
- Evaluate selected live models with representative briefs and real search evidence, including all providers advertised as supported.
- Test a hosted TLS/database configuration, backup restoration, and deployment-specific process failures.
- Measure load, queue age, concurrency, storage growth, latency, and costs; establish retention and perimeter abuse controls.
- Review a public-hosting security policy and CSP before collecting any user keys.

BYOK is documented in [the feasibility proposal](BYOK.md) and is **not implemented**. Neither package audits nor offline workflows prove the future BYOK security properties.

## Reproduce

Follow [TESTING.md](TESTING.md). The CI container job now reproduces PostgreSQL migration, backend tests, real HTTP outage/recovery, and browser checks against the standalone frontend. No external deployment, Git push, release publication, or paid provider evaluation was performed during this verification.
