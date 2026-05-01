# Phase 4 — Campaigns, Moves, Tasks Product Spine Repair

## Summary

Repaired the Campaigns → Moves → Tasks product spine so RaptorFlow can execute its core loop: Foundation → Campaign → Evaluation → Moves → Tasks → Artifacts → Office visibility.

This was a product-contract repair pass, not a pure design pass. The frontend now matches backend reality.

## What Was Broken

1. **Duplicate campaign hooks** — `hooks/use-campaigns.ts` and `features/campaigns/hooks/index.ts` had overlapping but incompatible types.
2. **Frontend expected fields backend did not return** — `evaluation_result.score`, `move.budget`, `move.sub_goal`, `task.assigned_agent_name`, etc.
3. **Unsafe casts everywhere** — `(eval as any).score`, `(move as {budget?: number}).budget`, `task.status as Task["status"]`.
4. **Fake data in normalize functions** — `normalizeCampaign` invented `progress_pct: 0`, `channels: []`, `tasks_completed: 0`. `normalizeMove` invented `name: "${move_type} move"`, `sub_goal: move_type`.
5. **Fake tasks page** — `INITIAL_TASKS` hardcoded 8 fake tasks with drag-and-drop that only mutated local state.
6. **Fake performance page** — `generateSeries()` created random data with `Math.random()`.
7. **Campaign create discarded fields** — `new/page.tsx` sent `channels` and `timeline` but `campaignsApi.create` only sent `name`+`goal`.
8. **Status naming mismatch** — Frontend used `complete`, backend used `completed`.

## What Was Repaired

### Canonical Types (`features/campaigns/types.ts`)

Created runtime-guarded types:

- `CampaignSummary` — matches backend `campaign_id`, `name`, `goal`, `status`, `created_at`
- `CampaignEvaluation` — matches backend `overall_score` (not `score`), `strengths`, `weaknesses`, `opportunities`, `threats`, `recommendations`
- `CampaignMove` — matches backend `move_id`, `campaign_id`, `sequence_number`, `move_type`, `status`, `created_at`
- `CampaignTask` — matches backend `task_id`, `campaign_id`, `move_id`, `title`, `status`, `created_at`
- Runtime guards: `isCampaignSummary`, `isCampaignEvaluation`, `isCampaignMove`, `isCampaignTask`
- Normalization functions that convert snake_case → camelCase without inventing data

### Unified Hooks (`features/campaigns/hooks.ts`)

- Deleted `hooks/use-campaigns.ts` (duplicate)
- Deleted `features/campaigns/hooks/index.ts` (old incompatible types)
- Created flat `features/campaigns/hooks.ts` with:
  - `useCampaigns()` — returns `CampaignSummary[]`
  - `useCampaignDetail(id)` — returns `{ campaign, moves, tasks, evaluation }`
  - `useCreateCampaign()` — sends `name`+`goal` only (honest)
  - `useEvaluateCampaign()` — returns `CampaignEvaluation` with `overallScore`
  - `useGenerateMoves()` — generates moves, invalidates queries
  - `useCampaignMoves(id)` — returns `CampaignMove[]`
  - `useCampaignTasks(id)` — returns `CampaignTask[]`
  - `useUpdateTaskStatus()` — PATCH `/tasks/{id}/status`
  - `useUpdateCampaignStatus()` — PATCH `/campaigns/{id}/status`
- Centralized query keys in `campaignKeys`

### Campaign List Page (`/campaigns`)

