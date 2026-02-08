# REPO_MAP.md (Updated 2026-02-08, services consolidation)

Goal: keep a single, working, no-auth path through the app. Everything else is legacy.

## Canonical Services (ADR-0005)

| Service | Provider | Client Module |
|---------|----------|---------------|
| Database + Storage | Supabase | `backend/core/supabase_mgr.py`, `backend/core/storage_mgr.py` |
| AI Inference | Vertex AI (Gemini) | `backend/services/vertex_ai_service.py` |
| Caching | Upstash Redis | `backend/core/redis_mgr.py` |
| Email | Resend | `backend/services/email_service.py` |
| Monitoring | Sentry | Init in `backend/app_factory.py`, frontend via `@sentry/nextjs` |

Email templates: `backend/templates/email/` (6 Jinja2 transactional templates).

## Commands

Frontend (Next.js, repo root):

- Dev: `npm.cmd run dev`
- Build: `npm.cmd run build`
- Start: `npm.cmd run start`
- Lint: `npm.cmd run lint`
- Typecheck: `npm.cmd run type-check`
- Unit tests: `npm.cmd run test` (Vitest)
- E2E tests: `npm.cmd run test:e2e` (Playwright; legacy suite currently removed)

Backend (FastAPI, Python):

- Run (Windows): `.\.venv\Scripts\python backend\run_simple.py`
  - If you have an activated venv, `python backend/run_simple.py` is fine too.
  - This runs `uvicorn` against `backend.main:app` (which delegates to `backend.app_factory.create_app()`).

Notes:

- PowerShell may block the `npm` shim (`npm.ps1`) depending on ExecutionPolicy; use `npm.cmd` / `npx.cmd`.

## Canonical Runtime

Frontend (Next.js App Router):

- Routes: `src/app/**`
- Shell layout (no auth): `src/app/(shell)/layout.tsx`
- Marketing routes (no auth): `src/app/features/**`
- Workspace bootstrap (tenant selection/creation):
  - `src/components/workspace/WorkspaceProvider.tsx`
  - localStorage key: `raptorflow.workspace_id`
- HTTP client (explicit error surfacing): `src/services/http.ts`
- Canonical service layer (no auth dependencies): `src/services/*.service.ts`
- Canonical Next API handler: `src/app/api/[...path]/route.ts`
  - Proxy base used by the UI: `/api/proxy/v1/*`
  - Proxies to backend `/api/v1/*` (see `src/services/http.ts`)

Backend (FastAPI):

- ASGI app: `backend/main.py` -> `backend/app_factory.create_app()`
- Router registry (ONLY these are active): `backend/api/registry.py`
  - `backend/api/v1/workspaces.py`
  - `backend/api/v1/campaigns.py`
  - `backend/api/v1/moves.py`
  - `backend/api/v1/foundation.py`
  - `backend/api/v1/muse.py`
  - `backend/api/v1/context.py` (BCM manifest CRUD)
- System routes: `backend/api/system.py`
  - `GET /` and `GET /health`
  - Also mounted under `/api/*` for compatibility (`GET /api/`, `GET /api/health`)

Database:

- Backend uses Supabase service-role access via `core/supabase_mgr.py`.
- Canonical schema (11 tables, pushed 2026-02-08):
  - `workspaces`
  - `workspace_members`
  - `profiles`
  - `foundations` (scoped by `workspace_id`)
  - `business_context_manifests` (scoped by `workspace_id`, versioned)
  - `icp_profiles` (scoped by `workspace_id`)
  - `campaigns` (scoped by `workspace_id`)
  - `moves` (scoped by `workspace_id`)
  - `subscription_plans`
  - `subscriptions`
  - `audit_logs`

BCM Pipeline (Cognitive Identity System - ADR-0005):

