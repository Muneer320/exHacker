import { expect, test } from "@playwright/test";
import { mkdir, readFile } from "node:fs/promises";
import { resolve } from "node:path";

test("complete a real persisted browser workflow, refine, export, and ask the assistant", async ({
  page,
  context,
}) => {
  const errors: string[] = [];
  await page.setViewportSize({ width: 1440, height: 1000 });
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/projects/new");
  await page
    .getByLabel("Your idea or challenge theme")
    .fill("Help rural students find STEM mentors despite unreliable internet");
  await page.getByLabel("Project name").fill("Rural mentoring studio");
  await page.locator("#name-0").fill("Asha");
  await page.locator("#skill-0-0").fill("React");
  await page
    .getByRole("button", { name: "+ Add teammate", exact: true })
    .click();
  await page.locator("#name-1").fill("Dev");
  await page.locator("#skill-1-0").fill("Python");
  await page
    .getByRole("button", { name: "Research & develop my ideas" })
    .click();
  await expect(page).toHaveURL(/\/projects\/[^/]+\/ideas/);
  await expect(page.locator(".idea-card")).toHaveCount(5);
  await expect(
    page.getByText("Demonstration mode · No live research or AI validation."),
  ).toBeVisible();
  await page.getByRole("button", { name: "Compare all five" }).click();
  await expect(page.locator(".comparison-table")).toBeVisible();
  if (process.env.CAPTURE_README === "true") {
    await mkdir(resolve("../docs/images"), { recursive: true });
    await page.setViewportSize({ width: 1440, height: 1120 });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: resolve("../docs/images/ideas.png") });
    await page.setViewportSize({ width: 1440, height: 1000 });
  }
  const first = page.locator(".idea-card").first();
  await first
    .getByRole("button", { name: "Refine with my own prompt" })
    .click();
  await first
    .getByLabel("What would you change?")
    .fill("Prioritize offline mentoring for rural schools");
  await first
    .getByRole("button", { name: "Polish & rescore this idea" })
    .click();
  await expect(
    page.getByText(/Requested refinement: Prioritize offline mentoring/),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByText(/Requested refinement: Prioritize offline mentoring/),
  ).toBeVisible();
  await page
    .locator(".idea-card")
    .filter({ hasText: "Requested refinement:" })
    .getByRole("button", { name: "Choose this direction" })
    .click();
  await expect(page).toHaveURL(/\/stack$/);
  await expect(
    page.getByRole("button", { name: "Edit technology choices" }),
  ).toBeEnabled();
  await page.getByRole("button", { name: "Edit technology choices" }).click();
  await page.locator("#technology-2").fill("Convex");
  await page
    .getByRole("button", { name: "Apply changes & review compatibility" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Convex", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Confirm stack & write documents" })
    .click();
  await expect(page).toHaveURL(/\/docs$/);
  await expect(page.locator(".document-files button")).toHaveCount(10);
  await expect(page.locator(".markdown-preview")).toContainText(
    "Product Requirements Document",
  );
  await expect(page.locator(".markdown-preview")).toContainText("FR-01");
  await page.getByRole("button", { name: "AGENTS.md" }).click();
  await expect(page.locator(".markdown-preview")).toContainText("Convex");
  await expect(page.locator(".markdown-preview")).toContainText("Asha");
  await page
    .getByRole("button", { name: "Markdown source", exact: true })
    .click();
  const markdown = await page.locator(".markdown-source").innerText();
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await page
    .locator(".document-toolbar")
    .getByRole("button", { name: "Copy", exact: true })
    .click();
  await expect
    .poll(() =>
      page.evaluate(async () =>
        (await navigator.clipboard.readText()).replace(/\r\n/g, "\n"),
      ),
    )
    .toBe(markdown);
  await page.getByRole("button", { name: "Preview", exact: true }).click();
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: "test-results/workspace-documents.png" });
  if (process.env.CAPTURE_README === "true") {
    await mkdir(resolve("../docs/images"), { recursive: true });
    await page.screenshot({ path: resolve("../docs/images/workspace.png") });
  }
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download all .md files" }).click();
  expect((await download).suggestedFilename()).toMatch(/\.zip$/);
  await page.getByRole("link", { name: "Talk to your assistant" }).click();
  await page
    .getByLabel("Ask your project assistant")
    .fill("How should Asha and Dev split the work?");
  await page.getByRole("button", { name: "Send message" }).click();
  await expect(page.locator(".chat-message.assistant")).toContainText("Convex");
  await page.reload();
  await expect(page.locator(".chat-message.user")).toContainText(
    "How should Asha and Dev split the work?",
  );
  await expect(page.locator(".chat-message.assistant")).toContainText("Asha");
  expect(errors).toEqual([]);
  if (process.env.CAPTURE_README === "true") {
    const artwork = await context.newPage();
    await artwork.setViewportSize({ width: 1280, height: 640 });
    await artwork.setContent(
      await readFile(resolve("../docs/images/social-preview.svg"), "utf8"),
    );
    await artwork.locator("svg").screenshot({
      path: resolve("../docs/images/social-preview.png"),
    });
    await artwork.close();
  }
});

