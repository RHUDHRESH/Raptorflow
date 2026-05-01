# Avatar + Office + Harness Spine Report

**Branch:** `fix/avatar-office-harness-spine`
**Base:** `main`
**Status:** COMPLETED ✅

---

## 0. Baseline Checks

| Check                          | Result                  |
| ------------------------------ | ----------------------- |
| `pnpm structural:check`        | ✅ PASS                 |
| `pnpm route-parity:check`      | ✅ PASS                 |
| `pnpm runtime-authority:check` | ✅ PASS                 |
| `pnpm typecheck`               | ✅ PASS                 |
| `cargo check --workspace`      | ✅ PASS                 |
| `cargo clippy --lib --bins`    | ✅ PASS (warnings only) |

---

## 1. Branch

- Branch: `fix/avatar-office-harness-spine`
- Base: `main`
- From PR #209 (already merged)

---

## 2. Files Changed

### Database

- `database/migrations/0021_avatars_harness.sql` — **NEW** — `avatars`, `harness_runs`, `harness_steps` tables

### Rust Models + Queries

- `crates/db/src/models.rs` — **MODIFIED** — Added `Avatar`, `HarnessRun`, `HarnessStep` structs
- `crates/db/src/queries.rs` — **MODIFIED** — Added avatar queries (list, get, get_by_key, create, update, soft_delete, ensure_defaults) and harness queries (list_runs, get_run, create_run, update_run_status, cancel_run, list_steps, create_step, update_step_status)

### Rust HTTP Routes

- `crates/http/src/routes/avatars.rs` — **NEW** — Avatar CRUD endpoints
- `crates/http/src/routes/harness.rs` — **NEW** — Harness ledger endpoints
- `crates/http/src/routes/mod.rs` — **MODIFIED** — Added `avatars`, `harness` modules
- `crates/http/src/router.rs` — **MODIFIED** — Added avatar and harness routes
- `crates/http/src/routes/office/handlers.rs` — **MODIFIED** — Enhanced office aggregation response

### Frontend

- `apps/web/src/lib/api.ts` — **MODIFIED** — Added `avatarsApi`, `harnessApi`, types, normalizers; enhanced `officeApi`
- `apps/web/src/hooks/use-avatars.ts` — **NEW** — React Query hooks for avatars
- `apps/web/src/hooks/use-harness.ts` — **NEW** — React Query hooks for harness

### Tombstones

- `apps/web/src/app/api/avatars/route.ts` — **MODIFIED** — 410 tombstone → `/api/v1/avatars`
- `apps/web/src/app/api/dashboard/route.ts` — **MODIFIED** — 410 tombstone → `/api/v1/office`

### Reports

- `AVATAR_OFFICE_HARNESS_SPINE_REPORT.md` — **NEW** — This report
- `RUST_API_GAP_LEDGER.md` — **MODIFIED** — Marked avatars and dashboard as implemented

---

## 3. Avatar Endpoints

| Method | Path                       | Description                                         |
| ------ | -------------------------- | --------------------------------------------------- |
| GET    | `/api/v1/avatars`          | List active avatars for org                         |
| POST   | `/api/v1/avatars`          | Create new avatar                                   |
| GET    | `/api/v1/avatars/{id}`     | Get avatar by ID                                    |
| PATCH  | `/api/v1/avatars/{id}`     | Update avatar (personality, tool_permissions, etc.) |
| DELETE | `/api/v1/avatars/{id}`     | Soft-delete avatar (sets is_active=false)           |
| POST   | `/api/v1/avatars/defaults` | Ensure default avatars exist for org                |

### Default Avatar Keys

`strategist`, `growth_operator`, `copywriter`, `researcher`, `analyst`, `creative_director`, `proof_collector`

### Response Shape

```json
{
  "avatar_id": "...",
  "avatar_key": "strategist",
  "display_name": "Strategist",
  "role": "strategy",
  "archetype": "market_war_room",
  "personality": { "tone": "direct", "creativity": 0.7, ... },
  "tool_permissions": { "can_use_bedrock": true, ... },
  "memory_scope": "org",
  "is_active": true,
  "created_at": "...",
  "updated_at": "..."
}
```

### Security Rules

- `org_id` from `TenantContext` only — never from request body
- Duplicate `avatar_key` returns 409
- Missing avatar returns 404
- DELETE is soft-delete (is_active=false)

---

## 4. Office Aggregation Endpoint

`GET /api/v1/office` — Enhanced response shape:

```json
{
  "org_id": "...",
  "summary": {
    "active_campaigns": 0,
    "active_council_sessions": 0,
    "open_nudges": 0,
    "recent_muse_conversations": 0
  },
  "event_types": [...],
  "status": "ok",
  "updated_at": "..."
}
```