- **Core Schema:** `backend/schemas/business_context.py`
  - BCMManifest with identity, prompt_kit, guardrails_v2 (new cognitive sections)
  - BCMIdentity (voice archetype, communication style, vocabulary DNA)
  - BCMPromptKit (system prompts, few-shot examples, ICP voice maps)
  - BCMGuardrailsV2 (positive/negative patterns, tone calibration)

- **AI Synthesis:** `backend/services/bcm_synthesizer.py`
  - Replaces static reducer with Gemini Flash-powered analysis
  - Generates brand identity, prompt templates, and smart guardrails
  - Falls back to static reducer if AI unavailable

- **Services:**
  - `backend/services/bcm_service.py` — Supabase CRUD with async synthesis paths
  - `backend/services/bcm_reducer.py` — Static fallback (legacy)
  - `backend/services/bcm_cache.py` — Upstash Redis hot cache (~2ms reads)
  - `backend/services/prompt_compiler.py` — Builds structured system prompts from BCM
  - `backend/services/bcm_memory.py` — Accumulated learning from feedback
  - `backend/services/bcm_generation_logger.py` — Tracks all Muse outputs
  - `backend/services/bcm_reflector.py` — Periodic self-improvement analysis

- **API Endpoints:**
  - `backend/api/v1/context.py` — BCM CRUD + reflect endpoint
  - `backend/api/v1/bcm_feedback.py` — Feedback submission, memory management
  - `backend/api/v1/muse.py` — AI generation with structured prompts + logging

- **Database Tables:**
  - `business_context_manifests` (existing, now with cognitive sections)
  - `bcm_memories` (new, accumulated learning)
  - `bcm_generation_log` (new, tracks all outputs for reflection)

- **Frontend:**
  - Types: `src/types/bcm.ts` (updated with cognitive identity types)
  - Service: `src/services/bcm.service.ts` + `src/services/feedback.service.ts`
  - Store: `src/stores/bcmStore.ts` (synthesized flag, reflect action)
  - UI: `src/components/bcm/BCMStatusPanel.tsx` (AI+ badge, Reflect button, memory count)
  - Feedback: `src/components/muse/MuseChat.tsx` (thumbs up/down on generations)

- **Key Features:**
  - AI-synthesized brand DNA at ingestion time
  - Structured system prompts (separates brand identity from user task)
  - Redis caching for sub-5ms BCM reads
  - User feedback → memories → BCM evolution
  - Periodic reflection analyzes patterns and updates guardrails
  - All with Gemini 2.0 Flash (cheap model, structured prompting = quality output)

Tenant model:

- No login / no JWT.
- Tenant boundary is workspace id (UUID) provided via request header: `x-workspace-id`.

Moves deep-links:

- Wizard: `/moves?new=1` or `/moves?create=true`
- Detail modal: `/moves?moveId=<uuid>`

## Folder Structure

```
/                       ← 5 root MDs: AGENTS, README, REPO_MAP, API_INVENTORY, AUTH_INVENTORY
├── ADRs/               ← Architectural Decision Records
├── archive/            ← Archived docs, screenshots, test artifacts (not canonical)
│   ├── docs/           ← Categorized: architecture/, security-audits/, redis/, etc.
│   ├── screenshots/    ← Historical UI screenshots
│   └── test-artifacts/ ← Old test output folders
├── backend/            ← Canonical FastAPI backend
│   ├── api/            ← Route handlers
│   ├── app/            ← Lifespan, middleware
│   ├── config/         ← Settings (Pydantic)
│   ├── core/           ← Service clients: supabase_mgr, redis_mgr, storage_mgr
│   ├── services/       ← Business logic: BCM, Vertex AI, email
│   └── templates/email ← Jinja2 email templates
├── docs/               ← Canonical documentation
├── src/                ← Next.js frontend (App Router)
└── supabase/           ← Migrations
```

## Legacy / Not Canonical

- Extra Next routes under `src/app/*` not linked from the canonical UI.
- Standalone apps in `cloud-scraper/` and other non-canonical directories.
- `archive/` contains all historical docs, plans, and reports moved during the 2026-02-08 cleanup.
