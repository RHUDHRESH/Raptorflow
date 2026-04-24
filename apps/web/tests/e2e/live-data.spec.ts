import { expect, test } from "@playwright/test";

test("campaigns page shows persisted campaign data", async ({ page }) => {
  await page.goto("/campaigns", { waitUntil: "domcontentloaded" });
  console.log("campaigns url", page.url());
  await expect(page.getByText("Live Smoke Campaign")).toBeVisible();
});

test("council page shows persisted session data", async ({ page }) => {
  await page.goto("/council", { waitUntil: "domcontentloaded" });
  await expect(page.getByText("01KPB8VE4DE9XJEBNRYQ15J8TV")).toBeVisible();
});

test("muse page shows persisted conversation list", async ({ page }) => {
  await page.goto("/muse", { waitUntil: "domcontentloaded" });
  await expect(page.getByText("strategic")).toBeVisible();
});

test("content page shows persisted generated content", async ({ page }) => {
  await page.goto("/content", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "Live Smoke Post" })).toBeVisible();
});
