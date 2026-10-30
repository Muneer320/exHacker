import { defineConfig, devices } from "@playwright/test";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { randomUUID } from "node:crypto";

const database = join(
  tmpdir(),
  `exhacker-browser-${randomUUID()}.db`,
).replaceAll("\\", "/");
const externalBase = process.env.PLAYWRIGHT_BASE_URL;
const byok = process.env.PLAYWRIGHT_BYOK === "true";

export default defineConfig({
  testDir: "./tests",
  testMatch: byok ? "byok.spec.ts" : "studio.spec.ts",
  timeout: 120000,
  expect: { timeout: 30000 },
  workers: 1,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: externalBase || "http://127.0.0.1:3100",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    reducedMotion: "reduce",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: externalBase
    ? undefined
    : [
        {
          command: `uv run uvicorn ${byok ? "tests.byok_server" : "app.main"}:app --host 127.0.0.1 --port 8101`,
          cwd: "../backend",
          url: "http://127.0.0.1:8101/ready",
          reuseExistingServer: false,
          env: {
            DATABASE_URL: `sqlite+aiosqlite:///${database}`,
            ENV: "development",
            EXHACKER_DEBUG: "false",
            STUDIO_DEMO_MODE: byok ? "false" : "true",
            AI_ACCESS_MODE: "byok",
            TAVILY_API_KEY: byok ? "synthetic-test-search-key" : "",
            STUDIO_WORKER_ENABLED: "true",
            FREE_TIER_PROJECTS_PER_DAY: "50",
          },
          timeout: 60000,
        },
        {
          command:
            "npm run build && npm run start -- --hostname 127.0.0.1 --port 3100",
          url: "http://127.0.0.1:3100",
          reuseExistingServer: false,
          env: {
            BACKEND_URL: "http://127.0.0.1:8101",
            NEXT_TELEMETRY_DISABLED: "1",
          },
          timeout: 240000,
        },
      ],
});
