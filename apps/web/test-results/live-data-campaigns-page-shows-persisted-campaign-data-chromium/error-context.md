# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: live-data.spec.ts >> campaigns page shows persisted campaign data
- Location: tests\e2e\live-data.spec.ts:3:1

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.goto: net::ERR_ABORTED; maybe frame was detached?
Call log:
  - navigating to "http://localhost:3000/campaigns", waiting until "domcontentloaded"

```

# Test source

```ts
  1  | import { expect, test } from "@playwright/test";
  2  | 
  3  | test("campaigns page shows persisted campaign data", async ({ page }) => {
> 4  |   await page.goto("/campaigns", { waitUntil: "domcontentloaded" });
     |              ^ Error: page.goto: net::ERR_ABORTED; maybe frame was detached?
  5  |   console.log("campaigns url", page.url());
  6  |   await expect(page.getByText("Live Smoke Campaign")).toBeVisible();
  7  | });
  8  | 
  9  | test("council page shows persisted session data", async ({ page }) => {
  10 |   await page.goto("/council", { waitUntil: "domcontentloaded" });
  11 |   await expect(page.getByText("01KPB8VE4DE9XJEBNRYQ15J8TV")).toBeVisible();
  12 | });
  13 | 
  14 | test("muse page shows persisted conversation list", async ({ page }) => {
  15 |   await page.goto("/muse", { waitUntil: "domcontentloaded" });
  16 |   await expect(page.getByText("strategic")).toBeVisible();
  17 | });
  18 | 
  19 | test("content page shows persisted generated content", async ({ page }) => {
  20 |   await page.goto("/content", { waitUntil: "domcontentloaded" });
  21 |   await expect(page.getByRole("heading", { name: "Live Smoke Post" })).toBeVisible();
  22 | });
  23 | 
```