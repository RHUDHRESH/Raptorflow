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
