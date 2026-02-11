# AUTH_INVENTORY.md

Updated: 2026-02-09.

Status: **no-auth reconstruction mode** (no login, no payments). See ADR-0004.

## Current Identity Model

- No login, no Supabase Auth session, no JWT.
- Tenant boundary is the **workspace ID** (UUID).
  - Frontend persists it in `localStorage` under `raptorflow.workspace_id`.
  - Backend scopes all data via the request header `x-workspace-id`.

## Frontend

- No auth middleware, guards, or redirects.
- Workspace bootstrap (required for app modules):
  - `src/components/workspace/WorkspaceProvider.tsx`
  - Wired in `src/app/(shell)/layout.tsx`

## Backend

- No auth middleware or dependencies. Requests are unauthenticated.
- Multi-tenant scoping via `x-workspace-id` header on all canonical routers:
  - `backend/api/v1/campaigns.py`
  - `backend/api/v1/moves.py`
  - `backend/api/v1/foundation.py`
  - `backend/api/v1/muse.py`
  - `backend/api/v1/context.py`
  - `backend/api/v1/bcm_feedback.py`
- Workspace CRUD (`backend/api/v1/workspaces.py`) does not require a header.

## Regression Checklist

If any of the following reappear, it is a regression:

- Any `useAuth()` hook, auth guard, or redirect to `/login`/`/signup`/`/signin`
- Any Next route handler under `src/app/api/auth/**` or `src/app/api/payments/**`
- Any backend JWT verification middleware or `require_auth` dependency
- Any PhonePe payment integration code
