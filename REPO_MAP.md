# REPO_MAP.md (Updated 2026-02-07)

Scope: full working tree (previously untracked critical files now included).

## Commands (Build/Run/Test)

### Frontend (Next.js, repo root)

Source: `package.json`

- Dev: `npm run dev`
- Build: `npm run build`
- Start: `npm run start`
- Lint: `npm run lint`
- Typecheck: `npm run type-check`
- Unit tests: `npm run test` (Vitest)
- E2E tests: `npm run test:e2e` (Playwright)

Notes:
- `package.json` engines: Node `22.x`; README currently says "Node.js 18+" (`README.md`).

### Backend (FastAPI, Python)

Canonical runner: `backend/run_simple.py` (runs `uvicorn` against `backend.main:app`)

- Run (module): `python -m backend.run_simple`
- Run (script): `python backend/run_simple.py`

Notes:
- `backend/main.py` delegates to `backend.app_factory.create_app()` (see ADR-0002).
- All routers are registered via `backend/api/registry.py` (49 routers).
- `backend/start_backend.py` and `backend/run.py` are marked deprecated (see module docstrings).

### Docker / Local Stack

Source: `docker-compose.yml`, `Dockerfile`, `backend/Dockerfile`, `backend/Dockerfile.production`

- Local stack: `docker compose up --build`
  - Services: `backend`, `redis`, `nginx-lb` (SearXNG LB), `searxng-1/2` + `gluetun-1/2` VPN sidecars.

Notes:
- Root `Dockerfile` references `frontend/` and `backend/requirements.txt`, which do not appear in git-tracked files; treat as potentially stale.
- `backend/Dockerfile` runs `gunicorn backend.main:app` on `0.0.0.0:8080` and healthchecks `GET /api/v1/health`.
- `backend/Dockerfile.production` runs `uvicorn backend.main:app` on `0.0.0.0:8080` and healthchecks `GET /health`.

## Entrypoints

### Frontend (Next.js)

- App Router: `src/app/`
- Global middleware (security + session validation): `src/middleware.ts`
- Route handlers (server endpoints): `src/app/api/**/route.ts` (see `API_INVENTORY.md`)

### Backend (FastAPI)

- Canonical ASGI app: `backend/main.py` → `backend/app_factory.create_app()`
- App factory: `backend/app_factory.py` (middleware ordering, router registration, CORS)
- Router registry: `backend/api/registry.py` (single list of all routers)
- Auth middleware: `backend/app/auth_middleware.py` (Supabase JWT verification)
- Auth dependencies: `backend/api/dependencies.py` (`require_auth`, `get_current_user`, context vars)
- Dependency wiring: `backend/dependencies.py` (re-exports from `api.dependencies` + service deps)
- System routes: `backend/api/system.py` (health check, root)
- Minimal app wrapper: `backend/main_minimal.py` (test backward compat)
- Backwards-compat wrappers: `backend/main_new.py`, `backend/main_production.py` (re-export `backend.main:app`)

### Other API Servers (FastAPI) In This Repo

These define standalone `FastAPI()` apps and run via `uvicorn.run(...)` (not necessarily production):

- Cloud scraper services:
  - `cloud-scraper/production_service.py`
  - `cloud-scraper/production_search_service.py`
  - `cloud-scraper/scraper_service.py`
  - `cloud-scraper/enhanced_scraper_service.py`
  - `cloud-scraper/ultra_fast_scraper.py`
  - `cloud-scraper/free_web_search.py` (runs on `8084` in code)
  - `cloud-scraper/visual_intelligence_extractor.py` (runs on `8083` in code)
- Gemini / legacy backends:
  - `minimal_gemini_backend.py` (runs on `8001` in code)
  - `secure_gemini_backend.py` (runs on `8002` in code)
  - `unlimited_backend.py` (runs on `8003` in code)
  - `legacy/unlimited_backend.py` (runs on `8003` in code)
  - `legacy/run_backend.py`
- Backend test/demo servers:
  - `backend/simple_backend.py`
  - `backend/muse_test_server.py`
  - `backend/standalone_phonepe_test.py`
  - `backend/agents/tools/ocr_complex/api.py`

### Supabase Edge Functions (Deno)

- `supabase/functions/phonepe-webhook/index.ts` (uses `Deno.serve(...)`)

## Module Map (High-level)

- Frontend UI: `src/app/`, `src/components/`
- Frontend platform libs: `src/lib/` (auth, Supabase, OAuth, payments, security, monitoring)
- Backend API routers: `backend/api/v1/`, `backend/domains/*/router.py`
- Backend middleware + lifecycle: `backend/app/`, `backend/middleware/`, `backend/core/`
- Backend infrastructure adapters: `backend/infrastructure/`
- Database + migrations: `supabase/` (SQL migrations + edge functions)
- Infra: `docker-compose.yml`, `nginx/`, `config/searxng/`

## API Clients (Callers)

### Browser -> Backend (direct)

Pattern: `fetch(${process.env.NEXT_PUBLIC_API_URL}/api/v1/...)`

Examples:
- `src/app/(shell)/blackbox/page.tsx`
- `src/stores/campaignStore.ts`
- `src/lib/bcm-client.ts`
- `src/components/muse/MuseChat.tsx`

### Browser -> Next API (same-origin)

Pattern: `fetch(/api/...)`

Examples:
- `src/lib/auth-service.ts` calls `GET /api/auth/me`
- `src/lib/api/client.ts` uses base URL `/api` (expects server routes/proxying)
- `src/components/auth/AuthProvider.tsx` calls `/api/proxy/...` (see note below)

### Next API (server) -> Backend / External

- Onboarding routes call backend and may fallback to demo data:
  - e.g. `src/app/api/onboarding/category-paths/route.ts` calls `${API_URL}/api/v1/onboarding/{session_id}/category-paths`
- Payments routes call PhonePe (OAuth token + pay endpoint) and update Supabase tables:
  - `src/app/api/payments/initiate/route.ts`
- PhonePe webhooks:
  - `src/app/api/payments/webhook/route.ts` (Next route handler processing webhook)
  - `src/app/api/webhooks/phonepe/route.ts` forwards to backend webhook endpoint

## ADRs

- `ADRs/ADR-0001-auth-unification.md` — Supabase JWT as single canonical auth
- `ADRs/ADR-0002-entrypoint-consolidation.md` — main.py delegates to app_factory
- `ADRs/ADR-0003-env-consolidation.md` — single .env.example

## Known Gaps (Resolved)

Previously untracked files now included in working tree:

- ✅ `backend/app_factory.py` — now canonical, used by `main.py`
- ✅ `backend/api/dependencies.py` — canonical auth guards
- ✅ `backend/api/registry.py` — canonical router list
- ✅ `backend/api/system.py` — system routes
- ✅ `src/app/api/[...path]/route.ts` — universal proxy with auth forwarding

## Remaining Gaps

- `.env.production` contains real secrets committed to repo — must be rotated and removed from history
- `.env.template`, `env.example`, `.env.universal-gemini` are superseded by `.env.example` — pending deletion
- `tsconfig.json` references `jest` and `node` type definitions that aren't installed
