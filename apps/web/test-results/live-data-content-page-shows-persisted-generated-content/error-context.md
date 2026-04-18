# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: live-data.spec.ts >> content page shows persisted generated content
- Location: tests\e2e\live-data.spec.ts:18:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText('Live Smoke Post')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByText('Live Smoke Post')

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e3]:
    - generic [ref=e4]:
      - heading "404" [level=1] [ref=e5]
      - heading "Page not found" [level=2] [ref=e6]
    - img "Error page illustration" [ref=e8]
  - alert [ref=e9]
```

# Test source

```ts
  1  | import { expect, test } from "@playwright/test";
  2  | 
  3  | test("campaigns page shows persisted campaign data", async ({ page }) => {
  4  |   await page.goto("/campaigns", { waitUntil: "domcontentloaded" });
  5  |   await expect(page.getByText("Live Smoke Campaign")).toBeVisible();
  6  | });
  7  | 
  8  | test("council page shows persisted session data", async ({ page }) => {
  9  |   await page.goto("/council", { waitUntil: "domcontentloaded" });
  10 |   await expect(page.getByText("01KPB8VE4DE9XJEBNRYQ15J8TV")).toBeVisible();
  11 | });
  12 | 
  13 | test("muse page shows persisted conversation list", async ({ page }) => {
  14 |   await page.goto("/muse", { waitUntil: "domcontentloaded" });
  15 |   await expect(page.getByText("strategic")).toBeVisible();
  16 | });
  17 | 
  18 | test("content page shows persisted generated content", async ({ page }) => {
  19 |   await page.goto("/content", { waitUntil: "domcontentloaded" });
> 20 |   await expect(page.getByText("Live Smoke Post")).toBeVisible();
     |                                                   ^ Error: expect(locator).toBeVisible() failed
  21 | });
  22 | 
```