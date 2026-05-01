# Phase 4 — Campaigns, Moves, Tasks Product Spine Audit

## Current State Summary

The campaigns/moves/tasks spine has **significant contract mismatches** between frontend expectations and backend reality. The frontend invents data, uses duplicate hooks, and has fake performance pages.

## Frontend Routes

| Route                            | File       | Status                          | Issues                                                                                                                                                                   |
| -------------------------------- | ---------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `/campaigns`                     | `page.tsx` | Uses `features/campaigns/hooks` | Creates campaign with `title`+`brief`, then auto-evaluates. Expects `evaluation_result.score` but backend returns `overall_score`.                                       |
| `/campaigns/new`                 | `page.tsx` | Uses `hooks/use-campaigns`      | Sends `name`, `goal`, `timeline`, `channels` — but `campaignsApi.create` only sends `name`+`goal`. Channels/timeline silently discarded.                                 |
| `/campaigns/[id]`                | `page.tsx` | Uses `features/campaigns/hooks` | Expects `CampaignDetail` with `moves`, `evaluation_result`. Uses `(eval as any).score` — backend returns `overall_score`. Fake council rationale.                        |
| `/campaigns/[id]/edit`           | `page.tsx` | Uses `hooks/use-campaigns`      | Only status is persisted. Name/goal edits are silently discarded (comment admits this).                                                                                  |
| `/campaigns/[id]/moves`          | `page.tsx` | Uses `hooks/use-campaigns`      | Expects `move.budget`, `move.sub_goal`, `move.name` — backend `BackendMove` only has `move_type`, `sequence_number`, `status`. Uses `(move as {budget?: number})` casts. |
| `/campaigns/[id]/moves/[moveId]` | `page.tsx` | Uses `hooks/use-campaigns`      | Expects rich move fields. Filters tasks by `task.move_name === moveId` but `normalizeTask` sets `move_name: task.move_id`.                                               |
| `/campaigns/[id]/tasks`          | `page.tsx` | **FAKE DATA**                   | `INITIAL_TASKS` hardcoded array with fake tasks. No API call. Drag-and-drop only mutates local state.                                                                    |
| `/campaigns/[id]/tasks/[taskId]` | `page.tsx` | Raw fetch                       | Uses `useAuth` + raw fetch instead of `apiFetch`. Calls `/approve`, `/request-revision`, `/complete` endpoints that may not exist in Rust router.                        |
| `/campaigns/[id]/performance`    | `page.tsx` | **FAKE DATA**                   | `generateSeries()` creates random data. All metrics are `Math.random()`.                                                                                                 |

## Hook Duplication

| Hook                  | Location                            | Used By                                                   |
| --------------------- | ----------------------------------- | --------------------------------------------------------- |
| `useCampaigns`        | `features/campaigns/hooks/index.ts` | `/campaigns/page.tsx`                                     |
| `useCampaigns`        | `hooks/use-campaigns.ts`            | `/campaigns/new`, `/campaigns/[id]/edit`                  |
| `useCampaign`         | `features/campaigns/hooks/index.ts` | `/campaigns/[id]/page.tsx`                                |
| `useCampaign`         | `hooks/use-campaigns.ts`            | `/campaigns/[id]/edit`                                    |
| `useCreateCampaign`   | `features/campaigns/hooks/index.ts` | `/campaigns/page.tsx`                                     |
| `useCreateCampaign`   | `hooks/use-campaigns.ts`            | `/campaigns/new/page.tsx`                                 |
| `useCampaignMoves`    | `hooks/use-campaigns.ts`            | `/campaigns/[id]/moves`, `/campaigns/[id]/moves/[moveId]` |
| `useCampaignTasks`    | `hooks/use-campaigns.ts`            | `/campaigns/[id]/moves/[moveId]`                          |
| `useEvaluateCampaign` | `features/campaigns/hooks/index.ts` | `/campaigns/page.tsx`, `/campaigns/[id]/page.tsx`         |
| `useGenerateMoves`    | `features/campaigns/hooks/index.ts` | `/campaigns/[id]/page.tsx`                                |
| `useUpdateTask`       | `features/campaigns/hooks/index.ts` | `/campaigns/[id]/page.tsx` (via MoveCard)                 |
| `useUpdateTaskStatus` | `hooks/use-campaigns.ts`            | Unused?                                                   |

**Decision:** Unify to `features/campaigns/hooks.ts` (flat file, not index.ts). Delete `hooks/use-campaigns.ts`.

## API Contract Mismatches

### Campaign List (`GET /api/v1/campaigns`)

**Backend returns:**

```json
{
  "campaigns": [
    {
      "campaign_id": "uuid",
      "org_id": "uuid",
      "name": "string",
      "goal": "string",
      "status": "string",
      "active_move_id": "uuid|null",
      "created_at": "ISO",
      "updated_at": "ISO"
    }
  ]
}
```

**Frontend expects (`features/campaigns/hooks/index.ts`):**

```typescript
interface CampaignListItem {
  id: string; // Backend: campaign_id
  title: string; // Backend: name
  brief: string; // NOT RETURNED
  status: string; // ✓
  goal: string | null; // ✓
  budget: string | null; // NOT RETURNED
  timeframe: string | null; // NOT RETURNED
  evaluation_result: Record | null; // NOT RETURNED
  evaluated_at: string | null; // NOT RETURNED
  move_count: number; // NOT RETURNED
  created_at: string; // ✓
}
```

**Frontend expects (`lib/api.ts` normalizeCampaign):**

- Invents: `goal_type: "awareness"`, `progress_pct: 0`, `timeline`, `channels: []`, `tasks_completed: 0`, `tasks_total: 0`

### Campaign Detail (`GET /api/v1/campaigns/:id`)

**Backend returns:** Same campaign fields + moves array + tasks array.

