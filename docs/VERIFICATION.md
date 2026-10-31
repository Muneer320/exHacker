# Verification evidence

Verified locally on **2026-10-31** against the completed BYOK implementation. These results establish the behaviors below, not a production certification or a claim that remote CI has run.

## Results

| Check | Observed result |
| --- | --- |
| Backend SQLite suite | **70 passed** in isolated temporary databases, including credential lifecycle, all five adapters, full synthetic live-pipeline journeys, ownership and recovery. |
| Backend PostgreSQL suite | **70 passed** in the Linux test image against PostgreSQL 16; each test owns a separate disposable schema. |
| BYOK browser journeys | **2 passed** against the real local API, worker, database and Next.js with synthetic provider/search HTTP responses. Covers key clearing/storage, provider switching, extension without changing selection, document preservation, reload and matching-session resume. |
| Browser against Docker | **6 passed** against the standalone frontend, real proxy, API, embedded worker and PostgreSQL: complete workflow, exports, workspace recovery/deletion, request limits, Markdown/Mermaid safety, mobile layout and visible outage. |
| Container builds/startup | Backend and frontend built from locked dependencies, migrated the existing verification database and reached readiness/health gates. The previous package-download blockage is resolved. |
| Legacy migration | Both versioned 0001 studio databases and unversioned development schemas upgrade to 0002 while preserving project context, queued jobs, artifact snapshots and messages. |
| General outage/recovery | Real API stop produces proxy 503; SIGKILL after queued acceptance is recovered by the normal worker. Saved documents, exports and ordered chat remain unchanged. |
| BYOK process restart | Real SIGKILL loses RAM credentials; the durable job pauses before external calls. Fresh matching credentials permit requeue; cancellation releases the project lock. Prior artifacts survive. |
| Static checks | Ruff lint/format, ESLint, TypeScript, Prettier, native production build and Linux standalone build pass. CI YAML parses. |
| Frontend dependency audit | **0 known vulnerabilities** in the locked tree at verification time. |
| Frozen Python runtime audit | **No known vulnerabilities found**. LiteLLM and its vulnerable transitive filelock chain were removed; no override or scanner suppression was used. |
| Documentation/assets | Local Markdown links and em-dash removal checked. All five repository Mermaid diagrams render in Chromium. Real application screenshots retain fixture/privacy disclosures and contain no entered provider key. |

The CI workflow now runs the demo and BYOK browser suites separately and executes both Docker recovery scripts. Local equivalents passed; no Git push or remote workflow execution was performed.

## Credential and workflow guarantees exercised

- Workspace-owned leases reject other owners, expire, renew explicitly, enforce capacity, clear on removal/restart and cancel active requests.
- Keys do not appear in project/job/artifact/message records, public responses or formatter output in the covered tests. Malformed credential input uses safe validation errors. Unexpected job errors expose only safe messages/types.
- Each new operation captures its provider/model/session. Switching future operations preserves existing artifacts. Missing BYOK credentials never fall back to the operator key.
- Paused operations accept a fresh matching provider/model lease, or can be cancelled. Resume retains monotonically increasing attempt identities, preventing a delayed old worker from pausing or publishing over a resumed attempt. A regression reproduced the original race before the fix.
- Extending an older session does not select it for future jobs. Renewal during an active call replaces its old deadline. Worker shutdown cancels the call and requeues the operation; loss of RAM on restart then requests credentials.
- Five native HTTPX protocols verify authentication headers, fixed endpoints, response parsing, token accounting, no redirects and request-scoped client closure. Provider error bodies and credential-like output are discarded; oversize/malformed/truncated results fail safely.
- Idea/stack approval and follow-up enqueue share a transaction. Stale revisions and superseded attempts cannot overwrite newer work. All ten Markdown files match their ZIP entries; reading/exporting never regenerates them.
- Untrusted Markdown cannot execute raw HTML or load tracking images. Mermaid renders in strict mode and contains invalid-diagram errors.

## What this does not establish

**No paid AI or live research request was made.** Full workflow tests use synthetic external responses, clearly separated from normal production code. Tests establish wiring, persistence, validation, recovery and rendering. They do not establish provider account access, model originality, factual research quality, document quality, real latency or actual bills.

The RAM-only architecture requires **one API process with its embedded worker**. Multiple replicas/separate workers are unsupported. A browser reload loses session references; expiry, removal or server restart requires credential reentry for affected work. Recovery can repeat external calls and charges. Physical byte zeroization, OS swap/core-dump behavior, hosting logs/APM and provider retention policies are outside application guarantees.

Still required for a public release:

- Evaluate every exposed live model and real Tavily evidence with representative briefs and provider account limits.
- Verify hosted HTTPS/private backend links, database TLS, backup restoration and deployment-specific failures.
- Review CSP, retention, perimeter abuse/rate limits, concurrency, storage growth and operating costs.
- Scan actual runtime OS images and repeat dependency audits at release time.

## Reproduce

Follow [TESTING.md](TESTING.md). Use only the disposable `exhacker-verify` stack for process-death checks. The default Compose file is a local SQLite setup, not production hosting. See [BYOK](BYOK.md), [deployment](DEPLOYMENT.md) and [security](../SECURITY.md) for operational boundaries.
