# Task new-task-3ec9 – Requirements (Outline Draft)

> **Purpose:** Rehydrate the missing requirements artifact so downstream plan/spec/status documents share a common scope reference. This outline captures the sections and bullet prompts that will be expanded in subsequent passes.

## 1. Scope & Objectives

The `new-task-3ec9` workstream exists to close the workflow gaps documented in the expanded status checklist. The scope spans the entire customer journey—authentication, payments, onboarding, BCM generation, surface integration, and operational verification. The objective is to take the “plan marked ✅ but missing in repo” mismatches and drive them to working code and documentation.

Success criteria:
- Every phase (1–6) has the referenced migrations, backend services, frontend components, and tests present in the repository and wired into the live flow.
- PhonePe payments, Supabase auth, and Redis-backed onboarding operate end-to-end with predictable recovery from errors.
- Blueprint design system standards (spacing vars, focus treatments, grid) are enforced in new UI work so UX aligns with the guardrails captured in prior memories.
- Telemetry (audit logging, metrics, runbooks) is sufficient for Ops to diagnose failures.

## 2. Context & Dependencies

- **Stack**: Frontend on Vercel (Next.js 14), backend FastAPI service (Render/Supabase functions), Supabase Postgres + auth, Upstash Redis, Vertex AI, Resend, PhonePe full-page SDK. All environment configs must be aligned between `.env`, `.env.local`, `.env.production`, Vercel dashboard, and backend `.env` files per the global coordination items.
- **Artifacts**: The Zenflow package lost `requirements.md`, `spec.md`, and `plan.md`; this file re-establishes the requirements baseline so forthcoming spec/plan rewrites share terminology with `status.md`.
- **Compliance**: Blueprint UI alignment (spacing tokens, focus states), TDD workflow from Conductor (`plan.md` gating), PhonePe SDK constraints (merchant key/secret, full-page SDK, no legacy salt), Supabase redirect rules (localhost:3000/auth/callback, environment-based redirects).

## 3. Functional Requirements by Phase

### 3.1 Phase 1 – Authentication & Profiles
- **Database**: Introduce `001_auth_triggers.sql` with `handle_new_user_profile()` and `handle_new_workspace()` (or equivalent) to auto-create profiles/workspaces when Supabase auth users are inserted. Include idempotent logic, indexes, and RLS.
- **Backend**: Implement `backend/services/profile_service.py` exposing `ensure_profile_exists`, `create_workspace_if_missing`, `verify_profile_complete`. FastAPI routes (`POST /auth/ensure-profile`, `GET /auth/verify-profile`) call the service and enforce workspace/payment pre-checks.
- **Frontend**: Extend `src/components/auth/AuthProvider.tsx` (and route guards/middleware) to block navigation until profile + workspace verified; surface friendly messaging when workspace missing or plan unpaid.
- **Testing**: Add integration tests covering email + Google signup, profile creation failures, workspace linking retries.

### 3.2 Phase 2 – Payments & PhonePe SDK
- **Migrations**: Create `002_payment_transactions.sql` and `005_subscriptions.sql` with proper RLS, indexes, and PhonePe references. Ensure function dependencies (e.g., subscription activation) exist.
- **Backend**: Expand `backend/api/v1/payments_v2.py` to include initiation, status, and cache-backed polling endpoints; add `backend/services/email_service.py` for Resend receipts; implement webhook processing with signature verification and idempotency.
- **Frontend**: Build payment polling utilities and integrate them with onboarding payment step (progress overlay, error states). Align UI copy with PhonePe product team guidance.
- **Docs/Env**: Document PhonePe keys (merchant key/secret), callback URLs, and manual sandbox validation steps.

### 3.3 Phase 3 – Onboarding System
- **Redis Session Manager**: Enhance `backend/redis/session_manager.py` to support schema validation, per-step partial saves, TTL refresh, and draft vs submitted markers. Add cleanup job for stale sessions.
- **API**: `backend/api/v1/onboarding.py` finalize endpoint must validate `business_context.json`, call BCM reducer/service, persist manifest + onboarding_status to Supabase, and clear Redis state.
- **Schema**: Publish `business_context_schema.json` (or Python validator) defining required sections, versioning, and analytics metadata.
- **Frontend**: Implement autosave/resume, progress UI, and error messaging across onboarding steps; ensure Supabase migration adds `onboarding_status` and timestamps to `users` table.

