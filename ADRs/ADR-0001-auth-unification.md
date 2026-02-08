# ADR-0001: Unify Authentication on Supabase JWT

## Status
Superseded by ADR-0004 (No-Auth/No-Payments Reconstruction Mode)

## Notes
This ADR is kept for historical context. In reconstruction mode, auth was intentionally removed.

## Date
2026-02-07

## Context

The codebase has accumulated **6+ distinct auth mechanisms**:

1. **Global JWT middleware** (`backend/app/auth_middleware.py`) — verifies `Authorization: Bearer <token>` using `SUPABASE_JWT_SECRET`. Soft-fails (sets user to `None`).
2. **Canonical dependency guards** (`backend/api/dependencies.py`) — `require_auth()`, `get_current_user()`, `get_auth_context()` backed by context-vars and Supabase profile lookups.
3. **Per-router HTTPBearer** — at least 5 routers implement their own `HTTPBearer()` parsing:
   - `backend/api/v1/agents.py` — `verify_token()` checks presence only (TODO comment: "real JWT verification").
   - `backend/api/v1/cognitive.py` — `get_current_user()` returns a mock user from bearer credentials.
   - `backend/api/v1/sessions.py` — derives `user_id` from bearer string (no verification) + requires `user_id` query param.
   - `backend/api/v1/payments_enhanced.py` — treats bearer as a payment `session_id`.
   - `backend/api/v1/payments/analytics.py` — another HTTPBearer instance.
4. **Header-based internal auth** — `X-Internal-Token` / `X-RF-Internal-Key` for service-to-service calls.
5. **Frontend MFA** — 4 separate implementations (Supabase MFA API, custom two-factor endpoint, DB-driven MFA helpers, disabled admin MFA route returning 503).
6. **Admin impersonation** — issues JWTs with a per-request random secret (unverifiable).

This violates AGENTS.md rule #3 ("No parallel auth flows").

## Decision

**Supabase JWT is the single canonical user authentication mechanism.**

All backend routes that need authentication MUST use `require_auth()` from `backend/api/dependencies.py` (which reads from the context set by `JWTAuthMiddleware`). Per-router `HTTPBearer()` instances are removed and replaced with `Depends(require_auth)`.

### Auth hierarchy

| Layer | Mechanism | Module |
|-------|-----------|--------|
| User auth | Supabase JWT via `Authorization: Bearer` | `backend/app/auth_middleware.py` → `backend/api/dependencies.py` |
| Service-to-service | `X-Internal-Token` header (validated in `_allow_header_auth`) | `backend/api/dependencies.py` |
| Payment session | Separate concern — NOT auth. Payment session IDs validated by `PaymentSessionManager`, not by auth middleware. | `backend/api/v1/payments_enhanced.py` |

### MFA

Consolidate on Supabase's built-in MFA (`supabase.auth.mfa.*`). Remove:
- `src/app/api/auth/two-factor/route.ts` (custom endpoint)
- `src/lib/two-factor-auth.ts` (DB-driven)
- `src/app/api/admin/mfa/setup/route.ts` (disabled 503 stub)

Keep only `src/lib/auth-service.ts` which wraps `supabase.auth.mfa.*`.

### Admin impersonation

The current implementation uses a per-request random secret, making verification impossible. This must be replaced with a fixed `IMPERSONATION_SECRET` env var or removed entirely.

## Alternatives Considered

1. **Keep per-router auth** — rejected; leads to inconsistent security posture and makes auditing impossible.
2. **Custom JWT (not Supabase)** — rejected; Supabase is already the canonical user store and auth provider.
3. **API gateway auth** — rejected; adds infrastructure complexity without benefit at current scale.

## Consequences

- All routes use a single auth path, making security audits tractable.
- Per-router `HTTPBearer()` code is deleted (not just deprecated).
- `payments_enhanced.py` must separate payment session validation from user auth.
- Frontend MFA code is simplified to one implementation.
- Breaking change for any client that sends a payment session ID as a Bearer token — those clients must switch to a dedicated header or body field.
