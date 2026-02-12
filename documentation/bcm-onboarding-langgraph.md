# BCM-First Onboarding and LangGraph Orchestration

This document defines the canonical startup contract for every workspace.

## Core Rule

No campaign, move, or muse generation runs until a workspace has a valid BCM.

## Canonical Flow

1. Create workspace: `POST /api/workspaces/`
2. Fetch step schema: `GET /api/workspaces/onboarding/steps`
3. Check status: `GET /api/workspaces/{workspace_id}/onboarding/status`
4. Complete onboarding: `POST /api/workspaces/{workspace_id}/onboarding/complete`
5. Backend generates `business_context` and seeds BCM through `langgraph_context_orchestrator.seed`.
6. Workspace settings are marked `bcm_ready=true`.
7. Campaigns, moves, and muse routes are unblocked.

## API Contracts

### `GET /api/workspaces/onboarding/steps`

Returns immutable onboarding schema metadata:
- `schema_version`
- `total_steps`
- `required_steps`
- ordered `steps[]`

### `GET /api/workspaces/{workspace_id}/onboarding/status`

Returns runtime completion state:
- `completed`
- `bcm_ready`
- `completion_pct`
- `missing_required_steps`
- `answers`

### `POST /api/workspaces/{workspace_id}/onboarding/complete`

Input:
- `answers` keyed by onboarding step id.

Side effects:
- validates required steps
- generates canonical `business_context`
- seeds BCM via LangGraph
- upserts foundation summary
- persists onboarding + BCM summary into workspace settings

Output:
- updated `workspace`
- `onboarding` status
- normalized `bcm` payload
- generated `business_context`

## Frontend Enforcement

`WorkspaceProvider` is the source of truth.

Rules:
- after workspace resolution, provider always fetches onboarding status
- if not completed, redirect to `/onboarding`
- if completed and route is `/onboarding`, redirect to `/dashboard`

Onboarding UI:
- route: `src/app/(shell)/onboarding/page.tsx`
- pulls schema from backend
- renders all steps dynamically
- submits directly to completion endpoint

## BCM Gate

Shared guard: `backend/api/v1/workspace_guard.py`

Used by:
- `backend/api/v1/campaigns.py`
- `backend/api/v1/moves.py`
- `backend/api/v1/muse.py`

Behavior:
- validates workspace header
- confirms workspace exists
- enforces BCM readiness
- if BCM missing: returns `412 Precondition Failed`

## Step IDs (Schema v2026.02)

1. `company_name`
2. `company_website`
3. `industry`
4. `business_stage`
5. `company_description`
6. `primary_offer`
7. `core_problem`
8. `ideal_customer_title`
9. `ideal_customer_profile`
10. `top_pain_points`
11. `top_goals`
12. `key_differentiator`
13. `competitors`
14. `brand_tone`
15. `banned_phrases`
16. `channel_priorities`
17. `geographic_focus`
18. `pricing_model`
19. `proof_points`
20. `acquisition_goal`
21. `constraints_and_guardrails`
