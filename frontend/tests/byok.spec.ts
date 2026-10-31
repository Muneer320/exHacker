import { expect, test, type Page } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import { resolve } from "node:path";

const key = "synthetic-browser-key-never-real";

async function connect(page: Page, provider: string) {
  await page.getByLabel("AI session settings").click();
  const dialog = page.getByRole("dialog");
  await dialog
    .getByRole("combobox", { name: "AI provider", exact: true })
    .selectOption(provider);
  if (process.env.CAPTURE_README === "true" && provider === "anthropic") {
    await page.setViewportSize({ width: 1440, height: 1000 });
    await mkdir(resolve("../docs/images"), { recursive: true });
    // Capture before a credential is entered, never a filled password field.
    await page.screenshot({ path: resolve("../docs/images/ai-session.png") });
  }
  await dialog.getByLabel("Provider API key", { exact: true }).fill(key);
  await dialog
    .getByRole("button", { name: "Start AI session", exact: true })
    .click();
  await expect(
    dialog.getByText("minutes remaining", { exact: false }).first(),
  ).toBeVisible();
  await expect(
    dialog.getByLabel("Provider API key", { exact: true }),
  ).toHaveValue("");
  await dialog.getByLabel("Close AI settings").click();
}

test("BYOK switches providers and preserves documents after session loss", async ({
  page,
}) => {
  await page.goto("/projects/new");
  await connect(page, "anthropic");
  await page
    .getByLabel("Your idea or challenge theme")
    .fill("Help rural students find mentors with low-bandwidth tools");
  await page.locator("#name-0").fill("Asha");
  await page.locator("#skill-0-0").fill("React");
  await page
    .getByRole("button", { name: "Research & develop my ideas" })
    .click();
  await expect(page.locator(".idea-card")).toHaveCount(5);
  const storage = await page.evaluate(() =>
    JSON.stringify({
      local: { ...localStorage },
      session: { ...sessionStorage },
    }),
  );
  expect(storage).not.toContain(key);
  await page
    .locator(".idea-card")
    .first()
    .getByRole("button", { name: "Choose this direction" })
    .click();
  await expect(page).toHaveURL(/\/stack$/);
  await expect(
    page.getByRole("button", { name: "Edit technology choices" }),
  ).toBeEnabled();
  await connect(page, "gemini");
  await page.getByLabel("AI session settings").click();
  const dialog = page.getByRole("dialog");
  const older = dialog.locator(".session-row").filter({ hasText: "anthropic" });
  const selected = dialog.locator(".session-row").filter({ hasText: "gemini" });
  const renewed = page.waitForResponse(
    (response) =>
      response.url().endsWith("/renew") &&
      response.request().method() === "POST",
  );
  await older.getByRole("button", { name: "Extend", exact: true }).click();
  expect((await renewed).ok()).toBeTruthy();
  await expect(selected).toContainText("Selected");
  await expect(
    older.getByRole("button", { name: "Use", exact: true }),
  ).toBeEnabled();
  await expect(
    selected.getByRole("button", { name: "Use", exact: true }),
  ).toBeDisabled();
  await dialog.getByLabel("Close AI settings").click();
  await page
    .getByRole("button", { name: "Confirm stack & write documents" })
    .click();
  await expect(page.locator(".document-files button")).toHaveCount(10);
  await page.reload();
  await expect(page.locator(".document-files button")).toHaveCount(10);
  await page.getByRole("link", { name: "Assistant", exact: true }).click();
  await page
    .getByLabel("Ask your project assistant")
    .fill("What should we build first?");
  await page
    .getByRole("button", { name: "Send message →", exact: true })
    .click();
  await expect(page.locator(".notice.error")).toContainText(
    "Reconnect an API key",
  );
  await connect(page, "groq");
  await page
    .getByRole("button", { name: "Send message →", exact: true })
    .click();
  await expect(page.locator(".chat-message.assistant")).toContainText(
    "Integration fixture",
  );
  await page.getByRole("link", { name: "Documents", exact: true }).click();
  await expect(page.locator(".document-files button")).toHaveCount(10);
});

test("paused jobs explain credential recovery and resume with a matching session", async ({
  page,
}) => {
  await page.goto("/projects/new");
  await connect(page, "openai");
  const result = await page.evaluate(async () => {
    const owner = localStorage.getItem("exhacker.workspace.access.v2")!;
    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${owner}`,
    };
    const lease = await fetch("/api/v1/ai/leases", {
      method: "POST",
      headers,
      body: JSON.stringify({
        provider: "openai",
        model: "gpt-6-luna",
        key: "queued-test-key",
      }),
    }).then((r) => r.json());
    const project = await fetch("/api/v1/projects", {
      method: "POST",
      headers: { ...headers, "X-AI-Lease": lease.data.id },
      body: JSON.stringify({
        idea: "Coordinate offline mentor sessions for rural students",
        available_hours: 24,
        teammates: [
          {
            name: "Asha",
            skills: [{ technology: "React", proficiency: "advanced" }],
          },
        ],
      }),
    }).then((r) => r.json());
    await fetch("/api/v1/ai/leases", { method: "DELETE", headers });
    return project.data.id;
  });
  await page.goto(`/projects/${result}/ideas`);
  await expect(
    page.getByRole("button", { name: "Reconnect API key", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Resume operation", exact: true }),
  ).toBeDisabled();
  await page
    .getByRole("button", { name: "Reconnect API key", exact: true })
    .click();
  const dialog = page.getByRole("dialog");
  await expect(
    dialog.getByRole("combobox", { name: "AI provider", exact: true }),
  ).toHaveValue("openai");
  await dialog.getByLabel("Provider API key", { exact: true }).fill(key);
  await dialog
    .getByRole("button", { name: "Start AI session", exact: true })
    .click();
  await dialog.getByLabel("Close AI settings").click();
  await page
    .getByRole("button", { name: "Resume operation", exact: true })
    .click();
  await expect(page.locator(".idea-card")).toHaveCount(5);
});
