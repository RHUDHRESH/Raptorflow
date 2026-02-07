# AUTH_INVENTORY.md (Generated 2026-02-07)

Scope: git-tracked files only (`git ls-files`, `git grep`). Untracked files were not scanned.

## Frontend Auth (Next.js / Supabase)

### Supabase Auth (Primary User Auth)

- Client (browser) Supabase auth:
  - `src/lib/auth-client.ts` (uses `createBrowserClient` from `@supabase/ssr`)
  - `src/lib/supabase/client.ts` (browser client factory)
  - `src/components/auth/AuthProvider.tsx` (session/user lifecycle + routing gates)
  - `src/lib/auth-service.ts` (centralized auth operations; wraps sign-in/out, user load, MFA helpers)

- Server (Next Route Handlers + middleware) Supabase auth:
  - `src/lib/auth-server.ts` (uses `createServerClient` from `@supabase/ssr` + cookie bridging)
  - `src/lib/supabase/server.ts` and `src/lib/supabase-factory.ts` (server client factories)
  - Example route using server auth: `src/app/api/auth/me/route.ts`

### OAuth (Frontend)

- OAuth helpers + provider config:
  - `src/lib/oauth.ts`
  - `src/lib/oauth-providers.ts`
  - `src/lib/oauth-csrf.ts`
  - `src/lib/auth-config.ts` (declares OAuth provider enablement based on env vars)

### MFA / 2FA (Frontend)

There are multiple implementations:

1. Supabase MFA APIs (through Supabase client):
   - `src/lib/auth-service.ts` uses `supabase.auth.mfa.*` (enroll/challenge/unenroll)

2. Custom two-factor endpoint (server-side admin-style flow):
   - `POST /api/auth/two-factor` implemented in `src/app/api/auth/two-factor/route.ts`
   - Uses `serviceAuth.getSupabaseClient()` (`src/lib/auth-service.ts`) and stores settings in `two_factor_settings` table

3. Custom MFA helpers (DB-driven):
   - `src/lib/mfa.ts` (RPC-based MFA helpers)
   - `src/lib/two-factor-auth.ts` (reads/writes `user_mfa` table)

4. Admin MFA route (currently disabled):
   - `src/app/api/admin/mfa/setup/route.ts` returns `503` and does not perform setup/verification/disable

### Session Management (Frontend)

- Next Route Handler:
  - `src/app/api/auth/session-management/route.ts` currently returns "not available in simple mode" responses (no persistent session tracking).

## Edge/Middleware Auth Gates (Next.js)

### Global Middleware Session Validation + Profile Gate

- `src/middleware.ts`:
  - Validates Supabase session using `createServerAuth(...)` from `src/lib/auth-server.ts`
  - Applies rate limiting + security headers
  - For authenticated requests, calls backend profile verification:
    - `GET {BACKEND_URL}/api/v1/auth/verify-profile`
    - Adds headers: `Cookie`, `Authorization`, `X-User-Id`, `X-Workspace-Id`, `X-User-Email`
    - Optionally adds `X-Internal-Token` from `process.env.INTERNAL_API_TOKEN`

Implication:
- The backend is expected to accept a header-based internal token for privileged/automation calls, but the enforcement code appears to live in untracked backend modules (see below).

## Backend Auth (FastAPI)

### JWT Middleware (Supabase JWT)

- `backend/app/auth_middleware.py`:
  - `JWTAuthMiddleware` verifies `Authorization: Bearer <token>` using `SUPABASE_JWT_SECRET`
  - Attaches `request.state.user_id`, `request.state.user_email`, `request.state.jwt_payload`, `request.state.access_token`
  - Does not hard-fail missing `Authorization` header (sets user to `None` and continues)
  - Defines public paths including:
    - `/api/v1/auth/login`, `/api/v1/auth/signup`, `/api/v1/auth/callback`, `/api/v1/auth/refresh`

- Workspace context:
  - `WorkspaceContextMiddleware` reads `x-workspace-id` and `x-workspace-slug` headers.

### Dependency-Based Auth Guards

- `backend/app/auth_middleware.py` exports:
  - `require_auth(request)` (raises 401 if `request.state.user_id` missing)
  - `require_workspace(request)` (requires `x-workspace-id`)

- Backend dependencies wiring:
  - `backend/dependencies.py` imports from `api.dependencies` for `get_current_user`, `get_auth_context`, `require_auth`, `require_workspace_id`, etc.
  - **Note:** `api/dependencies.py` is currently untracked (excluded), so the canonical dependency logic cannot be audited from tracked files alone.

### Route-Level HTTPBearer (Multiple Implementations)

Several routers implement their own `HTTPBearer()` parsing, separate from the global JWT middleware:

- `backend/api/v1/agents.py`: `verify_token()` currently checks presence only (TODO: real JWT verification).
- `backend/api/v1/cognitive.py`: `get_current_user()` returns a mock user object from bearer credentials.
- `backend/api/v1/sessions.py`: derives `user_id` from bearer token string (no verification) but also requires `user_id` via query params.
- `backend/api/v1/payments_enhanced.py`: treats bearer credentials as a payment `session_id` and validates via `PaymentSessionManager`.

### Backend Auth Domain (Supabase Admin + Anon Clients)

- `backend/domains/auth/service.py`:
  - Uses `SUPABASE_URL`
  - Uses `SUPABASE_ANON_KEY` for user auth operations (sign-up/sign-in)
  - Uses `SUPABASE_SERVICE_ROLE_KEY` for admin/profile/workspace operations
- `backend/domains/auth/router.py` exposes `/auth/*` endpoints (router prefix `/auth`)

### API Keys (Backend)

- `backend/api/v1/users.py` includes API key management endpoints under the `/users` router:
  - `GET /me/api-keys`
  - `POST /me/api-keys`
  - `DELETE /me/api-keys/{key_id}`
  - Uses Supabase RPCs like `create_api_key`, `revoke_api_key` (see file for details).

## Service-to-Service Auth (Payments)

### PhonePe OAuth (Not User Auth)

Several Next Route Handlers obtain PhonePe OAuth tokens and then call PhonePe payment APIs:

- `src/app/api/payments/initiate/route.ts` (calls `${PHONEPE_BASE_URL}/v1/oauth/token` then `${PHONEPE_BASE_URL}/pg/v1/pay`)
- `src/app/api/payments/status/[transactionId]/route.ts`
- `src/app/api/payments/verify/route.ts`

## Admin / Elevated Auth

- Admin impersonation token:
  - `src/app/api/admin/impersonate/route.ts` issues a signed JWT (via `jsonwebtoken`) containing `type=impersonation`, `originalUserId`, `targetUserId`, expiry, etc.
  - Secret is `process.env.IMPERSONATION_SECRET` or a per-request random secret (which makes verification impossible unless persisted elsewhere).

## Untracked Auth-Critical Files (Not Scanned)

These appear in `git status` but are not git-tracked, and are referenced by tracked code:

- `backend/api/dependencies.py` (likely the canonical auth_context/current_user implementation)
- `backend/app_factory.py` (app wiring, middleware ordering, router mounting)
- `src/app/api/[...path]/route.ts` (likely implements `/api/proxy/...` used by UI)
