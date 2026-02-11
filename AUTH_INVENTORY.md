# AUTH_INVENTORY.md

Updated: 2026-02-11

Status: **no-auth reconstruction mode** (no login, no payments).

## Current Identity Model

- No user login/session enforcement.
- No JWT validation middleware.
- Tenant boundary is `x-workspace-id` (workspace UUID).
- Frontend persists workspace id in local storage key `raptorflow.workspace_id`.

## Frontend

- No auth guards/redirects are part of canonical app flow.
- Workspace bootstrap is handled by:
  - `src/components/workspace/WorkspaceProvider.tsx`
  - wired in `src/app/(shell)/layout.tsx`

## Backend

- No `require_auth` dependency in canonical router stack.
- Workspace-scoped routes require `x-workspace-id`:
  - `backend/api/v1/campaigns.py`
  - `backend/api/v1/moves.py`
  - `backend/api/v1/foundation.py`
  - `backend/api/v1/muse.py`
  - `backend/api/v1/context.py`
  - `backend/api/v1/bcm_feedback.py`
- Workspace CRUD remains open (no header required):
  - `backend/api/v1/workspaces.py`

## Regression Checklist

If any of these reappear, treat as regression:

- `useAuth()` hooks or redirects to `/login`, `/signup`, `/signin`
- Next handlers under `src/app/api/auth/**` or `src/app/api/payments/**`
- Backend JWT verification middleware/dependencies on canonical routes
- PhonePe payment integration restored into active runtime flow