**Frontend `features/campaigns/hooks/index.ts` expects:**

- `moves: CampaignMove[]` with `title`, `description`, `channel`, `priority`, `tasks`
- Backend moves: `move_id`, `campaign_id`, `move_type`, `sequence_number`, `status`, `created_at`

### Evaluation (`POST /api/v1/campaigns/:id/evaluate`)

**Backend returns:**

```json
{
  "campaign_id": "uuid",
  "evaluation": {
    "overall_score": number,
    "strengths": [],
    "weaknesses": [],
    "opportunities": [],
    "threats": [],
    "recommendations": []
  }
}
```

**Frontend expects (`features/campaigns/hooks/index.ts`):**

```typescript
evaluation: {
  score: number; // Backend: overall_score
  summary: string; // NOT RETURNED
  strengths: []; // ✓
  weaknesses: []; // ✓
  icp_fit: string; // NOT RETURNED
  suggested_goal: string; // NOT RETURNED
  recommended_channels: []; // NOT RETURNED
  budget_assessment: string; // NOT RETURNED
}
```

**Frontend code uses:** `(eval as any).score` — should be `overall_score`.

### Moves (`GET /api/v1/campaigns/:id/moves`)

**Backend returns:**

```json
{
  "moves": [
    {
      "move_id": "uuid",
      "campaign_id": "uuid",
      "move_type": "string",
      "sequence_number": number,
      "status": "string",
      "created_at": "ISO"
    }
  ]
}
```

**Frontend expects:**

- `move_number`, `name`, `type`, `sub_goal`, `start_date`, `end_date`, `status`, `tasks_completed`, `tasks_total`, `budget`

**`lib/api.ts` normalizeMove invents:**

- `name: "${move_type} move"`
- `sub_goal: move.move_type`
- `start_date/end_date: move.created_at`
- `tasks_completed: 0`, `tasks_total: 0`

### Tasks (`GET /api/v1/campaigns/:id/tasks`)

**Backend returns:**

```json
{
  "tasks": [
    {
      "task_id": "uuid",
      "move_id": "uuid",
      "campaign_id": "uuid",
      "title": "string",
      "status": "string",
      "scheduled_date": "ISO|null",
      "created_at": "ISO"
    }
  ]
}
```

**Frontend expects (`lib/api.ts` Task interface):**

- `task_type`, `channel`, `content_ready`, `assigned_agent_key`, `assigned_agent_name`, `move_name`, `priority`

**`normalizeTask` invents:**

- `task_type: "setup"`, `channel: "general"`, `content_ready: false`
- `assigned_agent_key: "strategist"`, `assigned_agent_name: "Strategist"`
- `move_name: task.move_id` (should be move name, not ID)

## Unsafe Casts Found

1. `/campaigns/page.tsx:314` — `(c.evaluation_result as any).score`
2. `/campaigns/[id]/page.tsx:238` — `campaign.evaluation_result as { score: number; ... }`
3. `/campaigns/[id]/moves/page.tsx:27` — `(move as { budget?: number }).budget`
4. `/campaigns/[id]/moves/page.tsx:125` — `(move as { budget?: number }).budget`
5. `/campaigns/[id]/moves/[moveId]/page.tsx:42` — `task.move_name === moveId` (move_name is move_id string)
6. `lib/api.ts:2526` — `campaign.status as Campaign["status"]`
7. `lib/api.ts:2552` — `move.status as Move["status"]`
8. `lib/api.ts:2564` — `task.status as Task["status"]`

## Fake Data Found

1. `/campaigns/[id]/tasks/page.tsx` — `INITIAL_TASKS` hardcoded 8 fake tasks
2. `/campaigns/[id]/performance/page.tsx` — `generateSeries()` random data, fake channel breakdown
3. `lib/api.ts:normalizeCampaign` — invents `goal_type`, `progress_pct`, `channels`, `tasks_*`
4. `lib/api.ts:normalizeMove` — invents `name`, `sub_goal`, `start_date`, `end_date`, `tasks_*`
5. `lib/api.ts:normalizeTask` — invents `task_type`, `channel`, `assigned_agent_*`, `move_name`
6. `lib/api.ts:normalizeCampaignDetail` — invents `council_rationale`, `outcome_projection`

## Status Mismatches

| Frontend Status                                                          | Backend Status | Canonical                                          |
| ------------------------------------------------------------------------ | -------------- | -------------------------------------------------- |
| `complete`                                                               | `completed`    | `completed`                                        |
| `pending`, `due`, `ready_for_review`, `approved`, `missed`, `processing` | varies         | `pending`, `in_progress`, `completed`, `cancelled` |

## What Will Be Fixed in This PR

1. **Unify hooks** — Delete `hooks/use-campaigns.ts`, consolidate to `features/campaigns/hooks.ts`
2. **Create canonical types** — `features/campaigns/types.ts` with runtime guards
3. **Repair campaign list** — Use real backend shape, honest empty states
4. **Repair campaign detail** — Match evaluation response (`overall_score` not `score`)
5. **Repair moves page** — Remove fake budget/sub_goal expectations, show only real fields
6. **Repair tasks page** — Replace fake INITIAL_TASKS with real API data
7. **Fix normalize functions** — Stop inventing fields; document what backend lacks
8. **Fix status naming** — Use canonical `completed` not `complete`
9. **Office move ladder** — Wire real moves if available

## What Remains for Later

1. **Backend enrichment** — Moves need `title`, `description`, `expected_impact` from generated content
2. **Task detail endpoints** — `/approve`, `/request-revision`, `/complete` may need Rust implementation
3. **Performance page** — Needs real analytics backend
4. **Campaign edit** — Full PUT update (name, goal) needs backend support
5. **Pusher real-time** — Task updates via websocket
