# AUTH_INVENTORY.md (Updated 2026-02-07)

Scope: full working tree. See ADR-0001-auth-unification.md for the consolidation decision.

## Canonical Auth Flow (Post-Consolidation)

```
Browser → Supabase Auth (JWT) → Next.js middleware → proxy route → FastAPI
                                                        ↓
                                              JWTAuthMiddleware
                                                        ↓
                                              RequestContextMiddleware
                                                        ↓
                                              require_auth() dependency
```

**Single mechanism:** Supabase JWT via `Authorization: Bearer <token>`.

## Frontend Auth (Next.js / Supabase)

### Supabase Auth (Canonical)

- Client (browser):
  - `src/lib/auth-client.ts` (`createBrowserClient` from `@supabase/ssr`)
  - `src/lib/supabase/client.ts` (browser client factory)
  - `src/components/auth/AuthProvider.tsx` (session/user lifecycle + routing gates)
  - `src/lib/auth-service.ts` (centralized auth operations; wraps sign-in/out, user load, MFA)

- Server (Next Route Handlers + middleware):
  - `src/lib/auth-server.ts` (`createServerClient` from `@supabase/ssr` + cookie bridging)
  - `src/lib/supabase/server.ts` and `src/lib/supabase-factory.ts` (server client factories)

### OAuth (Frontend)

- `src/lib/oauth.ts`, `src/lib/oauth-providers.ts`, `src/lib/oauth-csrf.ts`
- `src/lib/auth-config.ts` (provider enablement via env vars)

### MFA (Consolidated on Supabase)

**Canonical:** `src/lib/auth-service.ts` uses `supabase.auth.mfa.*` (enroll/challenge/unenroll)

**Deprecated (return 410 Gone):**
- `src/app/api/admin/mfa/setup/route.ts` — was 503 stub, now returns 410 with migration instructions
- `src/lib/mfa.ts` — RPC-based helpers (to be removed)
- `src/lib/two-factor-auth.ts` — DB-driven `user_mfa` table (to be removed)
- `src/app/api/auth/two-factor/route.ts` — custom endpoint (to be removed)

### Session Management (Consolidated on Supabase)

**Canonical:** `supabase.auth.getSession()` / `signOut()` / `refreshSession()`

**Deprecated (returns 410 Gone):**
- `src/app/api/auth/session-management/route.ts` — was no-op stub, now returns 410

## Edge/Middleware Auth Gates (Next.js)

### Global Middleware

- `src/middleware.ts`:
  - Validates Supabase session via `createServerAuth(...)` from `src/lib/auth-server.ts`
  - Rate limiting + security headers
  - Profile verification: `GET {BACKEND_URL}/api/v1/auth/verify-profile`
  - Forwards: `Cookie`, `Authorization`, `X-User-Id`, `X-Workspace-Id`, `X-User-Email`, `X-Internal-Token`

### Universal Proxy Route

- `src/app/api/[...path]/route.ts`:
  - Forwards `Authorization` header (Supabase JWT) to backend
  - Forwards `Cookie`, context headers (`x-user-id`, `x-workspace-id`, etc.)
  - Adds `X-Internal-Token` for service-to-service auth
  - 30s timeout, 502 on backend unreachable

## Backend Auth (FastAPI)

### JWT Middleware (Supabase JWT) — Layer 1

- `backend/app/auth_middleware.py`:
  - `JWTAuthMiddleware` verifies `Authorization: Bearer <token>` using `SUPABASE_JWT_SECRET`
  - Sets `request.state.user_id`, `.user_email`, `.jwt_payload`, `.access_token`
  - Soft-fails (sets user to `None`) for unauthenticated requests
  - Public paths: `/api/v1/auth/login`, `/signup`, `/callback`, `/refresh`

- `WorkspaceContextMiddleware` reads `x-workspace-id` and `x-workspace-slug` headers

### Auth Dependencies — Layer 2

- `backend/api/dependencies.py` (canonical):
  - `require_auth()` — raises 401 if no authenticated user in context
  - `get_current_user()` — returns user dict from context vars
  - `get_auth_context()` — full auth context (user + workspace + token)
  - `get_current_user_id()`, `get_current_workspace_id()` — convenience extractors
  - `get_supabase_admin()`, `get_supabase_client()` — Supabase client accessors
  - `RequestContextMiddleware` — populates context vars from request state

- `backend/dependencies.py` re-exports all of the above + adds service dependencies (DB, Redis, etc.)

### Per-Router Auth (CONSOLIDATED — no more custom HTTPBearer)

All routers now use `Depends(require_auth)` from `backend/api/dependencies.py`:

- `backend/api/v1/agents.py` — was custom `verify_token()`, now `require_auth`
- `backend/api/v1/cognitive.py` — was mock `get_current_user()`, now canonical
- `backend/api/v1/sessions.py` — was token-string splitting, now `require_auth`
- `backend/api/v1/payments_enhanced.py` — payment session ID moved to `X-Payment-Session` header (NOT `Authorization`)

### Backend Auth Domain (Supabase Admin + Anon Clients)

- `backend/domains/auth/service.py`:
  - `SUPABASE_ANON_KEY` for user auth operations (sign-up/sign-in)
  - `SUPABASE_SERVICE_ROLE_KEY` for admin/profile/workspace operations
- `backend/domains/auth/router.py` exposes `/auth/*` endpoints

### API Keys (Backend)

- `backend/api/v1/users.py`: `/me/api-keys` CRUD via Supabase RPCs

## Service-to-Service Auth

### Internal Token

- `X-Internal-Token` header, validated in `backend/api/dependencies.py` (`_allow_header_auth`)
- Set by Next.js middleware and proxy route from `process.env.INTERNAL_API_TOKEN`

### PhonePe OAuth (Not User Auth)

- `src/app/api/payments/initiate/route.ts` (PhonePe OAuth token → pay endpoint)
- `src/app/api/payments/status/[transactionId]/route.ts`
- `src/app/api/payments/verify/route.ts`

## Admin / Elevated Auth

- Admin impersonation: `src/app/api/admin/impersonate/route.ts`
  - Issues JWT with `type=impersonation` via `jsonwebtoken`
  - **Known issue:** uses per-request random secret (unverifiable). Must be replaced with `IMPERSONATION_SECRET` env var or removed.

## Previously Untracked Files (Now Tracked)

- ✅ `backend/api/dependencies.py` — canonical auth guards
- ✅ `backend/app_factory.py` — app wiring with correct middleware ordering
- ✅ `src/app/api/[...path]/route.ts` — universal proxy with auth forwarding
