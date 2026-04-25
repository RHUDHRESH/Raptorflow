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
| Avatars    | `avatars`                                      | **Implemented + Tombstoned**              | ~~Medium~~ |
| Dashboard  | `dashboard`                                    | **Implemented + Tombstoned** (→ Office)   | ~~Medium~~ |
| Foundation | `foundation/scan/quick`                        | **Implemented + Tombstoned**              | ~~Medium~~ |
| Campaign   | `campaigns/[id]/evaluate`                      | **Implemented + Red-teamed**              | ~~Medium~~ |
| Campaign   | `campaigns/[id]/moves/generate`                | **Implemented + Red-teamed**              | ~~High~~   |
| Campaign   | `campaigns/[id]/moves/[moveId]/tasks/[taskId]` | Gap                                       | Low        |
| Council    | `council/[sessionId]/start`                    | **Implemented + Red-teamed + Tombstoned** | ~~High~~   |
| Council    | `council/[sessionId]/stream`                   | **Implemented + Red-teamed + Tombstoned** | ~~High~~   |
| Council    | `council/[sessionId]/synthesize`               | **Implemented + Red-teamed + Tombstoned** | ~~High~~   |
| Daily-wins | `daily-wins/cron`                              | Gap                                       | Low        |
| Intel      | `intel/[signalId]`                             | **Implemented + Tombstoned**              | ~~Low~~    |
| Intel      | `intel/brief/cron`                             | Gap                                       | Medium     |
| Intel      | `intel/competitors`                            | **Implemented + Tombstoned**              | ~~High~~   |
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

| Next Route | Current Behavior                       | Status                                               | Risk       |
| ---------- | -------------------------------------- | ---------------------------------------------------- | ---------- |
| `avatars`  | CRUD for council avatar configurations | **IMPLEMENTED** - Rust endpoint at `/api/v1/avatars` | ~~Medium~~ |

**Recommended Patch Bucket:** ~~Avatars Rust migration~~ - NOW DONE (see AVATAR_OFFICE_HARNESS_SPINE_REPORT.md)

### 3. Dashboard/Office Summary

| Next Route  | Current Behavior                              | Status                                                   | Risk       |
| ----------- | --------------------------------------------- | -------------------------------------------------------- | ---------- |
| `dashboard` | Aggregates office state from multiple sources | **IMPLEMENTED** - Office aggregation at `/api/v1/office` | ~~Medium~~ |

**Recommended Patch Bucket:** ~~Dashboard Rust migration~~ - NOW DONE (see AVATAR_OFFICE_HARNESS_SPINE_REPORT.md)

### 4. Foundation Scan Legacy

| Next Route              | Current Behavior           | Why No Rust Equivalent                                   | Risk       |
| ----------------------- | -------------------------- | -------------------------------------------------------- | ---------- |
| `foundation/scan/quick` | Runs quick scan via Prisma | **IMPLEMENTED** - Rust has `POST /foundation/scan/quick` | ~~Medium~~ |

**Recommended Patch Bucket:** ~~Foundation scan consolidation~~ - NOW DONE (see FOUNDATION_INTEL_CONTEXT_SPINE_REPORT.md)

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

| Next Route          | Current Behavior                          | Why No Rust Equivalent | Proposed Rust Route             | Risk     |
| ------------------- | ----------------------------------------- | ---------------------- | ------------------------------- | -------- |
| `intel/[signalId]`  | GET/PATCH intel signal                    | **IMPLEMENTED**        | `GET/PATCH /intel/signals/{id}` | ~~Low~~  |
| `intel/brief/cron`  | Generates intel briefs for all users      | Internal cron          | `POST /intel/brief/generate`    | Medium   |
| `intel/competitors` | GET competitor snapshots, POST to analyze | **IMPLEMENTED**        | `GET/POST /intel/competitors`   | ~~High~~ |

**Recommended Patch Bucket:** ~~Intel analysis features~~ - NOW DONE (see FOUNDATION_INTEL_CONTEXT_SPINE_REPORT.md)

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
3. ~~**Foundation scan consolidation**~~ - `POST /foundation/scan/quick`, `POST /foundation/scan/deep`, `GET /foundation/scan/{id}` - **IMPLEMENTED + TOMBSTONED**
4. ~~**Intel signals**~~ - `GET /intel/signals`, `GET/PATCH /intel/signals/{id}` - **IMPLEMENTED + TOMBSTONED**
5. ~~**Intel competitors**~~ - `GET/POST /intel/competitors` - **IMPLEMENTED + TOMBSTONED**
6. ~~**Avatars**~~ - `GET/POST/PATCH/DELETE /api/v1/avatars`, `POST /avatars/defaults` - **IMPLEMENTED + TOMBSTONED**
7. ~~**Dashboard**~~ - Merged into Office aggregation (`GET /api/v1/office`) - **IMPLEMENTED + TOMBSTONED**

### Medium Risk (Remaining)

8. **Harness ledger/scaffold** - Ledger implemented; full execution pending (see AVATAR_OFFICE_HARNESS_SPINE_REPORT.md)
9. **Intel brief cron** - Internal cron job

### Low Risk (Remaining)

9. **Auth flows** - Using Clerk, low risk
10. **Task PATCH** - Simple route rename
11. **Cron jobs** - Internal, not user-facing

---

## Notes

- Gap routes that are cron jobs (`daily-wins/cron`, `nudges/cron`, `prl/decay/cron`, `intel/brief/cron`) should be handled separately as infrastructure/ops patches
- ~~Campaign evaluate and generate moves are AI-heavy features that may need significant Rust/Bedrock integration work~~ - **NOW IMPLEMENTED**
- ~~Council streaming requires SSE support which may need async job infrastructure in Rust~~ - **NOW IMPLEMENTED (see AI_RUNTIME_REDTEAM_REPORT.md for SSE auth notes)**
- See `AI_RUNTIME_REDTEAM_REPORT.md` for security hardening details on implemented AI endpoints
