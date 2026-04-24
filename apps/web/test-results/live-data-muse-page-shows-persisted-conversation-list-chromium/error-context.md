# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: live-data.spec.ts >> muse page shows persisted conversation list
- Location: tests\e2e\live-data.spec.ts:14:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText('strategic')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByText('strategic')

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - banner [ref=e2]:
    - link "RAPTORFLOW" [ref=e4] [cursor=pointer]:
      - /url: /
  - generic [ref=e5]:
    - complementary [ref=e6]:
      - generic [ref=e7]:
        - generic [ref=e8]:
          - img [ref=e10]
          - generic [ref=e12]:
            - generic [ref=e13]: RaptorFlow
            - generic [ref=e14]: EST. 1989
        - button [ref=e15]:
          - img [ref=e16]
      - navigation [ref=e18]:
        - generic [ref=e19]:
          - heading "Workspace" [level=2] [ref=e20]
          - generic [ref=e21]:
            - link "Dashboard" [ref=e22] [cursor=pointer]:
              - /url: /app/dashboard
              - img [ref=e23]
              - generic [ref=e25]: Dashboard
            - link "The Office" [ref=e26] [cursor=pointer]:
              - /url: /office
              - img [ref=e27]
              - generic [ref=e29]: The Office
            - link "Daily Wins" [ref=e30] [cursor=pointer]:
              - /url: /daily-wins
              - img [ref=e31]
              - generic [ref=e33]: Daily Wins
            - link "Uploads" [ref=e34] [cursor=pointer]:
              - /url: /uploads
              - img [ref=e35]
              - generic [ref=e37]: Uploads
        - generic [ref=e38]:
          - heading "Intelligence" [level=2] [ref=e39]
          - generic [ref=e40]:
            - link "Intel" [ref=e41] [cursor=pointer]:
              - /url: /intel
              - img [ref=e42]
              - generic [ref=e44]: Intel
            - link "Nudges" [ref=e45] [cursor=pointer]:
              - /url: /nudges
              - img [ref=e46]
              - generic [ref=e48]: Nudges
            - link "Ripples" [ref=e49] [cursor=pointer]:
              - /url: /ripples
              - img [ref=e50]
              - generic [ref=e52]: Ripples
        - generic [ref=e53]:
          - heading "Strategy" [level=2] [ref=e54]
          - generic [ref=e55]:
            - link "Campaigns" [ref=e56] [cursor=pointer]:
              - /url: /campaigns
              - img [ref=e57]
              - generic [ref=e59]: Campaigns
            - link "Council" [ref=e60] [cursor=pointer]:
              - /url: /council
              - img [ref=e61]
              - generic [ref=e63]: Council
            - link "Muse" [ref=e64] [cursor=pointer]:
              - /url: /muse
              - img [ref=e66]
              - generic [ref=e68]: Muse
            - link "Content" [ref=e70] [cursor=pointer]:
              - /url: /content
              - img [ref=e71]
              - generic [ref=e73]: Content
        - generic [ref=e74]:
          - heading "System" [level=2] [ref=e75]
          - generic [ref=e76]:
            - link "Foundation" [ref=e77] [cursor=pointer]:
              - /url: /foundation
              - img [ref=e78]
              - generic [ref=e80]: Foundation
            - link "Settings" [ref=e81] [cursor=pointer]:
              - /url: /settings
              - img [ref=e82]
              - generic [ref=e84]: Settings
      - generic [ref=e85]:
        - paragraph [ref=e88]: "UPLINK: ACTIVE"
        - paragraph [ref=e89]: "ORG: org_3ClZOP8E"
      - generic [ref=e90]:
        - generic [ref=e91]:
          - generic [ref=e92]: Passive_HQ_View
          - generic [ref=e93]: 21 agents
        - generic [ref=e94]:
          - generic [ref=e95]: RECEPTIO
          - generic [ref=e96]: STRATEGI
          - generic [ref=e97]: THE COUN
          - generic [ref=e98]: CONTENT
          - generic [ref=e99]: INTEL LA
          - generic [ref=e100]: RESEARCH
          - generic [ref=e101]: SERVER R
    - main [ref=e102]:
      - generic [ref=e103]:
        - complementary [ref=e104]:
          - button "New Conversation" [ref=e106] [cursor=pointer]:
            - img [ref=e107]
            - text: New Conversation
          - generic [ref=e109]: Conversations
        - main [ref=e114]:
          - generic [ref=e115]:
            - generic [ref=e116]:
              - img [ref=e117]
              - generic [ref=e119]: Muse
            - generic [ref=e120]: RaptorFlow AI
          - generic [ref=e123]:
            - img [ref=e125]
            - generic [ref=e127]:
              - heading "What can Muse help you with?" [level=1] [ref=e128]
              - paragraph [ref=e129]: Select a conversation or start something new
            - generic [ref=e130]:
              - button "Write me 3 subject lines for a re-engagement email" [ref=e131]
              - button "What should our content strategy focus on this quarter?" [ref=e132]
              - button "Should we launch a podcast?" [ref=e133]
              - button "How do I improve our positioning?" [ref=e134]
          - generic [ref=e135]:
            - generic [ref=e136]:
              - textbox "Ask Muse… (Enter to send, Shift+Enter for newline)" [disabled] [ref=e137]
              - button [disabled]:
                - img
            - paragraph [ref=e138]: Select or create a conversation to start chatting
  - button "Open Next.js Dev Tools" [ref=e144] [cursor=pointer]:
    - img [ref=e145]
  - alert [ref=e148]
```

# Test source

```ts
  1  | import { expect, test } from "@playwright/test";
  2  | 
  3  | test("campaigns page shows persisted campaign data", async ({ page }) => {
  4  |   await page.goto("/campaigns", { waitUntil: "domcontentloaded" });
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
> 16 |   await expect(page.getByText("strategic")).toBeVisible();
     |                                             ^ Error: expect(locator).toBeVisible() failed
  17 | });
  18 | 
  19 | test("content page shows persisted generated content", async ({ page }) => {
  20 |   await page.goto("/content", { waitUntil: "domcontentloaded" });
  21 |   await expect(page.getByRole("heading", { name: "Live Smoke Post" })).toBeVisible();
  22 | });
  23 | 
```