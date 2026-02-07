# RaptorFlow Master Remediation Plan (Part 1)

This document is the start of a full-repo, step-by-step remediation plan. It is intentionally explicit and ordered. It will be expanded in additional parts to reach the requested depth and length. If you want me to keep extending it, say “continue” and I will append the next section.

## Scope

This plan covers the entire repo: frontend (`src/`), backend (`backend/`), infra/config (`vercel.json`, `backend/cloudbuild.yaml`, `nginx/`, `supabase/`, `gcp/`), tests, and scripts.

## Principles

- Stabilize local dev first, then CI, then staging, then production.
- Align one “canonical” backend entrypoint and one “canonical” frontend runtime.
- Prefer removing duplicate/legacy paths over patching every variant.
- Every feature must have a single source of truth for data + contracts.
- Do not deploy until integration tests and smoke tests pass.

## Task Format

Each task is written as:

- `[#ID] [ ] Task title`
- `Why:` short justification
- `Context:` what this touches
- `Files:` key files or folders
- `Deps:` upstream tasks that must be completed first
- `Output:` concrete deliverable

---

## Phase 0 — Repo Triage And Canonical Paths

- `[#P0-001] [ ] Establish canonical frontend entrypoint`
- `Why:` Multiple legacy paths and scripts make it unclear which app is “real.”
- `Context:` Next.js app appears to live at repo root (`src/`, `package.json`).
- `Files:` `package.json`, `src/app`, `src/components`, `src/lib`
- `Deps:` none
- `Output:` Written statement in this doc identifying the canonical frontend root and removing ambiguity.

- `[#P0-002] [ ] Establish canonical backend entrypoint`
- `Why:` There are multiple FastAPI apps (`backend/main.py`, `backend/app.py`, `backend/main_production.py`, etc.).
- `Context:` Backend app should have a single entrypoint for dev/prod.
- `Files:` `backend/main.py`, `backend/app.py`, `backend/main_production.py`, `backend/run.py`
- `Deps:` none
- `Output:` Documented choice of entrypoint and a plan to retire others.

- `[#P0-003] [ ] Map repo subsystems to owners`
- `Why:` Coordination requires clear module ownership.
- `Context:` Subsystems include frontend, backend, auth, payments, onboarding, BCM, AI/muse, infra.
- `Files:` `docs/architecture/raptorflow_system_overview.md`, `backend/api/v1`, `src/app`
- `Deps:` none
- `Output:` Ownership table in this doc with responsibility boundaries.

- `[#P0-004] [ ] Inventory all environment variables`
- `Why:` Env mismatch is a common failure source.
- `Context:` `.env.example`, `backend/.env.example`, `vercel.json`.
- `Files:` `.env.example`, `backend/.env.example`, `vercel.json`
- `Deps:` none
- `Output:` Unified env matrix in this doc (frontend, backend, infra).

- `[#P0-005] [ ] Normalize Node and Python versions`
- `Why:` Inconsistent versions cause build/test drift.
- `Context:` Node 22.x (frontend); Python 3.12+ (backend).
- `Files:` `package.json`, backend docs
- `Deps:` none
- `Output:` Single source of truth for versions and runtime constraints.

---

## Phase 1 — Local Dev Baseline (Frontend + Backend)

- `[#P1-001] [ ] Ensure frontend builds and runs locally`
- `Why:` The UI must be the first feedback loop.
- `Context:` Next.js at repo root, App Router.
- `Files:` `package.json`, `src/app`, `src/components`, `src/lib`
- `Deps:` `#P0-001`, `#P0-004`, `#P0-005`
- `Output:` `npm run dev` works with mocked or real backend URLs.

- `[#P1-002] [ ] Ensure backend can start with minimal config`
- `Why:` Backend must be runnable in isolation with mocked integrations.
- `Context:` FastAPI app start, with feature flags for mock services.
- `Files:` `backend/main.py`, `backend/config.py`, `backend/dependencies.py`
- `Deps:` `#P0-002`, `#P0-004`, `#P0-005`
- `Output:` `python backend/main.py` (or equivalent) starts without crashing.

