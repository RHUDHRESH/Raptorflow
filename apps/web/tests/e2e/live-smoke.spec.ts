import { expect, test } from "@playwright/test";

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

    const response = await page.goto(route, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(1500);

    expect(response, `No HTTP response for ${route}`).not.toBeNull();
    expect(response!.status(), `Unexpected status for ${route}`).toBeLessThan(500);
    expect(pageErrors, `Unhandled page errors for ${route}`).toEqual([]);
    const relevantConsoleErrors = consoleErrors.filter(
      (entry) =>
        !entry.includes("Clerk") &&
        !entry.includes("Failed to load resource: the server responded with a status of 404") &&
        !entry.includes("script-src") &&
        !entry.includes("default-src"),
    );
    expect(
      relevantConsoleErrors,
      `Console errors for ${route}`,
    ).toEqual([]);
  });
}
