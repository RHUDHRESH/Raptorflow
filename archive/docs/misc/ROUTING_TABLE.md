# ROUTING_TABLE.md (Generated 2026-02-07)

Documents the old → new endpoint mapping after entrypoint consolidation (ADR-0002).

## How Routing Works Now

All routers are registered in `backend/api/registry.py` and mounted by `backend/app_factory.py` under:

- **`/api`** — canonical prefix (via `include_universal(app, prefix="/api")`)
- **`/api/v1`** — legacy alias (via `include_legacy_v1`, enabled by `ENABLE_LEGACY_V1=true`)
- **`/api/legacy`** — experimental legacy (disabled by default)

Legacy path rewriting (`LegacyApiPathMiddleware`) rewrites `/api/v1/*` → `/api/*` when `ENABLE_LEGACY_API_PATHS=true`.

## Router Prefix Inventory

Routers with `/v1/` in their prefix will be double-prefixed when mounted under `/api`:
e.g. `prefix="/v1/foundation"` → `/api/v1/foundation`. This is intentional for backward compat.

| Router Module | Router Prefix | Effective Path (under /api) | Notes |
|---|---|---|---|
| `domains/auth/router.py` | `/auth` | `/api/auth/*` | Domain auth (Supabase) |
| `v1/admin.py` | `/admin` | `/api/admin/*` | |
| `v1/agents.py` | `/agents` | `/api/agents/*` | Auth: `require_auth` |
| `v1/ai_proxy.py` | `/ai` | `/api/ai/*` | |
| `v1/analytics.py` | `/analytics` | `/api/analytics/*` | |
| `v1/approvals.py` | `/approvals` | `/api/approvals/*` | |
| `v1/assets.py` | `/v1/assets` | `/api/v1/assets/*` | Has v1 in prefix |
| `v1/bcm_endpoints.py` | `/bcm` | `/api/bcm/*` | |
| `v1/blackbox.py` | `/blackbox` | `/api/blackbox/*` | |
| `v1/blackbox_learning.py` | `/v1/blackbox/learning` | `/api/v1/blackbox/learning/*` | Has v1 in prefix |
| `v1/blackbox_memory.py` | `/v1/blackbox/memory` | `/api/v1/blackbox/memory/*` | Has v1 in prefix |
| `v1/blackbox_roi.py` | `/v1/blackbox/roi` | `/api/v1/blackbox/roi/*` | Has v1 in prefix |
| `v1/blackbox_telemetry.py` | `/v1/blackbox/telemetry` | `/api/v1/blackbox/telemetry/*` | Has v1 in prefix |
| `v1/business_contexts.py` | `/business-contexts` | `/api/business-contexts/*` | |
| `v1/campaigns.py` | `/v1/campaigns` | `/api/v1/campaigns/*` | Has v1 in prefix |
| `v1/config.py` | `/config` | `/api/config/*` | |
| `v1/context.py` | `/context` | `/api/context/*` | |
| `v1/council.py` | `/council` | `/api/council/*` | |
| `v1/daily_wins.py` | `/daily-wins` | `/api/daily-wins/*` | |
| `v1/dashboard.py` | `/dashboard` | `/api/dashboard/*` | |
| `v1/evolution.py` | `/evolution` | `/api/evolution/*` | |
| `v1/feedback.py` | `/v1/feedback` | `/api/v1/feedback/*` | Has v1 in prefix |
| `v1/foundation.py` | `/v1/foundation` | `/api/v1/foundation/*` | Has v1 in prefix |
| `v1/graph.py` | `/graph` | `/api/graph/*` | |
| `v1/health_comprehensive.py` | `/health` | `/api/health/*` | |
| `v1/icps.py` | `/icps` | `/api/icps/*` | |
| `v1/infra_health.py` | `/infra` | `/api/infra/*` | |
| `v1/matrix.py` | `/v1/matrix` | `/api/v1/matrix/*` | Has v1 in prefix |
| `v1/memory.py` | `/memory` | `/api/memory/*` | |
| `v1/metrics.py` | `/metrics` | `/api/metrics/*` | |
| `v1/moves.py` | `/v1/moves` | `/api/v1/moves/*` | Has v1 in prefix |
| `v1/muse.py` | `/v1/muse` | `/api/v1/muse/*` | Has v1 in prefix |
| `v1/ocr.py` | `/ocr` | `/api/ocr/*` | |
| `v1/onboarding.py` | `/onboarding` | `/api/onboarding/*` | |
| `v1/payments.py` | `/v1/payments` | `/api/v1/payments/*` | Has v1 in prefix |
| `v1/payments_enhanced.py` | (empty) | legacy only | Not in canonical registry; mounted under `/api/legacy/` when `ENABLE_LEGACY_EXPERIMENTAL_ROUTES=true` |
| `v1/radar.py` | `/v1/radar` | `/api/v1/radar/*` | Has v1 in prefix |
| `v1/radar_analytics.py` | `/v1/radar/analytics` | `/api/v1/radar/analytics/*` | Has v1 in prefix |
| `v1/radar_notifications.py` | `/v1/radar/notifications` | `/api/v1/radar/notifications/*` | Has v1 in prefix |
| `v1/radar_scheduler.py` | `/v1/radar/scheduler` | `/api/v1/radar/scheduler/*` | Has v1 in prefix |
| `v1/search.py` | `/search` | `/api/search/*` | |
| `v1/sessions.py` | `/sessions` | `/api/sessions/*` | Auth: `require_auth` |
| `v1/storage.py` | `/storage` | `/api/storage/*` | |
| `v1/synthesis.py` | `/v1/synthesis` | `/api/v1/synthesis/*` | Has v1 in prefix |
| `v1/titan.py` | `/titan` | `/api/titan/*` | |
| `v1/usage.py` | `/usage` | `/api/usage/*` | |
| `v1/users.py` | `/users` | `/api/users/*` | |
| `v1/workspaces.py` | `/workspaces` | `/api/workspaces/*` | |

