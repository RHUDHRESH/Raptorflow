# Raptorflow Backend (Reconstruction Mode)

This backend is the canonical FastAPI API used by the current Next.js frontend.

Status: no-auth, no-payments. Tenant boundary is a workspace id passed via `x-workspace-id`.

## Run

From repo root (recommended):

```powershell
.\.venv\Scripts\python backend\run_simple.py
```

Health:

```powershell
curl http://localhost:8000/health
```

## Canonical API Surface

Routers are registered in `backend/api/registry.py` and mounted by `backend/app_factory.py`.

System:

- `GET /`
- `GET /health`

API (canonical prefix: `/api/*`):

- Workspaces: `POST /api/workspaces`, `GET/PATCH /api/workspaces/{id}`
- Campaigns: `GET/POST /api/campaigns`, `GET/PATCH/DELETE /api/campaigns/{id}` (requires `x-workspace-id`)
- Moves: `GET/POST /api/moves`, `PATCH/DELETE /api/moves/{id}` (requires `x-workspace-id`)
- Foundation: `GET/PUT /api/foundation` (requires `x-workspace-id`)
- Muse: `GET /api/muse/health`, `POST /api/muse/generate` (requires `x-workspace-id`, optional integration)

Compatibility:

- `/api/v1/*` is supported via path rewrite to `/api/*` when `ENABLE_LEGACY_API_PATHS=true`.

## Environment Variables

Required (database):

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Optional:

- `VERTEX_AI_PROJECT_ID`, `VERTEX_AI_LOCATION`, `VERTEX_AI_MODEL` (Muse/AI)
- `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN` (caching)
- `RESEND_API_KEY`, `EMAIL_FROM` (email)
- `SENTRY_DSN` (monitoring)

See `backend/.env.example`.