### 3.4 Phase 4 – BCM Generation & Storage
- **Supabase**: Add `003_bcm_storage.sql` for `business_context_manifests` table with versioning, constraints, and RLS.
- **Redis**: Introduce `backend/redis/bcm_storage.py` to tier manifests (e.g., tier0 hot cache, tier1 warm, fallback to Supabase) with TTL and consistency controls.
- **Reducer/Service**: Expand `backend/integration/bcm_reducer.py` and `backend/services/bcm_service.py` with extraction helpers, compression/checksum, version increment, and rebuild orchestration APIs (`backend/api/v1/context.py`).
- **Testing**: Contract tests for reducer outputs, storage tier fallbacks, and API responses.

### 3.5 Phase 5 – Feature Integration
- **State Layer**: Implement Zustand-based BCM store (`src/stores/bcmStore.ts`) and API client utilities (`src/lib/bcm-client.ts`) per `bcm_store_brief.md`.
- **Components**: Create BCM-aware components (freshness badge, rebuild dialog, export button) and embed them into Dashboard, Moves, Campaigns, Analytics, Settings pages with blueprint styling.
- **UX Rules**: Guard features when manifest missing/stale, highlight rebuild prompts, and align copy with product requirements.
- **Testing**: Component/unit tests verifying state reactions, plus page-level integration tests to ensure gating works.

### 3.6 Phase 6 – Testing, Performance & Security
- **Automation**: Reintroduce env validation scripts (ensuring PhonePe/Redis/Supabase/Vertex/Resend keys) and ensure CI runs `npm run lint`, `npm run type-check`, `pytest`, `flake8`, etc.
- **End-to-End**: Build or repair the signup → payment → onboarding → BCM → dashboard journey test, including retries/timeouts/webhook duplicates.
- **Performance**: Benchmark flows (auth <1s, onboarding save <300ms, finalize <5s, BCM fetch <200ms, dashboard <2s) and document results in performance audit files.
- **Security**: Validate RLS policies, webhook signatures, rate limits, audit logging, incident runbooks, and include rollback/deployment checklists.

## 4. Non-Functional Requirements

- **Performance**: Honor the budgets defined in Phase 6; capture metrics via observability tooling and include regression gates in CI when possible.
- **Reliability**: All new services/components must emit structured logs, leverage the audit logger system where appropriate, and expose health metrics for PhonePe, Redis, BCM rebuilds, and onboarding sessions.
- **Security**: Enforce Supabase RLS on new tables, verify PhonePe signature hashes, prevent workspace bypass, and ensure environment secrets are validated before runtime. Follow Blueprint security checklist where applicable.

## 5. Environment & Configuration Matrix

Create a table mapping each service to variable names, files, and owners. At minimum include:
- **Supabase**: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` in frontend `.env.local`, backend `.env`, and Vercel secrets.
- **PhonePe**: `PHONEPE_MERCHANT_ID`, `PHONEPE_MERCHANT_KEY`, `PHONEPE_MERCHANT_SECRET`, callback URLs stored in backend env + Vercel environment and mirrored in PhonePe dashboard.
- **Redis (Upstash)**: `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN` for backend sessions + BCM cache.
- **Vertex AI / Resend / GCS**: Document keys, scopes, project IDs, bucket names, email templates. Note where each is required (backend services, frontend proxies, CI pipelines).

## 6. Deliverables & Acceptance Criteria

- **Artifacts**: SQL migrations (001–005), backend services/modules, FastAPI routes, Redis utilities, frontend stores/components/pages, documentation (requirements/spec/plan/status, runbooks), test suites.
- **Acceptance**: For each phase, define a checklist in plan/spec referencing (a) code merged, (b) tests passing with coverage >80% for new modules, (c) manual verification plan executed, (d) documentation updated.
- **Traceability**: Link plan tasks to repo paths and commit hashes; include placeholders for git notes per Conductor workflow.

## 7. Open Questions & Risks

*Next step:* Expand each section with detailed requirements derived from status.md and future recovered specs.