- `[#P1-003] [ ] Define default dev ports and URLs`
- `Why:` Frontend and backend must agree on URLs.
- `Context:` `.env.example` uses `3000` and `3001`.
- `Files:` `.env.example`, `backend/.env.example`, `src/lib`
- `Deps:` `#P0-004`
- `Output:` A single documented dev URL map.

- `[#P1-004] [ ] Establish health endpoints and smoke scripts`
- `Why:` Automated sanity checks are required before deeper fixes.
- `Context:` `scripts/quick_check.js`, `backend/health`.
- `Files:` `scripts/quick_check.js`, `backend/health`, `backend/main.py`
- `Deps:` `#P1-001`, `#P1-002`
- `Output:` `npm run health-check` and backend `/health` return OK.

---

## Phase 2 — Backend Stabilization (FastAPI)

- `[#P2-001] [ ] Choose a single FastAPI app definition`
- `Why:` Multiple app definitions cause routing drift.
- `Context:` `backend/main.py` vs `backend/app.py` vs `backend/main_production.py`.
- `Files:` `backend/main.py`, `backend/app.py`, `backend/main_production.py`
- `Deps:` `#P0-002`
- `Output:` A single canonical FastAPI app module and deletion or deprecation plan for others.

- `[#P2-002] [ ] Normalize router registration`
- `Why:` API routes must be defined in one place to avoid missing endpoints.
- `Context:` `backend/api/v1/__init__.py` and app startup.
- `Files:` `backend/api/v1/__init__.py`, `backend/main.py`
- `Deps:` `#P2-001`
- `Output:` One registry for all routers with explicit prefixes.

- `[#P2-003] [ ] Confirm auth endpoints and Supabase integration`
- `Why:` Auth is prerequisite for onboarding, payments, and BCM.
- `Context:` `/auth/*` routes.
- `Files:` `backend/api/v1/auth.py`, `backend/dependencies.py`
- `Deps:` `#P2-002`, `#P0-004`
- `Output:` Auth endpoints respond with expected schema.

- `[#P2-004] [ ] Fix or retire duplicate “minimal/simple” backends`
- `Why:` Multiple backends create untrusted behavior.
- `Context:` `simple_backend.py`, `main_minimal.py`, `run_simple.py`.
- `Files:` `backend/simple_backend.py`, `backend/main_minimal.py`, `backend/run_simple.py`
- `Deps:` `#P2-001`
- `Output:` Only one supported backend runtime remains.

- `[#P2-005] [ ] Verify middleware stack order`
- `Why:` Errors, logging, rate-limit, and CORS must be deterministic.
- `Context:` `backend/app/middleware.py` and `backend/middleware/*`.
- `Files:` `backend/app/middleware.py`, `backend/middleware`
- `Deps:` `#P2-001`
- `Output:` Documented middleware order and tests confirming behavior.

- `[#P2-006] [ ] Standardize error schemas`
- `Why:` Frontend needs consistent error payloads.
- `Context:` `backend/middleware/errors.py`, `backend/core/errors.py`.
- `Files:` `backend/middleware/errors.py`, `backend/core/errors.py`
- `Deps:` `#P2-001`
- `Output:` Single error contract across endpoints.

- `[#P2-007] [ ] Align dependency injection`
- `Why:` Services should be injected once, not re-created per route.
- `Context:` `backend/dependencies.py`, `backend/config.py`.
- `Files:` `backend/dependencies.py`, `backend/config.py`
- `Deps:` `#P2-001`, `#P2-002`
- `Output:` Verified DI graph with clear lifetimes.

- `[#P2-008] [ ] Establish config hierarchy`
- `Why:` Multiple config files imply drift.
- `Context:` `config.py`, `config_clean.py`, `config_simple.py`.
- `Files:` `backend/config.py`, `backend/config_clean.py`, `backend/config_simple.py`
- `Deps:` `#P2-001`, `#P0-004`
- `Output:` One active config module and a deprecation plan for others.

