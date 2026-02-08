# REPO_MAP.md (Updated 2026-02-09, complete restructure)

Goal: keep a single, working, no-auth path through the app. Everything else is archived.

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
- Canonical schema (11+ tables):
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
  - `bcm_memories` (accumulated learning)
  - `bcm_generation_log` (tracks all outputs for reflection)

BCM Pipeline (Cognitive Identity System - ADR-0005):

- **Core Schema:** `backend/schemas/business_context.py`
- **AI Synthesis:** `backend/services/bcm_synthesizer.py`
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
- **Frontend:**
  - Types: `src/types/bcm.ts`
  - Service: `src/services/bcm.service.ts` + `src/services/feedback.service.ts`
  - Store: `src/stores/bcmStore.ts`
  - UI: `src/components/bcm/BCMStatusPanel.tsx`, `src/components/muse/MuseChat.tsx`

Tenant model:

- No login / no JWT.
- Tenant boundary is workspace id (UUID) provided via request header: `x-workspace-id`.

Moves deep-links:

- Wizard: `/moves?new=1` or `/moves?create=true`
- Detail modal: `/moves?moveId=<uuid>`

## Folder Structure

```
/                        ← Root MDs: AGENTS, README, REPO_MAP, API_INVENTORY, AUTH_INVENTORY, MODULE_USAGE_REPORT
├── ADRs/                ← Architectural Decision Records
├── archive/             ← All archived/historical artifacts
│   ├── cloud-scraper/   ← Archived standalone scraper system (180+ files, disconnected)
│   ├── docs/            ← Historical docs, architecture, security audits
│   ├── screenshots/     ← Historical UI screenshots
│   └── test-artifacts/  ← Old test reports, logs, debug scripts, build outputs
├── backend/             ← Canonical FastAPI backend
│   ├── api/             ← Route handlers (v1/)
│   ├── app/             ← Lifespan, middleware
│   ├── config/          ← Settings (Pydantic)
│   ├── core/            ← Service clients: supabase_mgr, redis_mgr, storage_mgr
│   ├── services/        ← Business logic: BCM, Vertex AI, email
│   ├── schemas/         ← Pydantic schemas
│   ├── templates/email  ← Jinja2 email templates
│   └── tests/           ← Backend tests (unit/, integration/, verification/)
├── docs/                ← Canonical documentation
│   └── archive/         ← Archived project docs (conductor/, etc.)
├── scripts/             ← Build/deploy/audit scripts
├── src/                 ← Next.js frontend (App Router)
│   ├── app/             ← Next.js routes
│   │   ├── (shell)/     ← Authenticated app (dashboard, campaigns, moves, etc.)
│   │   ├── api/         ← API proxy route
│   │   └── features/    ← Marketing pages
│   ├── components/      ← All React components (NO loose files at root)
│   │   ├── analytics/   ← Analytics visualizations
│   │   ├── animation/   ← Page transition animations
│   │   ├── bcm/         ← Business Context status panel
│   │   ├── compass/     ← Compass logo/branding
│   │   ├── dashboard/   ← Dashboard widgets
│   │   ├── effects/     ← Visual effects (cursor, magnetic, parallax, etc.)
│   │   ├── error/       ← Error boundaries
│   │   ├── foundation/  ← Foundation page components
│   │   ├── landing/     ← Landing page sections
│   │   ├── moves/       ← Moves CRUD components
│   │   ├── muse/        ← Muse AI chat
│   │   ├── notifications/← Toast/notification components
│   │   ├── positioning/ ← Competitive positioning visualizations
│   │   ├── providers/   ← React context providers
│   │   ├── shell/       ← App shell (sidebar, header)
│   │   ├── ui/          ← Design system (Blueprint + shadcn primitives)
│   │   └── workspace/   ← Workspace provider
│   ├── lib/             ← Utilities & helpers
│   ├── services/        ← API client services
│   ├── stores/          ← Zustand state management
│   ├── styles/          ← Global styles
│   ├── test/            ← Frontend test utilities
│   └── types/           ← TypeScript type definitions
├── supabase/            ← Database migrations
└── public/              ← Static assets
```

## What Was Removed (2026-02-09 Restructure, ADR-0006)

Orphaned modules (zero imports from main app):
- `cloud-scraper/` → `archive/cloud-scraper/` (180+ files, standalone scraper)
- `cognitive/` → DELETED (empty module, only `__init__.py`)
- `conductor/` → `docs/archive/conductor/` (documentation only, no code)
- `config/` at root → DELETED (searxng config, unused)
- `gcp/`, `nginx/` at root → DELETED (legacy infrastructure)
- `components/` at root → DELETED (legacy)

Orphaned frontend components (zero imports):
- `AgentChat.tsx`, `AgentManagement.tsx`, `WorkflowBuilder.tsx` (18-27KB each)
- `InteractiveHero.tsx`, `Button.jsx`, `Card.jsx`, `Input.jsx`
- `Magnetic.jsx`, `Preloader.jsx`, `RevealText.jsx`, `ScrambleText.jsx`, `SpotlightCard.jsx`

Duplicate components (kept canonical version):
- `CustomCursor` — kept `effects/CustomCursor.tsx`, deleted `ui/` and root `.jsx` versions
- `MagneticButton` — kept `effects/MagneticButton.tsx`, deleted `ui/` version
- `CompassLogo` — kept `compass/CompassLogo.tsx`, deleted `ui/` version

Root clutter moved to `archive/test-artifacts/`:
- 46+ `test_*.py` files → organized into `backend/tests/{unit,integration,verification}/`
- 20+ `.json` test reports
- 10+ build log `.txt` files
- Debug/verify/red-team Python scripts
- `.db` database files, `.html` test pages, screenshots

Duplicate config files removed:
- `.eslintrc.cjs` (kept `eslint.config.js`)
- `eslint.config.mjs` (kept `eslint.config.js`)
- `tailwind.config.cjs` (kept `tailwind.config.js`)
- `vitest.config.js` (kept `vitest.config.ts`)
- `env.example` (kept `.env.example`)
- `.gitignore.prod` (kept `.gitignore`)