test("the proxy rejects oversized requests", async ({ request }) => {
  const response = await request.post("/api/v1/projects", {
    data: "x".repeat(240000),
  });
  expect(response.status()).toBe(413);
  expect((await response.json()).error.message).toContain("large");
});

test("a saved workspace can be restored in another browser and deleted", async ({
  page,
  browser,
}) => {
  await page.goto("/projects");
  await expect(
    page.getByRole("heading", { name: "Your next project starts" }),
  ).toBeVisible();
  const key = await page.evaluate(() =>
    localStorage.getItem("exhacker.workspace.access.v2"),
  );
  const headers = { Authorization: `Bearer ${key}` };
  const created = await page.request.post("/api/v1/projects", {
    headers,
    data: {
      name: "Recovery verification",
      idea: "Build a practical accessibility guide for local public spaces",
      available_hours: 24,
      teammates: [
        {
          name: "Sam",
          skills: [{ technology: "TypeScript", proficiency: "advanced" }],
        },
      ],
    },
  });
  expect(created.status()).toBe(201);
  const project = (await created.json()).data;
  await expect
    .poll(
      async () =>
        (
          await (
            await page.request.get(`/api/v1/projects/${project.id}`, {
              headers,
            })
          ).json()
        ).data.active_job,
    )
    .toBeNull();
  const other = await browser.newContext();
  try {
    const restored = await other.newPage();
    await restored.goto(`/projects/${project.id}/ideas`);
    await expect(restored.locator('.studio-card [role="alert"]')).toContainText(
      "not found",
    );
    await restored.goto("/projects");
    await expect(restored.locator(".project-list-card")).toHaveCount(0);
    await restored
      .getByRole("button", { name: "Workspace access & recovery" })
      .click();
    await restored.getByLabel("Restore another workspace").fill(key!);
    await restored
      .getByRole("button", { name: "Restore workspace", exact: true })
      .click();
    await expect(restored.locator(".project-list-card")).toContainText(
      "Recovery verification",
    );
    restored.once("dialog", (dialog) => dialog.accept());
    await restored.getByRole("button", { name: "Delete project" }).click();
    await expect(restored.locator(".project-list-card")).toHaveCount(0);
    expect(
      (
        await page.request.get(`/api/v1/projects/${project.id}`, { headers })
      ).status(),
    ).toBe(404);
  } finally {
    await other.close();
  }
});

