# API_INVENTORY.md (Updated 2026-02-08)

This inventory describes the *canonical runtime API surface* used by the current Next.js UI.

## Frontend (Next.js) Route Handlers

Present route handlers (`src/app/api/**/route.ts`):

| Route | File | Notes |
| --- | --- | --- |
| `/api/*` (proxy; recommended base: `/api/proxy/v1/*`) | `src/app/api/[...path]/route.ts` | Proxies requests to backend `/api/v1/*` (see `src/services/http.ts`) |

There are no other supported Next route handlers. Auth/onboarding/payments handlers were deleted.

## Backend (FastAPI) Active Routes (Registered)

The canonical backend mounts:

- System routes: `backend/api/system.py`
  - `GET /`
  - `GET /health`
  - Also available under `/api/*` as `GET /api/` and `GET /api/health`
- API routes: registered via `backend/api/registry.py` and included in `backend/app_factory.py`
  - Canonical prefix: `/api/*`
  - Compatibility prefix: `/api/v1/*` (same routers)

### Workspaces (No Auth)

Prefix: `/api/workspaces`

- `POST /api/workspaces/` (create workspace)
- `GET /api/workspaces/{workspace_id}`
- `PATCH /api/workspaces/{workspace_id}`

### Campaigns (Scoped By Tenant)

Prefix: `/api/campaigns` (requires header `x-workspace-id`)

- `GET /api/campaigns/`
- `POST /api/campaigns/`
- `GET /api/campaigns/{campaign_id}`
- `PATCH /api/campaigns/{campaign_id}`
- `DELETE /api/campaigns/{campaign_id}`

### Moves (Scoped By Tenant)

Prefix: `/api/moves` (requires header `x-workspace-id`)

- `GET /api/moves/`
- `POST /api/moves/`
- `PATCH /api/moves/{move_id}`
- `DELETE /api/moves/{move_id}`

### Foundation (Scoped By Tenant)

Prefix: `/api/foundation` (requires header `x-workspace-id`)

- `GET /api/foundation/`
- `PUT /api/foundation/`

### Muse (Scoped By Tenant)

Prefix: `/api/muse` (requires header `x-workspace-id`)

- `GET /api/muse/health`
- `POST /api/muse/generate`

## Legacy Routers / Duplicate API Layers

Historical router modules and payment/auth API layers were removed during scorched-earth reconstruction.
Only the routers registered by `backend/api/registry.py` are considered supported.

Any code path related to auth, onboarding, or payments should be treated as legacy and is a deletion target.
- `cloud-scraper/free_web_search.py`
- `cloud-scraper/visual_intelligence_extractor.py`

Previously-present alternate backend entrypoints were deleted during reconstruction:

- `minimal_gemini_backend.py` (deleted)
- `secure_gemini_backend.py` (deleted)
- `unlimited_backend.py` (deleted)
