## Summary

Repaired the Campaigns → Moves → Tasks product spine so RaptorFlow can execute its core loop: Foundation → Campaign → Evaluation → Moves → Tasks → Artifacts → Office visibility.

This was a product-contract repair pass, not a pure design pass. The frontend now matches backend reality.

## What was broken

1. **Duplicate campaign hooks** — `hooks/use-campaigns.ts` and `features/campaigns/hooks/index.ts` had overlapping but incompatible types.
2. **Frontend expected fields backend did not return** — `evaluation_result.score`, `move.budget`, `move.sub_goal`, `task.assigned_agent_name`, etc.
3. **Unsafe casts everywhere** — `(eval as any).score`, `(move as {budget?: number}).budget`, `task.status as Task["status"]`.
4. **Fake data in normalize functions** — `normalizeCampaign` invented `progress_pct: 0`, `channels: []`, `tasks_completed: 0`. `normalizeMove` invented `name: "${move_type} move"`, `sub_goal: move_type`.
5. **Fake tasks page** — `INITIAL_TASKS` hardcoded 8 fake tasks with drag-and-drop that only mutated local state.
6. **Fake performance page** — `generateSeries()` created random data with `Math.random()`.
7. **Campaign create discarded fields** — `new/page.tsx` sent `channels` and `timeline` but `campaignsApi.create` only sent `name`+`goal`.
8. **Status naming mismatch** — Frontend used `complete`, backend used `completed`.

## Campaign contract changes

- Created `CampaignSummary`, `CampaignEvaluation`, `CampaignMove`, `CampaignTask` canonical types with runtime guards
- `CampaignEvaluation` uses `overallScore` (backend `overall_score`) not `score`
- `CampaignMove` uses `sequenceNumber`, `moveType`, `status` — no fake `budget`, `sub_goal`, `name`
- `CampaignTask` uses canonical statuses: `pending`, `in_progress`, `completed`, `cancelled`
- Status normalization maps backend `complete` → frontend `completed`

## Move contract changes

- Moves page no longer expects `budget` field (backend doesn't return it)
- Move detail no longer filters tasks by broken `move_name === moveId`
- Shows `sequenceNumber`, `moveType`, `title`, `description` only if available

## Task status changes

- Tasks page replaced fake `INITIAL_TASKS` with real `useCampaignTasks` hook
- Groups by canonical status: `pending`, `in_progress`, `completed`, `cancelled`
- Uses `StatusPill` component for consistent status display

## Hooks unified

- Deleted `hooks/use-campaigns.ts` (duplicate)
- Deleted `features/campaigns/hooks/index.ts` (old incompatible types)
- Created flat `features/campaigns/hooks.ts` with all campaign hooks
- Centralized query keys in `campaignKeys`
- All hooks use runtime guards, no `as any`

## Office move ladder update

- Added `useOfficeRecentMoves` hook
- Fetches campaigns, then moves from first campaign with moves
- Shows real move data in Office if available
- Falls back to honest empty state with link to Campaigns

## Files changed

### Created

- `apps/web/src/features/campaigns/types.ts`
- `apps/web/src/features/campaigns/hooks.ts`
- `apps/web/src/features/campaigns/index.ts`
- `docs/frontend-phase-4-campaigns-moves-audit.md`
- `docs/frontend-phase-4-campaigns-moves-product-spine.md`

### Rewritten

- `apps/web/src/app/(app)/campaigns/page.tsx`
- `apps/web/src/app/(app)/campaigns/[campaignId]/page.tsx`
- `apps/web/src/app/(app)/campaigns/[campaignId]/moves/page.tsx`
- `apps/web/src/app/(app)/campaigns/[campaignId]/tasks/page.tsx`
- `apps/web/src/app/(app)/campaigns/[campaignId]/moves/[moveId]/page.tsx`
- `apps/web/src/app/(app)/campaigns/[campaignId]/edit/page.tsx`

### Updated

- `apps/web/src/app/(app)/office/page.tsx`
- `apps/web/src/features/office/hooks.ts`

### Deleted

- `apps/web/src/hooks/use-campaigns.ts`
- `apps/web/src/features/campaigns/hooks/index.ts`

## Commands run with pass/fail table

| Command                   | Result                    |
| ------------------------- | ------------------------- |
| `pnpm typecheck`          | PASS                      |
| `pnpm lint`               | PASS                      |
| `pnpm structural:check`   | PASS (pre-existing WARNs) |
| `cargo fmt --all --check` | PASS                      |
| `cargo check --workspace` | PASS                      |

## Manual smoke checklist

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

## Known limitations

- Campaign full edit (name, goal) not yet persisted — backend only supports status updates
- Move enrichment (title, description) depends on backend generated content linking
- Task detail endpoints (/approve, /complete) may need Rust implementation
- Performance analytics page still uses fake data — needs real backend

## Confirmations

- [x] No fake data added
- [x] No discarded form fields (create only sends what backend accepts)
- [x] No unsafe casts added
- [x] No billing/landing work
- [x] No force push
- [x] No stale PR merge
