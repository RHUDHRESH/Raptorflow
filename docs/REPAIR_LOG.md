# Repair Log

## PR1 - Auth end-to-end (2026-01-29)

Root cause:
- Client auth checks relied on `GET /api/auth/me`, but the route did not exist (404), causing auth state to be reported as unauthenticated.
- Middleware session refresh wrote cookies to the request object; refreshed tokens were not persisted on the response.

Fix:
- Added `src/app/api/auth/me/route.ts` to validate auth (cookie or bearer token) and return the current user.
- Updated middleware auth wiring to use `src/lib/auth-server.ts` and persist refreshed cookies onto the response.

Verification:
- Before fix: `GET http://localhost:3000/api/auth/me` returned `404`.
- After fix: `AUTH_SMOKE_ALLOW_RESET=true DOTENV_CONFIG_PATH=.env.local AUTH_SMOKE_BASE_URL=http://localhost:3000 npm run auth:smoke` (requires local Next dev server running and Supabase access).