- `[#P2-009] [ ] Ensure requirements file completeness`
- `Why:` Backend installs must be deterministic.
- `Context:` Only `requirements-prod.txt` exists.
- `Files:` `backend/requirements-prod.txt`
- `Deps:` `#P2-001`
- `Output:` A standard `requirements.txt` or a formal decision to use prod-only.

---

## Phase 3 — Data Layer (Supabase, DB, Redis)

- `[#P3-001] [ ] Validate Supabase client usage across backend`
- `Why:` Auth, profile, and storage rely on Supabase.
- `Context:` Auth routes and storage services.
- `Files:` `backend/api/v1/auth.py`, `backend/services/storage.py`, `backend/dependencies.py`
- `Deps:` `#P2-003`
- `Output:` Successful connection and basic CRUD verification.

- `[#P3-002] [ ] Standardize database connection pool`
- `Why:` Multiple DB helpers exist and can conflict.
- `Context:` `backend/database.py` and `backend/core/connection_pool.py`.
- `Files:` `backend/database.py`, `backend/core/connection_pool.py`
- `Deps:` `#P2-007`
- `Output:` One DB pool configured and used by all DB access.

- `[#P3-003] [ ] Validate Redis client setup`
- `Why:` Redis is used for cache, rate limiting, BCM, and session state.
- `Context:` `backend/redis_client.py`, `backend/redis_services.py`.
- `Files:` `backend/redis_client.py`, `backend/redis_services.py`
- `Deps:` `#P0-004`
- `Output:` Verified connection + basic get/set tests.

- `[#P3-004] [ ] Align cache TTL policies`
- `Why:` Cache expiration affects onboarding and BCM accuracy.
- `Context:` `CACHE_TTL`, `SESSION_TTL` and any defaults.
- `Files:` `backend/config.py`, `backend/redis_services.py`
- `Deps:` `#P3-003`
- `Output:` Single TTL policy document and config wiring.

---

## Phase 4 — Core API Features

### 4A) Onboarding

- `[#P4A-001] [ ] Validate onboarding step ingestion endpoints`
- `Why:` Onboarding is upstream of BCM and product readiness.
- `Context:` `/api/v1/onboarding/*`
- `Files:` `backend/api/v1/onboarding.py`, `src/app/onboarding`
- `Deps:` `#P2-002`, `#P3-003`
- `Output:` Endpoints accept step payloads and persist state.

- `[#P4A-002] [ ] Align onboarding frontend state with backend schemas`
- `Why:` Schema drift causes runtime failures.
- `Context:` Step forms + API models.
- `Files:` `src/modules/onboarding`, `src/lib`, `backend/schemas`
- `Deps:` `#P4A-001`
- `Output:` Typed contracts match between frontend and backend.

### 4B) BCM (Business Context Manifest)

- `[#P4B-001] [ ] Verify BCM creation pipeline`
- `Why:` BCM powers most AI features.
- `Context:` `/api/v1/bcm/*` endpoints and storage.
- `Files:` `backend/api/v1/bcm_endpoints.py`, `backend/cognitive`, `backend/redis`
- `Deps:` `#P4A-001`, `#P3-003`
- `Output:` BCM creation completes and returns manifest.

- `[#P4B-002] [ ] Validate BCM retrieval and versioning`
- `Why:` UI needs stable manifest reads.
- `Context:` BCM fetch and version metadata.
- `Files:` `backend/api/v1/bcm_endpoints.py`, `src/lib`
- `Deps:` `#P4B-001`
- `Output:` Consistent manifest retrieval with version info.

### 4C) Payments (PhonePe)

- `[#P4C-001] [ ] Confirm payment initiation workflow`
- `Why:` Subscription gating depends on it.
- `Context:` PhonePe integration and callbacks.
- `Files:` `backend/api/v1/payments.py`, `src/app/onboarding/payment`
- `Deps:` `#P2-002`, `#P0-004`
- `Output:` Initiate endpoint returns checkout URL.

