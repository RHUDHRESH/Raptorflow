# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: live-data.spec.ts >> campaigns page shows persisted campaign data
- Location: tests\e2e\live-data.spec.ts:3:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText('Live Smoke Campaign')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByText('Live Smoke Campaign')

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - banner [ref=e2]:
    - generic [ref=e3]:
      - link "RAPTORFLOW" [ref=e4] [cursor=pointer]:
        - /url: /
      - button "Open user menu" [ref=e7] [cursor=pointer]:
        - img "Live Smoke's logo" [ref=e10]
  - generic [ref=e12]:
    - complementary [ref=e13]:
      - generic [ref=e14]:
        - generic [ref=e15]:
          - img [ref=e17]
          - generic [ref=e19]:
            - generic [ref=e20]: RaptorFlow
            - generic [ref=e21]: EST. 1989
        - button [ref=e22]:
          - img [ref=e23]
      - navigation [ref=e25]:
        - generic [ref=e26]:
          - heading "Workspace" [level=2] [ref=e27]
          - generic [ref=e28]:
            - link "Dashboard" [ref=e29] [cursor=pointer]:
              - /url: /app/dashboard
              - img [ref=e30]
              - generic [ref=e32]: Dashboard
            - link "The Office" [ref=e33] [cursor=pointer]:
              - /url: /office
              - img [ref=e34]
              - generic [ref=e36]: The Office
            - link "Daily Wins" [ref=e37] [cursor=pointer]:
              - /url: /daily-wins
              - img [ref=e38]
              - generic [ref=e40]: Daily Wins
            - link "Uploads" [ref=e41] [cursor=pointer]:
              - /url: /uploads
              - img [ref=e42]
              - generic [ref=e44]: Uploads
        - generic [ref=e45]:
          - heading "Intelligence" [level=2] [ref=e46]
          - generic [ref=e47]:
            - link "Intel" [ref=e48] [cursor=pointer]:
              - /url: /intel
              - img [ref=e49]
              - generic [ref=e51]: Intel
            - link "Nudges" [ref=e52] [cursor=pointer]:
              - /url: /nudges
              - img [ref=e53]
              - generic [ref=e55]: Nudges
            - link "Ripples" [ref=e56] [cursor=pointer]:
              - /url: /ripples
              - img [ref=e57]
              - generic [ref=e59]: Ripples
        - generic [ref=e60]:
          - heading "Strategy" [level=2] [ref=e61]
          - generic [ref=e62]:
            - link "Campaigns" [ref=e63] [cursor=pointer]:
              - /url: /campaigns
              - img [ref=e65]
              - generic [ref=e67]: Campaigns
            - link "Council" [ref=e69] [cursor=pointer]:
              - /url: /council
              - img [ref=e70]
              - generic [ref=e72]: Council
            - link "Muse" [ref=e73] [cursor=pointer]:
              - /url: /muse
              - img [ref=e74]
              - generic [ref=e76]: Muse
            - link "Content" [ref=e77] [cursor=pointer]:
              - /url: /content
              - img [ref=e78]
              - generic [ref=e80]: Content
        - generic [ref=e81]:
          - heading "System" [level=2] [ref=e82]
          - generic [ref=e83]:
            - link "Foundation" [ref=e84] [cursor=pointer]:
              - /url: /foundation
              - img [ref=e85]
              - generic [ref=e87]: Foundation
            - link "Settings" [ref=e88] [cursor=pointer]:
              - /url: /settings
              - img [ref=e89]
              - generic [ref=e91]: Settings
      - generic [ref=e92]:
        - paragraph [ref=e95]: "UPLINK: ACTIVE"
        - paragraph [ref=e96]: "ORG: org_3ClZOP8E"
      - generic [ref=e97]:
        - generic [ref=e98]:
          - generic [ref=e99]: Passive_HQ_View
          - generic [ref=e100]: 21 agents
        - generic [ref=e101]:
          - generic [ref=e102]: RECEPTIO
          - generic [ref=e103]: STRATEGI
          - generic [ref=e104]: THE COUN
          - generic [ref=e105]: CONTENT
          - generic [ref=e106]: INTEL LA
          - generic [ref=e107]: RESEARCH
          - generic [ref=e108]: SERVER R
    - main [ref=e109]:
      - generic [ref=e111]:
        - generic [ref=e112]:
          - generic [ref=e113]:
            - paragraph [ref=e114]: Strategy Ledger
            - heading "Campaigns" [level=1] [ref=e115]
          - button "Initiate Campaign" [ref=e116] [cursor=pointer]:
            - img [ref=e117]
            - text: Initiate Campaign
        - generic [ref=e119]:
          - generic [ref=e120]:
            - paragraph [ref=e121]: Active Fronts
            - generic [ref=e122]: ...
          - generic [ref=e123]:
            - paragraph [ref=e124]: Completed Initiatives
            - generic [ref=e125]: ...
          - generic [ref=e126]:
            - paragraph [ref=e127]: Total Briefs
            - generic [ref=e128]: ...
        - paragraph [ref=e131]: Campaign Log
        - generic [ref=e136]:
          - generic [ref=e137]:
            - img [ref=e139]
            - generic [ref=e141]:
              - paragraph [ref=e142]: Ready for deployment?
              - paragraph [ref=e143]: Strategist 01 is standing by for new instructions.
          - button "Open Deployment Interface" [ref=e144]
  - button "Open Next.js Dev Tools" [ref=e150] [cursor=pointer]:
    - img [ref=e151]
  - alert [ref=e154]
```

# Test source

```ts
  1  | import { expect, test } from "@playwright/test";
  2  | 
  3  | test("campaigns page shows persisted campaign data", async ({ page }) => {
  4  |   await page.goto("/campaigns", { waitUntil: "domcontentloaded" });
  5  |   console.log("campaigns url", page.url());
> 6  |   await expect(page.getByText("Live Smoke Campaign")).toBeVisible();
     |                                                       ^ Error: expect(locator).toBeVisible() failed
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