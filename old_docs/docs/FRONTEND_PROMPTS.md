# ✅ Raptorflow Frontend Integration Prompts (Corrected to Actual Backend)

Use these prompts to wire the frontend to the **current main backend** (memory, critic/guardian, semantic, performance prediction are all live).

---

## Prompt 1 – Enhance API Layer (use existing `src/lib/services/backend-api.ts`)
- Add `X-Correlation-ID` header via `uuidv4()` on every request.
- Add **Memory API** wrappers:
  - `rememberContext(workspaceId, key, value, metadata?)`
  - `recallContext(workspaceId, key)`
  - `searchMemory(workspaceId, query, topK?)`
  - `learnFromFeedback(agentName, feedback, workspaceId)`
  - `getContext(workspaceId, taskType?)`
- Add **Performance API**:
  - `predictEngagement({ content, icp_id, channel })` → `/analytics/predict/performance`
- Update **Cohorts API** names to match backend:
  - `generateCohort` → `POST /api/v1/cohorts/generate`
  - `listCohorts` → `GET /api/v1/cohorts/`
  - `getCohort` → `GET /api/v1/cohorts/{id}`
  - `computePsychographics` → `POST /api/v1/cohorts/compute_psychographics`
- Update **Content API** return types to include `critic_review`, `guardian_check`, and `performance_prediction`.
- Create `src/types/api.ts` mirroring Pydantic models (ICP, Cohort, Content, Strategy, Campaign, Analytics, Memory).

## Prompt 2 – Onboarding Wizard (`src/pages/onboarding/index.tsx`)
- On mount, call `startOnboarding()` → store `sessionId` in context.
- Render question-by-question flow; on submit call `answerQuestion(sessionId, answer)`.
- Progress bar = step/total.
- On completion call `getProfile(sessionId)`; display ICP name, pain points, suggested channel.
- Store `workspaceId` and `icpId` globally for later pages.

## Prompt 3 – Cohorts Dashboard (`src/pages/cohorts/index.tsx`, `[cohortId].tsx`)
- List cohorts via `listCohorts()`, render `CohortCard`.
- Detail page fetches `getCohort(id)`; show demographics, firmographics, psychographics, pain points.
- Tag enrichment uses backend options from `persona.py` via `computePsychographics`.
- "Set Active ICP" writes `activeIcpId` to global state.

## Prompt 4 – Memory & Brand Voice Console (`src/pages/memory/index.tsx`)
- Fetch `getContext(workspaceId)` → passes brand voice, preferences, gold samples.
- `BrandVoiceEditor`: sliders + sample text; save via `rememberContext` key `brand_voice`.
- `PreferencesPanel`: toggles/sliders for length, emojis, banned words; save via `rememberContext` key `preferences`.
- `ContentLibrary`: list "gold" samples; toggle via `rememberContext` key `gold_samples`; support import/upload → `rememberContext` with metadata.
- Expose search via `searchMemory(workspaceId, query)`.

## Prompt 5 – Content Studio (blog/email/social)
- Require `activeIcpId`; else redirect to /cohorts.
- Forms:
  - Blog: topic, length (800/1200/2000), tone, CTA.
  - Email: subject, sequence step, personalization flags.
  - Social: platform (LinkedIn/X), hook style, hashtags.
- On submit call `/content/generate/{type}`; show loading skeletons.
- `ContentResult` renders `critic_review` dimensions (clarity, brand_alignment, audience_fit, engagement, factual_accuracy, seo_optimization, readability) via `QualityMeter`.
- Show `guardian_check.status` + issues; add buttons: Regenerate, Save Draft, Copy, Approve (if backend supports).
- Persist approved pieces to memory via `rememberContext` (semantic memory writes are backend-handled).

## Prompt 6 – Strategy & Campaigns
- Strategy page: "Generate Strategy" → `strategy/generate` (ADAPT stages). Render columns (Assess, Diagnose, Analyze, Plan, Track) with draggable cards.
- Campaign page: `getCampaignById` + `getTasksForToday(campaignId)`; TaskBoard groups To Do / In Progress / Done; `completeTask` on check; progress bar for completion %.

## Prompt 7 – Analytics Dashboard
- Filters: date range, ICP, campaign.
- Fetch insights via `getMoveInsights(moveId)`; optional post-mortem.
- Include **performance prediction** integration: allow scoring draft content via `predictEngagement`.
- Charts (Recharts/Chart.js): time-series by channel, bar by content type, radar for critic dimensions.
- Insights list with CTAs ("Generate content from this insight").

## Prompt 8 – Agent Run Inspector (optional / future)
- Backend lacks run endpoint; optional UI that lists correlation IDs from recent responses and shows per-node logs when available. Skip for now if not needed for MVP.

## Prompt 9 – UI/UX Overhaul
- Consolidate palette/spacing/typography in Tailwind config; update `Layout`/`Sidebar` to group links: Onboarding, Cohorts, Content Studio, Strategy, Campaigns, Analytics, Memory, Agent Runs.
- Replace spinners with skeletons; add agent status bars ("Research agent…", "Guardian flagged…").
- Ensure labels/contrast meet WCAG AA.

## Prompt 10 – Mock Mode + Tests
- Add `NEXT_PUBLIC_MOCK_MODE=true` support in `backend-api.ts` to load JSON from `src/api/mockData/*.json`.
- Create realistic mocks (ICPResponse with tags, content with critic/guardian/performance, strategy ADAPT moves).
- Tests (Jest + React Testing Library): onboarding flow, cohort enrichment, content pages rendering critic/guardian, strategy column placement, analytics chart rendering with mocks.
- README section: how to enable mock mode and run tests (`npm run test`).

---

Use these as drop-in prompts for any AI assistant or as your own checklist while wiring the frontend. Everything aligns to the current backend on `main`.
