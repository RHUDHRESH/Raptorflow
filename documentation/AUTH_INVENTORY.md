# Auth Inventory

Current authentication model and integration points.

## Runtime Model

- Reconstruction mode is active for product flows.
- Workspace isolation is enforced by `x-workspace-id` header.
- Global login gate is intentionally not required for core app usage.

## Auth Components

- `backend/services/auth_service.py`
  - Integrates with Supabase Auth for token verification.
  - Uses `SUPABASE_URL` plus `SUPABASE_ANON_KEY` or `SUPABASE_SERVICE_ROLE_KEY`.
- `backend/api/v1/auth.py`
  - `POST /api/auth/verify` verifies bearer/access token.
  - `GET /api/auth/health` reports auth provider reachability.
- `src/app/api/[...path]/route.ts`
  - Proxies API requests.
  - Forwards only explicit headers (`x-workspace-id`, `x-request-id`, `x-idempotency-key`).

## Workspace Isolation

- `src/components/workspace/WorkspaceProvider.tsx`
  - Creates/loads workspace and stores workspace id locally.
  - Redirects to onboarding until BCM-ready onboarding is complete.
- `src/services/http.ts`
  - Adds `x-workspace-id` to API calls when `workspaceId` is available.

## Integration Health Surface

- `GET /api/ops/services`:
  - `configured_integrations.supabase_auth` indicates auth env readiness.
  - `runtime_services.auth_service` indicates runtime auth health.
- `GET /api/ops/ai-architecture`:
  - Includes auth service runtime status in architecture response.

## Known Constraints

- Auth verification is explicit opt-in per endpoint; no global auth middleware.
- Service role credentials must stay server-side only and never be exposed in client bundles.
