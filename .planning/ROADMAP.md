# Roadmap: RaptorFlow

**Project:** RaptorFlow - Marketing Intelligence & Campaign Orchestration
**Created:** 2026-04-11
**Granularity:** Fine (natural boundaries)

## Core Value

Organizations can launch data-driven marketing campaigns faster by leveraging AI agent councils that debate and synthesize strategy, with real-time visualization through an interactive office canvas where AI avatars represent different strategic perspectives.

## Phases

- [ ] **Phase 1: Auth & Foundation** - Multi-tenant auth, tenant isolation, foundation data management, PRL core
- [ ] **Phase 2: Campaign Core** - Campaign CRUD, moves, tasks, content generation pipeline
- [ ] **Phase 3: Intelligence** - Competitor tracking, SEO/ad monitoring, Daily Wins briefings
- [ ] **Phase 4: AI Communication** - Multi-agent council debates, Muse conversational AI
- [ ] **Phase 5: Real-Time Office** - PixiJS canvas, WebSocket broadcasting, council visualization
- [ ] **Phase 6: Billing** - PhonePe subscription, payment processing

## Phase Details

### Phase 1: Auth & Foundation

**Goal:** Users can securely authenticate and manage foundation data with tenant isolation

**Depends on:** Nothing (first phase)

**Requirements:** AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05, AUTH-06, FOUND-01, FOUND-02, FOUND-03, FOUND-04, FOUND-05, PRL-01, PRL-02, PRL-03, PRL-04

**Success Criteria** (what must be TRUE):

1. User can sign up with email/password and receive email verification
2. User can reset forgotten password via email link
3. User session persists across browser refresh without re-login
4. Multi-tenant isolation via Clerk JWT org_id extraction works correctly
5. Row-Level Security enforces tenant data isolation on all queries
6. User can create organization and complete 21-screen foundation onboarding
7. Foundation data is versioned with snapshots user can view/restore
8. User can trigger foundation scan (quick/deep modes) and see results
9. Foundation sections can be edited and re-injected into campaigns
10. Ripples can be created, tracked, and connected via edges
11. Agent essences persist across sessions
12. PRL decay policies apply correctly

**Plans:** 3 plans

**Plan list:**

- [ ] 01-01-PLAN.md — Auth & Multi-Tenant Foundation (Clerk, JWT, RLS, webhooks)
- [ ] 01-02-PLAN.md — Foundation Data Management (21-screen onboarding, snapshots, scan)
- [ ] 01-03-PLAN.md — PRL Core (Ripples, edges, agent essences, decay)

**UI hint:** yes

### Phase 2: Campaign Core

**Goal:** Users can create, manage campaigns with moves/tasks, and generate content

**Depends on:** Phase 1

**Requirements:** CAMP-01, CAMP-02, CAMP-03, CAMP-04, CAMP-05, CAMP-06, CAMP-07, CONT-01, CONT-02, CONT-03

**Success Criteria** (what must be TRUE):

1. User can create campaign with brief and see it in campaign list
2. User can view full campaign details including timeline and status
3. User can update campaign status (draft → active → paused → completed)
4. User can create moves within campaign and reorder them
5. User can create tasks within moves and assign them
6. User can trigger content generation for tasks and receive generated content
7. User can initiate campaign replan session that resets appropriate state
8. File uploads to S3 complete successfully
9. Content pregeneration jobs queue and process via SQS
10. Embedding jobs process asynchronously without blocking user requests

**Plans:** TBD

**UI hint:** yes

### Phase 3: Intelligence

**Goal:** Users can track competitors and receive AI-generated briefings

**Depends on:** Phase 1 (foundation data)

**Requirements:** INTEL-01, INTEL-02, INTEL-03, INTEL-04, INTEL-05

**Success Criteria** (what must be TRUE):

1. User can capture and store competitor snapshots
2. User can add/tracked SEO rankings over time
3. User can track competitor ad library entries
4. System generates intelligence alerts when significant changes detected
5. User receives Daily Wins briefing with relevant insights

**Plans:** TBD

**UI hint:** yes

### Phase 4: AI Communication

**Goal:** Users can leverage multi-agent councils and conversational AI for strategy

**Depends on:** Phase 1 (PRL), Phase 2 (campaigns)

**Requirements:** COUNC-01, COUNC-02, COUNC-03, COUNC-04, COUNC-05, MUSE-01, MUSE-02, MUSE-03, MUSE-04

**Success Criteria** (what must be TRUE):

1. User can start council session for any campaign
2. Multiple AI agents (3-5) participate and debate different positions
3. Council session progress streams to user via WebSocket in real-time
4. Council produces synthesis summarizing debate outcomes
5. Agent positions are tracked and persisted for audit/review
6. User can start Muse conversational session
7. AI responds contextually using foundation and campaign data
8. Conversation history persists across sessions
9. Route-based conversation handling directs queries appropriately

**Plans:** TBD

**UI hint:** yes

### Phase 5: Real-Time Office

**Goal:** Users can visualize AI agent collaboration on interactive office canvas

**Depends on:** Phase 1 (PRL), Phase 4 (council)

**Requirements:** OFFICE-01, OFFICE-02, OFFICE-03, OFFICE-04, OFFICE-05

**Success Criteria** (what must be TRUE):

1. Office canvas renders via PixiJS with smooth 60fps animation
2. WebSocket broadcasts agent movements to all connected clients
3. Agent walk events display as animated movement on canvas
4. Speech bubbles appear for agent dialogue during council
5. Council debates visualize in real-time on office canvas

**Plans:** TBD

**UI hint:** yes

### Phase 6: Billing

**Goal:** Users can subscribe to plans and make payments

**Depends on:** Phase 1 (auth)

**Requirements:** BILL-01, BILL-02, BILL-03

**Success Criteria** (what must be TRUE):

1. User can view available plans and select one
2. User can complete PhonePe payment flow for subscription
3. Payment events process correctly and update subscription status
4. Subscription status reflects current plan and billing cycle

**Plans:** TBD

**UI hint:** yes

## Progress Table

| Phase                | Plans Complete | Status      | Completed |
| -------------------- | -------------- | ----------- | --------- |
| 1. Auth & Foundation | 3/3            | Planned     | -         |
| 2. Campaign Core     | 0/10           | Not started | -         |
| 3. Intelligence      | 0/5            | Not started | -         |
| 4. AI Communication  | 0/9            | Not started | -         |
| 5. Real-Time Office  | 0/5            | Not started | -         |
| 6. Billing           | 0/4            | Not started | -         |

---

_Roadmap created: 2026-04-11_
