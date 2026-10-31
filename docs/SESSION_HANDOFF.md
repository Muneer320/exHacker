# Verification checkpoint

Updated: 2026-10-31 after resuming the end-of-day checkpoint. The previously unfinished container verification is complete. Changes are committed in focused units on the existing branch; no remote push or deployment was performed.

## Completed on resumption

- Started Docker Desktop and rebuilt/started the isolated PostgreSQL verification stack successfully. Existing data was retained and migrated; no verification volume was deleted.
- Reproduced and fixed a stale-worker race when a paused job resumed. Attempt numbers now remain monotonic, while explicit resume separately renews its interruption allowance (`e88c90d`).
- Verified active-call lease renewal and true worker shutdown/requeue with credential loss on recovery.
- Fixed extension of an older AI session so it preserves the currently selected provider/model (`91a4c7b`).
- Verified preservation of all four studio tables during both versioned 0001 upgrades and adoption of unversioned development databases (`dd616dd`).
- Added both BYOK browser journeys and the real SIGKILL/reentry check to CI, with separate browser output directories (`d2abe3e`).
- Refreshed the visual assets and documentation to describe the implemented behavior and observed verification results.

## Latest evidence

| Check | Result |
| --- | --- |
| SQLite backend suite | 70 passed |
| PostgreSQL backend suite | 70 passed |
| Native BYOK Chromium suite | 2 passed |
| Chromium against standalone Docker frontend | 6 passed |
| General Docker outage/recovery script | Passed |
| BYOK Docker SIGKILL/reentry script | Passed |
| Lint, format, TypeScript and production builds | Passed |
| Frozen Python runtime and frontend audits | No known vulnerabilities at the recorded verification date |

Details and boundaries are recorded in [VERIFICATION.md](VERIFICATION.md). All inference/search protocol tests use controlled external responses. No paid provider access or live model quality is implied.

## Local state

The disposable demo stack remains available at `http://localhost:3200`, with its API on loopback port 8200 and PostgreSQL internal. It uses explicit offline fixtures, no real API keys, and its existing verification volume. `docker compose -p exhacker-verify -f compose.verify.yml down` stops it while retaining that volume.

The temporary audit requirements export was removed in the previous session. A stale IDE tab may still display its name; it is not part of the repository.

## Release work that needs external evidence

1. Evaluate the six exposed models across five providers with real account access, representative briefs and Tavily results. Check output quality, account quotas, latency and actual spend.
2. Exercise a hosted TLS/database setup, backup restoration, rate/concurrency controls and process failures on the intended deployment.
3. Review CSP, logging/APM capture exclusions, swap/core-dump policy, retention and runtime OS advisories before collecting public user keys.
4. Repeat locked dependency audits and review provider catalog IDs/prices at release time. Gemini's documented introductory price ends 2026-12-31.

BYOK requires one persistent API process and its embedded worker. Multiple replicas and separate worker processes cannot access its RAM registry and are unsupported. Expiry/removal/restart requires matching provider/model credentials before resume; repeated work can repeat charges. Saved artifacts remain accessible without an AI session.
