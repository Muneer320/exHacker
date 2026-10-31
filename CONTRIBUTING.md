# Contributing to exHacker

Thanks for helping turn a promising challenge into a plan a team can actually build. Start with the [README](README.md), [architecture](docs/ARCHITECTURE.md), and [configuration](docs/CONFIGURATION.md).

For a substantial workflow, persistence, authentication, or credential-handling change, open an issue describing the user problem and proposed behavior first. Preserve the implemented [BYOK lifecycle](docs/BYOK.md): owner-bound expiring RAM leases, no credential persistence, safe job recovery, and explicit provider selection.

## Local checks

Use Python 3.12, uv, Node.js 22, and Docker Compose v2 for the tested development path. Install locked dependencies with `uv sync --frozen --extra dev` in `backend` and `npm ci` in `frontend`.

```sh
cd backend
uv run ruff check app tests migrations
uv run ruff format --check app tests migrations
uv run pytest -q
cd ../frontend
npm run lint
npm run typecheck
npm run format:check
npm run build
npx playwright install chromium
npm test
```

For changes affecting persistence, containers, or the server proxy, also run the PostgreSQL/container checks in [testing](docs/TESTING.md). Test actual interactions when touching the UI. Add regression tests for meaningful bugs; avoid tests that merely restate implementation details.

## Change standards

- Preserve the intake → researched ideas → explicit idea approval → stack review/approval → Markdown handoff → assistant flow.
- Keep frontend and backend contracts synchronized. Scope every project resource to its owner and guard writes with the current revision.
- Never hide provider errors behind sample output. Offline fixtures must remain explicitly labeled and opt-in.
- Treat generation, request input, Markdown, and retrieved sources as untrusted. Keep credentials out of job payloads, artifacts, prompts, and browser bundles.
- Add a migration for schema changes. Do not rewrite or delete old prototype data as a shortcut.
- Explain any new dependency and update the lockfile, documentation, and relevant checks.

Pull requests should explain the concrete problem, resulting behavior, validation performed, and remaining limits. Include screenshots for visible changes, and identify fixtures or mocked provider boundaries honestly. Do not claim a live-provider test if no actual provider request was made.

Never commit `.env`, real API/workspace keys, local databases, private exports, or generated test traces containing user data. See [SECURITY.md](SECURITY.md) for private vulnerability reporting. Contributions are covered by the repository's [MIT license](LICENSE).