- Uses `CampaignSummary` type
- Shows `name`, `goal`, `status`, `moveCount`, `evaluationScore`
- Create modal only asks for `name` and `goal` (honest to backend)
- Auto-evaluates after creation
- No more `brief` field (backend doesn't store it)

### Campaign Detail Page (`/campaigns/[id]`)

- Uses `useCampaignDetail` with real evaluation data
- Shows `overallScore` (not `score`)
- Shows real `strengths`, `weaknesses`, `recommendations`
- Move cards use real `sequenceNumber`, `moveType`, `title`, `description`
- Tasks toggled via `useUpdateTaskStatus`
- No more fake `council_rationale` or `outcome_projection`

### Moves Page (`/campaigns/[id]/moves`)

- Removed fake `budget` calculations
- Shows `sequenceNumber`, `moveType`, `title`, `description`, `status`
- Honest empty state if no moves
- No more `(move as {budget?: number})` casts

### Tasks Page (`/campaigns/[id]/tasks`)

- **Replaced fake INITIAL_TASKS with real API data**
- Uses `useCampaignTasks`
- Groups by canonical status: `pending`, `in_progress`, `completed`, `cancelled`
- Shows `title`, `description`, `dueAt`, `owner`
- Honest empty state if no tasks

### Move Detail Page (`/campaigns/[id]/moves/[moveId]`)

- Uses real move data
- Shows tasks filtered by `moveId` (not broken `move_name === moveId`)
- No more fake agent references

### Edit Page (`/campaigns/[id]/edit`)

- Uses `useCampaignDetail`
- Status update works
- Name/goal fields show honest warning: "not yet persisted"

### Office Move Ladder

- Added `useOfficeRecentMoves` hook
- Fetches campaigns, then moves from first campaign with moves
- Shows real move data in Office if available
- Falls back to honest empty state

## Files Changed

### Created

- `apps/web/src/features/campaigns/types.ts` — Canonical types with runtime guards
- `apps/web/src/features/campaigns/hooks.ts` — Unified hooks
- `apps/web/src/features/campaigns/index.ts` — Barrel export
- `docs/frontend-phase-4-campaigns-moves-audit.md` — Audit document

### Rewritten

- `apps/web/src/app/(app)/campaigns/page.tsx` — Honest create flow, real data
- `apps/web/src/app/(app)/campaigns/[campaignId]/page.tsx` — Real evaluation, real moves
- `apps/web/src/app/(app)/campaigns/[campaignId]/moves/page.tsx` — No fake budget
- `apps/web/src/app/(app)/campaigns/[campaignId]/tasks/page.tsx` — Real API data
- `apps/web/src/app/(app)/campaigns/[campaignId]/moves/[moveId]/page.tsx` — Real move data
- `apps/web/src/app/(app)/campaigns/[campaignId]/edit/page.tsx` — Honest status-only edit

### Updated

- `apps/web/src/app/(app)/office/page.tsx` — Wired real move ladder
- `apps/web/src/features/office/hooks.ts` — Added `useOfficeRecentMoves`

### Deleted

- `apps/web/src/hooks/use-campaigns.ts` — Duplicate hooks
- `apps/web/src/features/campaigns/hooks/index.ts` — Old incompatible hooks

## APIs Used

| Endpoint                                           | Purpose                | Status                |
| -------------------------------------------------- | ---------------------- | --------------------- |
| `GET /api/v1/campaigns`                            | Campaign list          | Real                  |
| `POST /api/v1/campaigns`                           | Create campaign        | Real (name+goal only) |
| `GET /api/v1/campaigns/:id`                        | Campaign detail        | Real                  |
| `POST /api/v1/campaigns/:id/evaluate`              | Evaluate campaign      | Real                  |
| `POST /api/v1/campaigns/:id/moves/generate`        | Generate moves         | Real                  |
| `GET /api/v1/campaigns/:id/moves`                  | Move list              | Real                  |
| `GET /api/v1/campaigns/:id/tasks`                  | Task list              | Real                  |
| `PATCH /api/v1/campaigns/:id/tasks/:taskId/status` | Update task status     | Real                  |
| `PATCH /api/v1/campaigns/:id/status`               | Update campaign status | Real                  |

## Remaining Missing Backend Support

| Feature                                     | Gap                               | Documented |
| ------------------------------------------- | --------------------------------- | ---------- |
| Campaign full edit (name, goal)             | No PUT endpoint                   | Yes        |
| Move enrichment (title, description)        | Backend only returns move_type    | Yes        |
| Task detail endpoints (/approve, /complete) | May not exist in Rust router      | Yes        |
| Performance analytics                       | Entirely fake data                | Yes        |
| Campaign brief                              | Separate endpoint, not integrated | Yes        |

## Manual Smoke Test Checklist

1. [ ] Create campaign — name + goal only
2. [ ] View campaign list — shows name, goal, status, evaluation score
3. [ ] Open campaign detail — shows evaluation with overallScore
4. [ ] Run evaluation — returns strengths/weaknesses/recommendations
5. [ ] Generate moves — creates move ladder
6. [ ] Open moves page — shows sequence, type, status
7. [ ] Open move detail — shows tasks for that move
8. [ ] Open tasks page — shows real tasks grouped by status
9. [ ] Update task status — toggles pending/completed
10. [ ] Verify Office move ladder — reflects real data

## Commands Run

| Command                   | Result                    |
| ------------------------- | ------------------------- |
| `pnpm typecheck`          | PASS                      |
| `pnpm lint`               | PASS                      |
| `pnpm structural:check`   | PASS (pre-existing WARNs) |
| `cargo fmt --all --check` | PASS                      |
| `cargo check --workspace` | PASS                      |

## Confirmations

- [x] No fake data added
- [x] No discarded form fields (create only sends what backend accepts)
- [x] No unsafe casts added
- [x] No billing/landing work
- [x] No force push
- [x] No stale PR merge

## Next Phase Recommendation

**Phase 5: Campaign Backend Enrichment**

Add `title`, `description`, `expected_impact` fields to the moves table so the move ladder can show rich move bodies instead of just `move_type`.
