# REPO_MAP.md (Updated 2026-02-08)

Goal: keep a single, working, no-auth path through the app. Everything else is legacy.

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

BCM Pipeline:

- Fixtures: `backend/fixtures/business_context_*.json` (3 diverse fake businesses)
- Pydantic schemas: `backend/schemas/business_context.py`
- Reducer (pure function): `backend/services/bcm_reducer.py`
- Service (Supabase CRUD): `backend/services/bcm_service.py`
- Seed script: `scripts/seed_bcm.py`
- Frontend types: `src/types/bcm.ts`
- Frontend service: `src/services/bcm.service.ts`
- Frontend store: `src/stores/bcmStore.ts`
- Dashboard panel: `src/components/bcm/BCMStatusPanel.tsx`

Tenant model:

- No login / no JWT.
- Tenant boundary is workspace id (UUID) provided via request header: `x-workspace-id`.

Moves deep-links:

- Wizard: `/moves?new=1` or `/moves?create=true`
- Detail modal: `/moves?moveId=<uuid>`

## Legacy / Not Canonical

This repo contains many legacy apps, services, scripts, and docs. They are not part of the canonical runtime and are candidates for deletion if broken/misleading:

- Extra Next routes under `src/app/*` that are not linked from the canonical UI.
- Previously present parallel backend layers (Node/Express, payments/webhooks) have been deleted as part of reconstruction.
- Additional standalone FastAPI apps scattered across `cloud-scraper/*` and other non-canonical directories.