Backwards compatible with existing `officeApi.getState()` frontend caller.

---

## 5. Harness Ledger Endpoints

| Method | Path                               | Description                               |
| ------ | ---------------------------------- | ----------------------------------------- |
| GET    | `/api/v1/harness/runs`             | List harness runs for org                 |
| POST   | `/api/v1/harness/runs`             | Create harness run (queued, no execution) |
| GET    | `/api/v1/harness/runs/{id}`        | Get run by ID                             |
| POST   | `/api/v1/harness/runs/{id}/cancel` | Cancel a queued/running run               |
| GET    | `/api/v1/harness/runs/{id}/steps`  | List steps for a run                      |

### MVP Behavior

- `POST /harness/runs` creates run + steps for requested avatar_keys
- `execute_now: true` → returns 501 `harness_execution_not_implemented`
- No Bedrock calls
- Statuses: `queued`, `running`, `completed`, `failed`, `cancelled`

### POST Input

```json
{
  "run_type": "council_orchestration",
  "input": { "goal": "Evaluate campaign idea" },
  "avatar_keys": ["strategist", "researcher"],
  "execute_now": false
}
```

---

## 6. Frontend Hooks

### `use-avatars.ts`

- `useAvatars()` — list all active avatars
- `useAvatar(id)` — get single avatar
- `useCreateAvatar()` — create avatar
- `useUpdateAvatar()` — patch avatar
- `useDeleteAvatar()` — soft-delete avatar
- `useEnsureAvatarDefaults()` — ensure default avatars exist

### `use-harness.ts`

- `useHarnessRuns()` — list runs
- `useHarnessRun(id)` — get single run
- `useHarnessSteps(runId)` — list steps for run
- `useCreateHarnessRun()` — create run
- `useCancelHarnessRun()` — cancel run

---

## 7. Tombstoned Routes

| Old Route                     | New Route                | Status                         |
| ----------------------------- | ------------------------ | ------------------------------ |
| `/api/avatars` (Next)         | `/api/v1/avatars` (Rust) | ✅ 410 tombstone               |
| `/api/dashboard` (Next)       | `/api/v1/office` (Rust)  | ✅ 410 tombstone               |
| `/api/harness/inspect` (Next) | —                        | Kept as-is (local harness lib) |

---

## 8. Red Team Results

| Search                                                                        | Result                                 |
| ----------------------------------------------------------------------------- | -------------------------------------- |
| `rg "/api/(avatars\|dashboard\|office\|harness)" apps/web/src`                | Active calls use `/api/v1/*`           |
| `rg "Prisma" apps/web/src/app/api/avatars\|dashboard`                         | No Prisma in tombstoned routes         |
| `rg "@raptorflow/database\|prisma\." apps/web/src/app/api/avatars\|dashboard` | No Prisma imports in tombstoned routes |
| `rg "org_id" crates/http/src/routes/avatars.rs\|harness.rs`                   | org_id from TenantContext only         |

---

## 9. Check Results

| Check                          | Status                                |
| ------------------------------ | ------------------------------------- |
| `pnpm structural:check`        | ✅ PASS                               |
| `pnpm route-parity:check`      | ✅ PASS                               |
| `pnpm runtime-authority:check` | ✅ PASS                               |
| `pnpm typecheck`               | ✅ PASS                               |
| `cargo check --workspace`      | ✅ PASS                               |
| `cargo clippy --lib --bins`    | ✅ PASS (warnings only, pre-existing) |

---

## 10. Remaining Gaps

1. **Harness execution/orchestration** — Ledger scaffold implemented; actual Bedrock execution not yet wired
2. **Avatar memory/ripple integration** — Avatars exist but not yet wired to PRL memory system
3. **Cron jobs** — `daily-wins/cron`, `nudges/cron`, `prl/decay/cron`, `intel/brief/cron` still Prisma-only
4. **Marketing capability kernel** — Not started (intentionally deferred)

---

## 11. Recommended Next Workstream

After Avatar/Office/Harness spine lands:

1. **Harness Execution Patch** — Wire harness runs to actual Bedrock/council execution
2. **Avatar Memory Integration** — Connect avatars to PRL ripple system
3. **Cron Job Migration** — Move remaining cron routes to Rust

---

## 12. Pre-Existing Clippy Warnings

96 clippy warnings in `raptorflow-http` — pre-existing, not introduced by this patch:

- `needless_borrow` (many)
- `should_implement_trait`
- `let_and_return`
- `manual_clamp`
- `collapsible_if`
- etc.

One clippy warning in `raptorflow-db` (new this patch):

- `too_many_arguments` in `create_avatar` (11 args) — acceptable for now
