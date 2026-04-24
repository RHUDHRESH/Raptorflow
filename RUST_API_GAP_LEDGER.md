# Rust API Gap Ledger

**Purpose:** Document routes that still use Prisma or need Rust equivalents but are NOT part of the current migration patch.

**Rules:**

- Routes with Rust equivalents MUST NOT have Prisma (enforced by `check-no-prisma-product-runtime.mjs`)
- Routes without Rust equivalents are documented here as gaps
- Do NOT implement all gaps in one patch — handle bucket by bucket in follow-up patches

---

## Gap Summary

| Category   | Route                                          | Status                                    | Risk       |
| ---------- | ---------------------------------------------- | ----------------------------------------- | ---------- |
| Auth       | `auth/forgot-password`                         | Gap                                       | Low        |
| Auth       | `auth/reset-password`                          | Gap                                       | Low        |
| Avatars    | `avatars`                                      | Gap                                       | Medium     |
| Dashboard  | `dashboard`                                    | Gap                                       | Medium     |
| Foundation | `foundation/scan/quick`                        | Gap                                       | Medium     |
| Campaign   | `campaigns/[id]/evaluate`                      | **Implemented + Red-teamed**              | ~~Medium~~ |
| Campaign   | `campaigns/[id]/moves/generate`                | **Implemented + Red-teamed**              | ~~High~~   |
| Campaign   | `campaigns/[id]/moves/[moveId]/tasks/[taskId]` | Gap                                       | Low        |
| Council    | `council/[sessionId]/start`                    | **Implemented + Red-teamed + Tombstoned** | ~~High~~   |
| Council    | `council/[sessionId]/stream`                   | **Implemented + Red-teamed + Tombstoned** | ~~High~~   |
| Council    | `council/[sessionId]/synthesize`               | **Implemented + Red-teamed + Tombstoned** | ~~High~~   |
| Daily-wins | `daily-wins/cron`                              | Gap                                       | Low        |
| Intel      | `intel/[signalId]`                             | Gap                                       | Low        |
| Intel      | `intel/brief/cron`                             | Gap                                       | Medium     |
| Intel      | `intel/competitors`                            | Gap                                       | High       |
| Nudges     | `nudges/cron`                                  | Gap                                       | Low        |
| PRL        | `prl/decay/cron`                               | Gap                                       | Low        |

---

## Detailed Gap Analysis

### 1. Auth/Account Flows

| Next Route             | Current Behavior                                      | Why No Rust Equivalent                        | Risk |
| ---------------------- | ----------------------------------------------------- | --------------------------------------------- | ---- |
| `auth/forgot-password` | Sends password reset email via Prisma + email service | Clerk handles auth; this is custom email flow | Low  |
| `auth/reset-password`  | Updates password in Prisma after reset                | Clerk handles auth; this is custom flow       | Low  |

**Recommended Patch Bucket:** Auth/account cleanup

### 2. Avatars

| Next Route | Current Behavior                       | Why No Rust Equivalent | Risk   |
| ---------- | -------------------------------------- | ---------------------- | ------ |
| `avatars`  | CRUD for council avatar configurations | No Rust equivalent yet | Medium |

**Recommended Patch Bucket:** Avatars Rust migration

### 3. Dashboard/Office Summary

| Next Route  | Current Behavior                              | Why No Rust Equivalent | Risk   |
| ----------- | --------------------------------------------- | ---------------------- | ------ |
| `dashboard` | Aggregates office state from multiple sources | No Rust equivalent yet | Medium |

**Recommended Patch Bucket:** Dashboard Rust migration

### 4. Foundation Scan Legacy

| Next Route              | Current Behavior           | Why No Rust Equivalent                                             | Risk   |
| ----------------------- | -------------------------- | ------------------------------------------------------------------ | ------ |
| `foundation/scan/quick` | Runs quick scan via Prisma | Rust has `POST /foundation/scan/quick` but this route is different | Medium |

**Recommended Patch Bucket:** Foundation scan consolidation

### 5. Campaign Sub-Routes

| Next Route                                     | Current Behavior                | Why No Rust Equivalent                                   | Proposed Rust Route                   | Risk     |
| ---------------------------------------------- | ------------------------------- | -------------------------------------------------------- | ------------------------------------- | -------- |
| `campaigns/[id]/evaluate`                      | AI evaluation of campaign brief | **IMPLEMENTED** - Rust endpoint exists with validation   | `POST /campaigns/{id}/evaluate`       | ~~High~~ |
| `campaigns/[id]/moves/generate`                | AI generation of move ladder    | **IMPLEMENTED** - Rust endpoint exists with validation   | `POST /campaigns/{id}/moves/generate` | ~~High~~ |
| `campaigns/[id]/moves/[moveId]/tasks/[taskId]` | PATCH task status               | Rust uses `PATCH /campaigns/{id}/tasks/{task_id}/status` | Rename to match Rust                  | Low      |