- `[#P4C-002] [ ] Implement webhook verification and status updates`
- `Why:` Payment state must be authoritative.
- `Context:` Webhook handlers.
- `Files:` `src/app/api/webhooks/phonepe`, `backend/api/v1/payments.py`
- `Deps:` `#P4C-001`
- `Output:` Verified webhook processing and transaction updates.

### 4D) Auth + Profiles

- `[#P4D-001] [ ] Confirm auth readiness endpoint logic`
- `Why:` Frontend gating relies on readiness flags.
- `Context:` `/auth/verify-profile`.
- `Files:` `backend/api/v1/auth.py`, `src/lib`
- `Deps:` `#P2-003`
- `Output:` Accurate readiness flags for UX gating.

---

## Phase 5 — AI And “Muse” Content Generation

- `[#P5-001] [ ] Verify Vertex AI credentials and model config`
- `Why:` AI features depend on stable model access.
- `Context:` Vertex AI SDK and model names.
- `Files:` `backend/llm.py`, `backend/cognitive`, `.env.example`
- `Deps:` `#P0-004`, `#P2-007`
- `Output:` Successful model call in a controlled test.

- `[#P5-002] [ ] Stabilize Muse generation endpoints`
- `Why:` Muse is a core differentiator.
- `Context:` Content generation APIs and UI.
- `Files:` `backend/api/v1`, `backend/services`, `src/modules/muse`
- `Deps:` `#P5-001`, `#P4B-001`
- `Output:` Predictable API response schema and UI rendering.

- `[#P5-003] [ ] Add cost and token usage tracking`
- `Why:` AI costs need observability.
- `Context:` Token usage from LLM calls.
- `Files:` `backend/llm.py`, `backend/metrics`
- `Deps:` `#P5-001`
- `Output:` Logged cost metrics per request.

---

## Phase 6 — Notifications (Resend)

- `[#P6-001] [ ] Validate Resend integration`
- `Why:` Notifications and onboarding emails require it.
- `Context:` Resend API usage and templates.
- `Files:` `src/app/api`, `backend/services` (if used), `.env.example`
- `Deps:` `#P0-004`
- `Output:` Successful test email using Resend.

---

## Phase 7 — Monitoring And Error Tracking

- `[#P7-001] [ ] Confirm Sentry config for frontend and backend`
- `Why:` Production stability depends on visibility.
- `Context:` Sentry SDKs in both stacks.
- `Files:` `src/instrumentation.ts`, `backend/middleware/sentry_middleware.py`
- `Deps:` `#P1-001`, `#P2-001`
- `Output:` Sentry captures a test error.

---

## Phase 8 — Deployment

- `[#P8-001] [ ] Validate Vercel build and runtime config`
- `Why:` Frontend deployment depends on Vercel config.
- `Context:` `vercel.json` build env and routes.
- `Files:` `vercel.json`, `.env.example`
- `Deps:` `#P1-001`, `#P0-004`
- `Output:` Successful Vercel build with correct env mapping.

- `[#P8-002] [ ] Validate backend deployment pipeline`
- `Why:` Backend needs a stable CI/CD path.
- `Context:` Cloud Build and Docker settings.
- `Files:` `backend/cloudbuild.yaml`, `backend/Dockerfile`
- `Deps:` `#P2-001`, `#P2-009`
- `Output:` Build and deploy pipeline documented and tested.

---

## Open Questions To Resolve Early

- Which backend module is the canonical FastAPI app: `backend/main.py` or `backend/app.py`?
- Which auth flow is authoritative: Supabase-only or hybrid?
- Which endpoints are required for “must-have” MVP vs long-term roadmap?
- Which environments exist (dev/stage/prod) and where are they deployed?

---

## Next Steps For This Plan

If you want me to continue, I will append Part 2 with:

- Detailed frontend module-by-module fixes
- Full endpoint inventory with contract status
- Infra hardening and secrets management
- Test plan and CI gates
- A full cutover and deployment checklist
