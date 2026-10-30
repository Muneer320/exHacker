# exHacker frontend

The Next.js workspace for the product studio. See the [repository README](../README.md) for the complete product flow, backend setup, environment configuration, deployment, and verification.

```sh
npm ci
npm run dev
```

The browser uses `/api/v1` on the same origin. The server proxy reads `BACKEND_URL`, defaulting to `http://127.0.0.1:8000`. Provider keys are currently operator-managed Python backend settings; [user BYOK](../docs/BYOK.md) is a proposal awaiting approval. Never put provider keys in `NEXT_PUBLIC_*` variables or the intake draft.

Routes: `/projects/new` for intake, `/projects` for private workspaces, and `/projects/[id]/{overview,ideas,stack,docs,chat,research,history}` for the studio. Older workspace paths redirect to their current equivalents.

See [testing](../docs/TESTING.md) for browser checks, Docker targeting, and screenshots. The frontend image runs the standalone Node server with its static/public assets; it does not expose provider secrets. [Configuration](../docs/CONFIGURATION.md) explains which environment variables are read by Next.js versus Python.
