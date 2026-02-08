# AUTH_INVENTORY.md (Updated 2026-02-08)

Status: scorched-earth reconstruction mode (no auth, no payments).

## Canonical Identity/Tenant Model (No-Auth)

- No login, no Supabase Auth session, no JWT.
- Tenant boundary is the workspace id (UUID).
  - Frontend persists it in `localStorage` under `raptorflow.workspace_id`.
  - Backend scopes data using the request header `x-workspace-id` (UUID).

## Frontend (Next.js)

- No auth middleware / guards / redirects.
  - `src/middleware.ts` is deleted in the working tree.
- Workspace bootstrap (required for app modules):
  - `src/components/workspace/WorkspaceProvider.tsx`
  - Wired in `src/app/(shell)/layout.tsx`

## Backend (FastAPI)

- No auth middleware/dependencies; requests are not authenticated.
- Multi-tenant scoping is done via `x-workspace-id` header on the canonical routers:
  - `backend/api/v1/workspaces.py` (create/get/update; no auth)
  - `backend/api/v1/campaigns.py` (CRUD; requires `x-workspace-id`)
  - `backend/api/v1/moves.py` (CRUD; requires `x-workspace-id`)
  - `backend/api/v1/foundation.py` (get/save; requires `x-workspace-id`)
  - `backend/api/v1/muse.py` (health/generate; requires `x-workspace-id`)

## Regression Checklist (Must Stay Gone)

If any of these reappear, it is a regression against reconstruction mode:

- Any `useAuth()` flow, auth guard, or redirect to `/login`/`/signup`/`/signin`
- Any Next route handler under `src/app/api/auth/**` or `src/app/api/payments/**`
- Any backend JWT verification middleware or `require_auth` dependency
