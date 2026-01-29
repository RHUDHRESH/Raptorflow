# Task new-task-3ec9 – Technical Specification

_Last updated: 2026-01-28_

## 1. Overview
- **Objective:** Implement the workflow recovery backlog captured in `status.md`, restoring end-to-end functionality across authentication, payments, onboarding, business context generation, feature integration, and operational validation.
- **Scope:** Six phases (Auth, Payments, Onboarding, BCM Storage, Feature Integration, Testing/Perf/Security) plus documentation rehydration. Backend (FastAPI + Supabase), Frontend (Next.js 14 on Vercel), Infra (Upstash Redis, Vertex AI, Resend, PhonePe SDK).
- **Assumptions:** Supabase remains the system of record for auth + data; PhonePe full-page SDK is mandated; Blueprint design conventions must be followed for all UI work; MCP/Playwright instability may persist until tooling refresh.

## 2. Architecture Notes
| Layer | Key Components | Notes |
| --- | --- | --- |
| Frontend | Next.js 14 / App Router, Zustand stores, API proxy routes | All auth-protected data fetched via `/api/proxy` or Supabase client; use `useAuthenticatedApi` hook.
| Backend | FastAPI monolith, Redis (Upstash), Supabase Postgres | New services: profile_service, payments_v2, onboarding + BCM orchestration.
| Data | Supabase tables: users, workspaces, workspace_members, business_context_manifests, payments/subscriptions | Missing migrations 001–005 must be created; align columns with 20260126004502 user schema.
| Observability | Audit logger, logging middleware, metrics placeholders | Extend to cover new flows (PhonePe callbacks, onboarding finalize, BCM rebuilds).

## 3. Functional Specs by Phase
### Phase 1 – Authentication & Profiles
1. **Migration 001** – Auto-profile/workspace triggers (see `001_auth_triggers.sql`) + indexes + RLS alignments.
2. **profile_service.py** – Methods: `ensure_profile_exists(user_id)`, `create_workspace_if_missing(user_id)`, `verify_profile_complete(user_id)`. Uses Supabase admin client.
3. **Auth API** – Add `POST /auth/ensure-profile` (idempotent) and `GET /auth/verify-profile`. Responses include workspace_id, plan status, actionable errors.
4. **AuthProvider.tsx & middleware** – After login, call ensure/verify before routing. Display modals if workspace missing or plan unpaid. Guard `middleware.ts` to prevent bypass.
5. **Tests** – Backend unit/integration tests mocking Supabase; frontend tests for redirect logic.

### Phase 2 – Payments & PhonePe SDK
1. **Migrations 002 & 005** – Payment transactions + subscriptions tables, RLS, indexes, enums for status, PhonePe reference IDs.
2. **backend/services/email_service.py** – Resend integration for payment confirmations.
3. **payments_v2 API** – Flows: initiation (`POST /payments/v2/init`), status polling (`GET /payments/v2/status/{order_id}`), cached results (Redis). Validate amount/tier, log audit events.
4. **Webhook route** – `src/app/api/webhooks/phonepe/route.ts` verifies X-VERIFY signature, idempotent updates, Supabase service-role usage, emails user on completion/failure.
5. **Frontend** – Payment polling utility, onboarding payment step overlay, copy per PhonePe guidelines.
6. **Docs** – Manual test plan, env var matrix.

### Phase 3 – Onboarding System
1. **Redis session manager** – Support schema validation, TTL refresh, draft vs submitted states, background cleanup.
2. **Business context schema** – JSON schema + TypeScript types describing structure from onboarding steps.
3. **Backend finalize endpoint** – Validates session data, builds `business_context.json`, invokes BCM service, persists manifest + onboarding status, clears Redis.
4. **Frontend** – Autosave/resume, progress meter, error states; align with Blueprint spec.
5. **Migration 004** – Add `onboarding_status`, timestamps to `users`.

### Phase 4 – BCM Generation & Storage
1. **Supabase migration 003** – `business_context_manifests` table w/ versioning, checksum, source, JSONB content, indexes.
2. **Redis tiered storage module** – TTL tiers (tier0 hot, tier1 warm, tier2 cold) with `store_bcm` / `retrieve_bcm` API + metrics.
3. **Reducer/service updates** – Compression, checksum, version increments, rebuild orchestration, manual rebuild entrypoints.
4. **API** – `GET /context/manifest`, `GET /context/history`, `POST /context/export`, `POST /context/rebuild`. Add auth/workspace checks.
5. **Tests** – Contract tests verifying reducer output, storage fallbacks, checksums.

### Phase 5 – Feature Integration
1. **State** – Zustand `bcmStore`/`useBcmSync` already scaffolded; extend with selectors for freshness, history, export state.
2. **Components** – Freshness badges, rebuild dialog, export button, stale warnings. Pages affected: Dashboard, Moves, Campaigns, Analytics, Settings.
3. **UX** – When manifest missing/stale, gate controls and show blueprint-styled warnings. Logging for user actions.
4. **Tests** – Component and integration tests verifying gating logic.

### Phase 6 – Testing, Performance & Security
1. **Env validation script** – Asserts presence of PhonePe, Supabase, Redis, Vertex, Resend keys.
2. **Journey test** – Signup → payment → onboarding → BCM → dashboard using Playwright or Cypress (pending MCP fix).
3. **Performance harness** – Record timings vs budgets; update `PERFORMANCE` docs.
4. **Security** – RLS audits, webhook signature tests, rate limiting, audit logger coverage.
5. **Deployment/rollback** – Document manual verification, fallback steps.

## 4. Non-Functional Requirements
- **Performance:** Auth <1s, onboarding autosave <300ms, finalize <5s, BCM fetch <200ms, dashboard load <2s.
- **Reliability:** All flows emit structured logs + audit events; Redis TTL enforcement w/ metrics; fallback strategies documented.
- **Security:** Enforce Supabase RLS, verify PhonePe signatures, ensure environment validation before deploy.
- **UX:** Blueprint design tokens, consistent spacing, focus states, blueprint components.

## 5. Dependencies & Risks
| Dependency | Risk | Mitigation |
| --- | --- | --- |
| PhonePe sandbox credentials | Credentials missing or outdated | Coordinate with ops; document manual test steps. |
| Supabase schema alignment | Existing 130+ migrations already define users/workspaces | Cross-check new migrations vs `20260126004502_backend_user_management_schema.sql`. |
| MCP/Playwright instability | Browser automation blocked | Provide manual test plan fallback; fix MCP separately. |
| Redis tier TTL accuracy | Potential stale data | Implement metrics + logging for tier hits/misses. |

## 6. Acceptance Criteria Summary
- Each phase’s deliverables exist in repo with tests and docs updated.
- Zenflow artifacts (`requirements.md`, `spec.md`, `plan.md`, `status.md`) aligned and cross-linked.
- Manual + automated verification plans documented per Conductor workflow.

## 7. Open Questions
1. Final plan tier mapping for PhonePe (Ascend/So Ascend/Glide) – confirm pricing + entitlements.
2. BCM rebuild cadence – scheduled jobs or manual trigger only?
3. Auth workspace gating – should middleware hard-block or show intermediate screen?
4. Test environment strategy while MCP is flaky – fallback to manual instructions?

---
*Next:* Use this spec to derive `plan.md` with ordered tasks, owners, and checkpoints.
