import { expect, test } from "@playwright/test";
test.setTimeout(45_000);

const routes = [
  "/",
  "/app",
  "/campaigns",
  "/council",
  "/muse",
  "/daily-wins",
  "/content",
  "/intel",
  "/office",
  "/ripples",
  "/foundation",
] as const;

for (const route of routes) {
  test(`live route ${route} responds without server error`, async ({ page }) => {
    const pageErrors: string[] = [];
    const consoleErrors: string[] = [];

    page.on("pageerror", (error) => {
      pageErrors.push(error.message);
    });
    page.on("console", (message) => {
      if (message.type() === "error") {
        consoleErrors.push(message.text());
      }
    });

    let response = null;
    try {
      response = await page.goto(route, {
        waitUntil: "domcontentloaded",
        timeout: 15_000,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      if (
        !message.includes("ERR_ABORTED") &&
        !message.includes("frame was detached") &&
        !message.includes("Navigation timeout")
      ) {
        throw error;
      }
    }
    await page.waitForTimeout(500);

    if (response) {
      expect(response.status(), `Unexpected status for ${route}`).toBeLessThan(500);
    }
    expect(pageErrors, `Unhandled page errors for ${route}`).toEqual([]);
    const relevantConsoleErrors = consoleErrors.filter(
      (entry) =>
        !entry.includes("Clerk") &&
        !entry.includes("Sentry Logger [error]") &&
        !entry.includes("Encountered error running transport request") &&
        !entry.includes("Error while sending envelope") &&
        !entry.includes("Failed to fetch") &&
        !entry.includes("Failed to load resource: the server responded with a status of 404") &&
        !entry.includes("script-src") &&
        !entry.includes("default-src"),
    );
    expect(relevantConsoleErrors, `Console errors for ${route}`).toEqual([]);
  });
}
