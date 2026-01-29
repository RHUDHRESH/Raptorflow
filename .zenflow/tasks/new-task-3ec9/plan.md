<<<<<<< HEAD
# Task Plan – new-task-3ec9

_Last updated: 2026-01-28_

## Phase 0 – Coordination & Artifacts
1. Recreate Zenflow documents (`requirements.md`, `spec.md`, `plan.md`, `status.md`).
2. Sync status tracker with real repo gaps (auth, payments, onboarding, BCM, testing).
3. Assign owners (backend, frontend, QA, ops) and confirm environment matrix.
4. Resolve pre-commit/lint failures blocking work (e.g., trailing whitespace).

## Phase 1 – Authentication & Profiles
- **Goal:** Users cannot access anything without profiles/workspaces; Supabase + backend enforce creation and verification.
- **Tasks:**
  1. Finalize `001_auth_triggers.sql` (triggers stored in repo).
  2. Implement `backend/services/profile_service.py` and FastAPI endpoints `/auth/ensure-profile`, `/auth/verify-profile`.
  3. Update `AuthProvider`, middleware, and route guards to enforce profile + workspace gating.
  4. Add integration/unit tests (backend + frontend) and docs.
- **Checkpoint:** `[phase1-check]` when API + frontend gating verified.

## Phase 2 – Payments & PhonePe SDK
- **Goal:** PhonePe full-page flow works end-to-end with subscriptions + email confirmations.
- **Tasks:**
  1. Add migrations `002_payment_transactions.sql` and `005_subscriptions.sql`.
  2. Implement `backend/services/email_service.py` + update `payments_v2` endpoints (init/status/cache/logging).
  3. Harden PhonePe webhook route + Resend notifications + idempotency.
  4. Build frontend polling utility + onboarding payment UI.
  5. Write tests (backend + frontend) and PhonePe manual test doc.
- **Checkpoint:** `[phase2-check]` after sandbox payment journey passes.

## Phase 3 – Onboarding System
- **Goal:** Redis-backed onboarding with autosave, schema validation, and finalize endpoint that persists BCM + onboarding status.
- **Tasks:**
  1. Enhance `redis/session_manager.py` (validation, TTL refresh, draft markers, cleanup job).
  2. Define business context JSON schema/validator + TypeScript types.
  3. Implement finalize endpoint (validate steps, generate `business_context.json`, call BCM service, update Supabase, clear session).
  4. Frontend autosave/resume/progress UI with errors.
  5. Migration `004_add_onboarding_status.sql` (users table).
  6. Tests: Redis manager, API, autosave/resume flows.
- **Checkpoint:** `[phase3-check]` once finalize endpoint + UI verified.

## Phase 4 – BCM Generation & Storage
- **Goal:** Tiered BCM storage with Supabase persistence, reducer upgrades, and API endpoints.
- **Tasks:**
  1. Migration `003_bcm_storage.sql` for `business_context_manifests` table + RLS.
  2. Redis tiered storage module (`bcm_storage.py`) integrated with `MemoryController`.
  3. Upgrade `bcm_reducer` + `bcm_service` with compression, checksum, versioning.
  4. API routes: manifest/history/export/rebuild with workspace/auth checks.
  5. Tests: reducer contracts, storage fallback, checksum validation.
- **Checkpoint:** `[phase4-check]` when BCM fetch/rebuild works with caching tiers.

## Phase 5 – Feature Integration
- **Goal:** Frontend surfaces consume BCM state (freshness badges, rebuild/export controls, guardrails).
- **Tasks:**
  1. Finalize Zustand store (`bcmStore`), `useBcmSync` hook, and client utilities.
  2. Integrate into Dashboard (done), Moves, Campaigns, Analytics, Settings.
  3. Build UI components (freshness indicator, rebuild dialog, export controls) with blueprint styling + spacing tokens.
  4. Add error/stale states and logging.
  5. Tests: component/unit/integration coverage for gating logic.
- **Checkpoint:** `[phase5-check]` when all surfaces display BCM freshness + controls.

## Phase 6 – Testing, Performance & Security
- **Goal:** Holistic verification covering env validation, E2E journeys, performance budgets, security.
- **Tasks:**
  1. Env validation script for all secrets.
  2. E2E test (signup → payment → onboarding → BCM → dashboard) or documented manual fallback if MCP blocked.
  3. Performance benchmarks + documentation updates.
  4. Security reviews (RLS, webhook sigs, rate limits, audit logging) with fixes.
  5. Deployment + rollback checklist, monitoring alerts.
- **Checkpoint:** `[phase6-check]` after QA signoff.

## Phase 7 – Verification & Reporting
1. Execute Conductor verification protocol when a phase completes (tests, manual plan, checkpoint commit, git notes).
2. Update `status.md` tracker and Zenflow docs with progress + commit SHAs.
3. Produce final verification report once all phases complete.
=======
# Full SDD workflow

## Configuration
- **Artifacts Path**: {@artifacts_path} → `.zenflow/tasks/{task_id}`

---

## Workflow Steps

### [x] Step: Requirements
<!-- chat-id: d980d798-4880-410c-9785-c1f7033acdbf -->

Create a Product Requirements Document (PRD) based on the feature description.

1. Review existing codebase to understand current architecture and patterns
2. Analyze the feature definition and identify unclear aspects
3. Ask the user for clarifications on aspects that significantly impact scope or user experience
4. Make reasonable decisions for minor details based on context and conventions
5. If user can't clarify, make a decision, state the assumption, and continue

Save the PRD to `{@artifacts_path}/requirements.md`.

**Status**: ✅ COMPLETED - Comprehensive PRD created covering:
- Complete user journey (Auth → Payment → Onboarding → BCM → Features)
- Authentication flow requirements and fixes
- PhonePe SDK integration requirements
- Onboarding system requirements (23 steps)
- BCM generation system requirements
- Feature integration requirements (Dashboard, Moves, Campaigns, Analytics, Settings)
- Technical requirements for each component
- Success criteria and metrics
- Open questions for clarification

### [ ] Step: Technical Specification
<!-- chat-id: 3f971a9b-1094-4cdb-ab8f-f9d95d796568 -->

Create a technical specification based on the PRD in `{@artifacts_path}/requirements.md`.

1. Review existing codebase architecture and identify reusable components
2. Define the implementation approach

Save to `{@artifacts_path}/spec.md` with:
- Technical context (language, dependencies)
- Implementation approach referencing existing code patterns
- Source code structure changes
- Data model / API / interface changes
- Delivery phases (incremental, testable milestones)
- Verification approach using project lint/test commands

### [ ] Step: Planning

Create a detailed implementation plan based on `{@artifacts_path}/spec.md`.

1. Break down the work into concrete tasks
2. Each task should reference relevant contracts and include verification steps
3. Replace the Implementation step below with the planned tasks

Rule of thumb for step size: each step should represent a coherent unit of work (e.g., implement a component, add an API endpoint, write tests for a module). Avoid steps that are too granular (single function) or too broad (entire feature).

If the feature is trivial and doesn't warrant full specification, update this workflow to remove unnecessary steps and explain the reasoning to the user.

Save to `{@artifacts_path}/plan.md`.

### [ ] Step: Implementation

This step should be replaced with detailed implementation tasks from the Planning step.

If Planning didn't replace this step, execute the tasks in `{@artifacts_path}/plan.md`, updating checkboxes as you go. Run planned tests/lint and record results in plan.md.
>>>>>>> new-task-3ec9