test("untrusted Markdown cannot execute HTML or load tracking images, and diagrams render", async ({
  page,
}) => {
  const errors: string[] = [];
  const tracking: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (request.url().includes("tracking.invalid"))
      tracking.push(request.url());
  });
  await page.goto("/projects");
  await expect(
    page.getByRole("heading", { name: "Your next project starts" }),
  ).toBeVisible();
  const key = await page.evaluate(() =>
    localStorage.getItem("exhacker.workspace.access.v2"),
  );
  const headers = { Authorization: `Bearer ${key}` };
  const created = await page.request.post("/api/v1/projects", {
    headers,
    data: {
      name: "Markdown safety verification",
      idea: "Build accessible routes to local public services",
      available_hours: 48,
      teammates: [
        {
          name: "Sam",
          skills: [{ technology: "Python", proficiency: "advanced" }],
        },
      ],
    },
  });
  expect(created.status()).toBe(201);
  const id = (await created.json()).data.id;
  const path = `/api/v1/projects/${id}`;
  async function idle() {
    await expect
      .poll(
        async () =>
          (await (await page.request.get(path, { headers })).json()).data
            .active_job,
      )
      .toBeNull();
    return (await (await page.request.get(path, { headers })).json()).data;
  }
  let project = await idle();
  expect(
    (
      await page.request.post(
        `${path}/ideas/${project.context.ideas[0].id}/confirm`,
        { headers, data: { revision: project.revision } },
      )
    ).ok(),
  ).toBeTruthy();
  project = await idle();
  expect(
    (
      await page.request.post(path + "/stack/confirm", {
        headers,
        data: { revision: project.revision },
      })
    ).ok(),
  ).toBeTruthy();
  project = await idle();
  expect(project.state).toBe("ready");
  const diagrams: string[] = [];
  for (const file of [
    "../README.md",
    "../docs/ARCHITECTURE.md",
    "../docs/BYOK.md",
  ]) {
    const source = await readFile(resolve(file), "utf8");
    for (const match of source.matchAll(/```mermaid\r?\n([\s\S]*?)```/g))
      diagrams.push(match[1]);
  }
  expect(diagrams).toHaveLength(5);
  // Inject only an untrusted artifact at the HTTP boundary; the project and
  // workflow above are real. No renderer or diagram implementation is mocked.
  await page.route(`**${path}`, async (route) => {
    const response = await route.fetch();
    const body = await response.json();
    body.data.context.documents.files[0].content =
      [
        "# Render safety",
        "<script>window.markdownExecuted = true</script>",
        '<img src="https://tracking.invalid/html.png" onerror="window.markdownExecuted=true">',
        "![Tracking pixel](https://tracking.invalid/pixel.png)",
        "[Unsafe link](javascript:alert(1))",
        "```mermaid",
        "graph LR",
        "  A[Brief] --> B[Idea]",
        "```",
      ].join("\n\n") +
      diagrams.map((code) => `\n\n\`\`\`mermaid\n${code}\n\`\`\``).join("");
    body.data.context.documents.files[0].content +=
      "\n\n```mermaid\nthis is not a diagram\n```";
    await route.fulfill({ response, json: body });
  });
  await page.goto(`/projects/${id}/docs`);
  await expect(
    page.locator('.markdown-preview svg[id^="mermaid-"]'),
  ).toHaveCount(6);
  await expect(page.locator('.markdown-preview [role="alert"]')).toHaveCount(1);
  await expect(page.locator("body > svg")).toHaveCount(0);
  await expect(
    page.locator('.markdown-preview svg[id^="mermaid-"]').first(),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: /Open external image: Tracking pixel/ }),
  ).toBeVisible();
  await expect(
    page.locator('.markdown-preview a[href^="javascript:"]'),
  ).toHaveCount(0);
  await expect(
    page.locator(".markdown-preview script, .markdown-preview img"),
  ).toHaveCount(0);
  expect(await page.evaluate(() => "markdownExecuted" in window)).toBe(false);
  expect(tracking).toEqual([]);
  expect(errors).toEqual([]);
});

test("mobile intake is usable without horizontal page overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/projects/new");
  await expect(page.getByLabel("Your idea or challenge theme")).toBeVisible();
  const dimensions = await page.evaluate(() => ({
    width: document.documentElement.clientWidth,
    scroll: document.documentElement.scrollWidth,
  }));
  expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.width + 1);
  await page.screenshot({
    path: "test-results/mobile-intake.png",
    fullPage: true,
  });
});

test("an API outage is visible and cannot create a fake project", async ({
  page,
}) => {
  await page.route("**/api/v1/projects", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({
        success: false,
        error: { message: "The project service is unavailable." },
      }),
    }),
  );
  await page.goto("/projects");
  await expect(page.locator(".notice.error[role=alert]")).toContainText(
    "unavailable",
  );
  await expect(page.locator(".project-list-card")).toHaveCount(0);
});