**Recommended Patch Bucket:** ~~Campaign AI features~~ - NOW DONE (see red-team patch)

### 6. Council Sub-Routes

| Next Route                       | Current Behavior                   | Why No Rust Equivalent                                     | Proposed Rust Route             | Risk     |
| -------------------------------- | ---------------------------------- | ---------------------------------------------------------- | ------------------------------- | -------- |
| `council/[sessionId]/start`      | Triggers async position generation | **IMPLEMENTED** - Rust endpoint exists                     | `POST /council/{id}/start`      | ~~High~~ |
| `council/[sessionId]/stream`     | SSE stream for council progress    | **IMPLEMENTED** - SSE endpoint exists (see red-team notes) | `GET /council/{id}/stream`      | ~~High~~ |
| `council/[sessionId]/synthesize` | Triggers async synthesis           | **IMPLEMENTED** - Rust endpoint exists                     | `POST /council/{id}/synthesize` | ~~High~~ |

**Recommended Patch Bucket:** ~~Council streaming~~ - NOW DONE (see red-team patch)

### 7. Daily-Wins Cron

| Next Route        | Current Behavior                          | Why No Rust Equivalent             | Risk |
| ----------------- | ----------------------------------------- | ---------------------------------- | ---- |
| `daily-wins/cron` | Generates daily wins for all active users | Internal cron, not user-facing API | Low  |

**Recommended Patch Bucket:** Cron job migration

### 8. Intel Sub-Routes

| Next Route          | Current Behavior                          | Why No Rust Equivalent       | Proposed Rust Route               | Risk   |
| ------------------- | ----------------------------------------- | ---------------------------- | --------------------------------- | ------ |
| `intel/[signalId]`  | GET/PATCH intel signal                    | Rust doesn't have this route | `GET/PATCH /intel/signals/{id}`   | Low    |
| `intel/brief/cron`  | Generates intel briefs for all users      | Internal cron                | `POST /intel/brief/generate`      | Medium |
| `intel/competitors` | GET competitor snapshots, POST to analyze | Complex AI + scraping logic  | `POST /intel/competitors/analyze` | High   |

**Recommended Patch Bucket:** Intel analysis features

### 9. Nudges Cron

| Next Route    | Current Behavior                      | Why No Rust Equivalent         | Risk |
| ------------- | ------------------------------------- | ------------------------------ | ---- |
| `nudges/cron` | Generates nudges for all active users | Internal cron, not user-facing | Low  |

**Recommended Patch Bucket:** Cron job migration

### 10. PRL Cron

| Next Route       | Current Behavior               | Why No Rust Equivalent | Risk |
| ---------------- | ------------------------------ | ---------------------- | ---- |
| `prl/decay/cron` | Runs decay on all user ripples | Internal cron          | Low  |

**Recommended Patch Bucket:** Cron job migration

---

## Implementation Priority

### DONE (High Risk - Completed)

1. ~~**Council streaming**~~ - `POST /council/{id}/start`, `GET /stream`, `POST /synthesize` - **IMPLEMENTED + RED-TEAMED**
2. ~~**Campaign AI features**~~ - `POST /campaigns/{id}/evaluate`, `POST /moves/generate` - **IMPLEMENTED + RED-TEAMED**

### Medium Risk (Remaining)

3. **Avatars** - Needed for Council to work properly
4. **Dashboard** - Office summary endpoint
5. **Intel competitors** - Competitor analysis feature
6. **Intel brief cron** - Internal cron job

### Low Risk (Remaining)

7. **Auth flows** - Using Clerk, low risk
8. **Foundation scan** - Minor route difference
9. **Task PATCH** - Simple route rename
10. **Cron jobs** - Internal, not user-facing

---

## Notes

- Gap routes that are cron jobs (`daily-wins/cron`, `nudges/cron`, `prl/decay/cron`, `intel/brief/cron`) should be handled separately as infrastructure/ops patches
- ~~Campaign evaluate and generate moves are AI-heavy features that may need significant Rust/Bedrock integration work~~ - **NOW IMPLEMENTED**
- ~~Council streaming requires SSE support which may need async job infrastructure in Rust~~ - **NOW IMPLEMENTED (see AI_RUNTIME_REDTEAM_REPORT.md for SSE auth notes)**
- See `AI_RUNTIME_REDTEAM_REPORT.md` for security hardening details on implemented AI endpoints
