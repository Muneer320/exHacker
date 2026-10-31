# Verification evidence

Verified locally on **2026-10-31**. This records observed behavior and known limits; it is not a production certification or a claim that remote CI has already run this local work.

## Latest BYOK checkpoint

Completed locally on 2026-10-31 before the requested end-of-day pause:

| Check | Observed result |
| --- | --- |
| Backend SQLite suite | **65 passed**, including the RAM registry, five native adapters, full synthetic live-pipeline journeys, credential isolation/disclosure checks and durable-job recovery. |
| BYOK Chromium journeys | **2 passed** against the real API/worker/SQLite/Next.js with synthetic external HTTP responses: provider switching, cleared key input, no browser-storage key, document persistence, reload and reconnect/resume. |
| Static checks | Ruff lint/format, ESLint, TypeScript and native production build passed. |
| Frontend audit | **0 known vulnerabilities**. |
| Locked Python runtime audit | **No known vulnerabilities found**, using an exported frozen requirements set and pip-audit. An initial PyPI timeout succeeded on retry. The temporary export was removed. |
| New Docker verification | Frontend image built successfully; the combined rebuild was cancelled at the requested pause while backend package downloads stalled. The prior stack remains intact. See [session handoff](SESSION_HANDOFF.md). |

LiteLLM and its transitive filelock dependency were removed as part of the approved request-scoped HTTPX transport replacement. This resolves the earlier locked-tree advisory constraint without an override or scanner suppression. The new model catalog and five adapters are verified at controlled protocol boundaries, not with paid provider accounts.

The expanded PostgreSQL suite, both process-restart scripts and the six-test demonstration browser suite must be rerun on the final BYOK images. The previously successful results below are retained as historical evidence, not substituted for that rerun.

## Earlier restoration baseline

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

## Earlier dependency finding resolved

The restoration baseline used LiteLLM 1.106.6, which constrained filelock below its patched 4.x line. The approved native HTTPX replacement removes both packages. The latest frozen-runtime audit reports no known advisories. Container OS scanning and hosted infrastructure review remain separate release checks.

## What the tests do not prove

The full UI and worker journeys deliberately use explicit offline fixtures. Provider request/response and Tavily protocol tests use controlled boundaries. **No paid live AI or research request was made.** This verifies wiring, persistence, constraints, error handling, and rendering; it does not validate real-model originality, evidence quality, generated document quality, latency, provider account access, or actual billing.

Queued acceptance/recovery after process death is tested end to end. Expired running leases and superseded publication are tested in the backend suite. Unattended recovery can repeat external work; exactly-once inference billing is not established.

Still required before a public release:

- Scan actual runtime OS images and repeat locked dependency audits at release time.
- Evaluate selected live models with representative briefs and real search evidence, including all providers advertised as supported.
- Test a hosted TLS/database configuration, backup restoration, and deployment-specific process failures.
- Measure load, queue age, concurrency, storage growth, latency, and costs; establish retention and perimeter abuse controls.
- Review a public-hosting security policy and CSP before collecting any user keys.

BYOK is implemented and documented in [the credential lifecycle guide](BYOK.md). Automated tests establish specific application properties; they do not establish physical memory zeroization, host security, provider policy compliance or live-model quality.

## Reproduce

Follow [TESTING.md](TESTING.md). The CI container job now reproduces PostgreSQL migration, backend tests, real HTTP outage/recovery, and browser checks against the standalone frontend. No external deployment, Git push, release publication, or paid provider evaluation was performed during this verification.