## Deprecated Frontend Routes (Return 410 Gone)

| Old Route | Status | Migration |
|---|---|---|
| `POST/PUT/DELETE /api/admin/mfa/setup` | 410 Gone | Use `supabase.auth.mfa.*` |
| `POST/GET /api/auth/session-management` | 410 Gone | Use `supabase.auth.getSession/signOut/refreshSession` |

### Endpoint Collisions Resolved

| Router | Original Path | Collision | Resolution |
|---|---|---|---|
| `v1/onboarding.py` | `GET /progress` | Defined twice (Redis vs DB) | Redis: `/onboarding/{id}/progress`<br>DB: `/onboarding/{id}/progress/persistent` |

## Known Issues

1. ~~**`v1/memory.py`** double `/api` prefix~~ — **RESOLVED**: prefix is now `/memory`.
2. **`v1/payments_enhanced.py`** has `prefix=""` — not mounted canonically; only available under `/api/legacy/payments-enhanced/` when `ENABLE_LEGACY_EXPERIMENTAL_ROUTES=true`. Its routes (`/initiate`, `/webhook`, `/refund`) collide with `payments_v2` and `payments_v2_secure` if both are enabled in legacy mode.
3. **`v1/payments_v2.py`** and **`v1/payments_v2_secure.py`** also have `prefix=""` — same collision risk. These are legacy-only (not in canonical registry).
4. **Mixed prefix styles**: some routers include `/v1/` in their prefix (e.g. `/v1/foundation`), others don't (e.g. `/agents`). When mounted under `/api`, the former become `/api/v1/foundation` while the latter become `/api/agents`. This inconsistency should be normalized in a future pass.

## Proxy Route Path Resolution (Frontend → Backend)

`src/app/api/[...path]/route.ts` resolves paths as:

```
/api/proxy/v1/agents/execute  →  /api/v1/agents/execute   (strips "proxy", keeps v1)
/api/proxy/v2/something       →  /api/v2/something        (strips "proxy", keeps v2)
/api/proxy/agents/execute     →  /api/v1/agents/execute    (strips "proxy", adds v1)
/api/v1/agents/execute        →  /api/v1/agents/execute    (keeps v1 as-is)
/api/agents/execute           →  /api/v1/agents/execute    (adds v1)
```
