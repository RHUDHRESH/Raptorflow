# TODO – Task `new-task-3ec9`

> Updated: 2026-01-29

This file tracks the remaining implementation and verification work. Each item references the relevant files or evidence already in the repo. Check off items in-place as they land.

## Phase 2 – Payments & PhonePe SDK
1. [ ] Re-review `backend/services/payment_service.py` + `backend/services/phonepe_official_gateway.py` to confirm retry logic, subscription activation, idempotent DB updates, and signature validation. Add missing unit tests.
2. [ ] Audit `src/app/onboarding/payment/page.tsx` (and any related components) to ensure it wires `payment-polling.ts` with UX per PRD (popup handling, progress indicators, retry button).
3. [ ] Document PhonePe + Resend environment variables in README/spec; ensure `.env.*` files include required keys (merchant IDs, RESEND API key, FROM email).
4. [ ] Produce manual sandbox test checklist covering payment initiation, polling, webhook success/failure, subscription activation, and email notifications.
5. [ ] Add backend integration tests for `/api/payments/v2/initiate`, `/status/{id}`, `/webhook` and frontend tests for polling utility.

## Phase 3 – Onboarding System
1. [ ] Enhance `backend/redis/session_manager.py` with schema-aware validation, TTL refresh, draft markers, and cleanup job.
2. [ ] Extend `backend/api/v1/onboarding.py` to add per-step validation, AI retries (3x with backoff), 30s timeout enforcement, and progress metrics in responses.
3. [ ] Define `business_context` JSON schema (include version, company profile, intelligence, positioning, messaging) and add validator module used during finalize.
4. [ ] Implement `POST /api/v1/onboarding/{session_id}/finalize` logic: aggregate 23 steps from Redis, validate against schema, invoke BCM service, update `users.onboarding_status`, persist manifests, purge Redis.
5. [ ] Build onboarding UI enhancements: `ProgressBar`, `AutoSave`, draft resume, save status indicator, and integrate on each step page.
6. [ ] Apply `supabase/migrations/004_onboarding_status.sql` (verify fields/indexes) and backfill data.

## Phase 4 – BCM Generation & Storage
1. [ ] Verify `supabase/migrations/003_bcm_storage.sql` includes required indexes/RLS; apply migration in dev env.
2. [ ] Implement `backend/redis/bcm_storage.py` with tier0/1/2 caches, TTLs (1h/24h/7d), retry logic, and invalidation helpers.
3. [ ] Upgrade `backend/integration/bcm_reducer.py` with `_extract_icps`, `_extract_competitive`, `_extract_messaging`, token budget compression (<1200 tokens), and checksum.
4. [ ] Build `backend/services/bcm_service.py` to orchestrate reduction, storage (Redis + Supabase), retrieval with fallbacks, rebuild workflow, semantic versioning, and validation.
5. [ ] Implement `backend/api/v1/context.py` endpoints: `GET /context/manifest`, `POST /context/rebuild`, `GET /context/version-history`, `GET /context/export` with auth + rate limiting.
6. [ ] Add reducer/storage/service unit tests plus integration test covering cache tier fallback and checksum validation.

## Phase 5 – Feature Integration
1. [ ] Create Zustand store `src/stores/bcmStore.ts` with fetch/rebuild/export actions, error/loading states, and freshness calculator.
2. [ ] Implement BCM client utilities (`src/lib/bcm-client.ts`) for manifest fetch, rebuild trigger, export download with proper error handling.
3. [ ] Build reusable UI components: `BCMIndicator`, `BCMRebuildDialog`, `BCMExportButton` following blueprint spacing/typography.
4. [ ] Integrate BCM data into dashboard page (moves, campaigns, KPIs, ICP highlights) with stale state fallback.
5. [ ] Wire BCM guardrails into Moves, Campaigns, Analytics pages as described in spec (ICP selections, messaging guardrails, channel recommendations, positioning-aligned insights).
6. [ ] Add BCM management panel to Settings (status, version history, rebuild/export controls, progress indicator).

## Phase 6 – Testing, Performance & Security
1. [ ] Create environment validation script covering Supabase, PhonePe, Redis, Vertex AI, Resend, GCS; run on startup.
2. [ ] Apply migrations 001–005 sequentially in dev/staging and record results (include timestamps/DB logs in status file).
3. [ ] Execute full user journey test (Signup → Payment → Onboarding → BCM → Dashboard). Capture screenshots/logs or document manual steps if automation blocked.
4. [ ] Test error recovery scenarios: profile retry exhaustion, webhook delay, Redis outage, AI timeout, BCM rebuild failure, duplicate webhook payloads.
5. [ ] Run `npm run lint`, `npm run type-check`, backend `pytest`, and ensure coverage ≥80% for critical modules.
6. [ ] Benchmark performance targets (auth <1s, payment init <2s, onboarding save <300ms, finalize <5s, BCM fetch <200ms, rebuild <5s, dashboard load <2s).
7. [ ] Perform security verification: JWT gating, RLS enforcement, PhonePe signature validation, rate limiting, no secrets in logs, HTTPS enforcement.
8. [ ] Prepare deployment + rollback checklist, monitoring alert configuration, and final documentation bundle.

## Coordination / Reporting
1. [ ] Assign owners + timelines to every TODO above; track in this file with names/dates.
2. [ ] Update `requirements.md`, `spec.md`, `plan.md`, and `status.md` after each major milestone (Phase completion, migration applied, QA run).
3. [ ] Capture commit SHAs + QA evidence for Conductor checkpoints (`[phaseX-check]`).
4. [ ] Keep dependency matrix up to date (PhonePe SDK version, Resend SDK, Vertex AI client, Redis client, Zustand, etc.).
