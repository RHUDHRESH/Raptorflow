# API_INVENTORY.md (Generated 2026-02-07)

Scope: git-tracked files only (`git ls-files`, `git grep`). Untracked files were not scanned.

## Frontend (Next.js) Route Handlers

### Present Route Handlers (`src/app/api/**/route.ts`)

These are Next.js Route Handlers exposed under `/api/...` (path derived from directory structure).

| Route | File |
| --- | --- |
| `/api/admin/impersonate` | `src/app/api/admin/impersonate/route.ts` |
| `/api/admin/mfa/setup` | `src/app/api/admin/mfa/setup/route.ts` |
| `/api/auth/forgot-password` | `src/app/api/auth/forgot-password/route.ts` |
| `/api/auth/me` | `src/app/api/auth/me/route.ts` |
| `/api/auth/reset-password-production` | `src/app/api/auth/reset-password-production/route.ts` |
| `/api/auth/session-management` | `src/app/api/auth/session-management/route.ts` |
| `/api/auth/two-factor` | `src/app/api/auth/two-factor/route.ts` |
| `/api/auth/verify-email` | `src/app/api/auth/verify-email/route.ts` |
| `/api/billing/dunning` | `src/app/api/billing/dunning/route.ts` |
| `/api/gdpr/data-export` | `src/app/api/gdpr/data-export/route.ts` |
| `/api/health` | `src/app/api/health/route.ts` |
| `/api/me/subscription` | `src/app/api/me/subscription/route.ts` |
| `/api/onboarding/category-paths` | `src/app/api/onboarding/category-paths/route.ts` |
| `/api/onboarding/channel-strategy` | `src/app/api/onboarding/channel-strategy/route.ts` |
| `/api/onboarding/classify` | `src/app/api/onboarding/classify/route.ts` |
| `/api/onboarding/competitor-analysis` | `src/app/api/onboarding/competitor-analysis/route.ts` |
| `/api/onboarding/complete` | `src/app/api/onboarding/complete/route.ts` |
| `/api/onboarding/contradictions` | `src/app/api/onboarding/contradictions/route.ts` |
| `/api/onboarding/create-workspace` | `src/app/api/onboarding/create-workspace/route.ts` |
| `/api/onboarding/current-selection` | `src/app/api/onboarding/current-selection/route.ts` |
| `/api/onboarding/extract` | `src/app/api/onboarding/extract/route.ts` |
| `/api/onboarding/focus-sacrifice` | `src/app/api/onboarding/focus-sacrifice/route.ts` |
| `/api/onboarding/icp-deep` | `src/app/api/onboarding/icp-deep/route.ts` |
| `/api/onboarding/launch-readiness` | `src/app/api/onboarding/launch-readiness/route.ts` |
| `/api/onboarding/market-size` | `src/app/api/onboarding/market-size/route.ts` |
| `/api/onboarding/messaging-rules` | `src/app/api/onboarding/messaging-rules/route.ts` |
| `/api/onboarding/neuroscience-copy` | `src/app/api/onboarding/neuroscience-copy/route.ts` |
| `/api/onboarding/perceptual-map` | `src/app/api/onboarding/perceptual-map/route.ts` |
| `/api/onboarding/positioning` | `src/app/api/onboarding/positioning/route.ts` |
| `/api/onboarding/proof-points` | `src/app/api/onboarding/proof-points/route.ts` |
| `/api/onboarding/provision-storage` | `src/app/api/onboarding/provision-storage/route.ts` |
| `/api/onboarding/reddit-research` | `src/app/api/onboarding/reddit-research/route.ts` |
| `/api/onboarding/select-plan` | `src/app/api/onboarding/select-plan/route.ts` |
| `/api/onboarding/soundbites` | `src/app/api/onboarding/soundbites/route.ts` |
| `/api/onboarding/truth-sheet` | `src/app/api/onboarding/truth-sheet/route.ts` |
| `/api/payments/create-order` | `src/app/api/payments/create-order/route.ts` |
| `/api/payments/initiate` | `src/app/api/payments/initiate/route.ts` |
| `/api/payments/status/[transactionId]` | `src/app/api/payments/status/[transactionId]/route.ts` |
| `/api/payments/verify` | `src/app/api/payments/verify/route.ts` |
| `/api/payments/webhook` | `src/app/api/payments/webhook/route.ts` |
| `/api/plans` | `src/app/api/plans/route.ts` |
| `/api/subscriptions/change-plan` | `src/app/api/subscriptions/change-plan/route.ts` |
| `/api/webhooks/phonepe` | `src/app/api/webhooks/phonepe/route.ts` |

### Tracked But Deleted Route Handlers (Deleted In Working Tree)

These paths are still tracked in git, but are currently deleted in the working tree:

- `src/app/api/auth-status/route.ts`
- `src/app/api/auto-setup/route.ts`
- `src/app/api/create-direct-payment/route.ts`
- `src/app/api/create-embedded-payment/route.ts`
- `src/app/api/create-payment/route.ts`
- `src/app/api/create-storage/route.ts`
- `src/app/api/create-tables-direct/route.ts`
- `src/app/api/create-tables-final/route.ts`
- `src/app/api/create-tables-immediate/route.ts`
- `src/app/api/create-tables-now/route.ts`
- `src/app/api/create-tables/route.ts`
- `src/app/api/execute-sql/route.ts`
- `src/app/api/force-create-tables/route.ts`
- `src/app/api/gcp-storage/route.ts`
- `src/app/api/init-storage/route.ts`
- `src/app/api/monitoring/dashboard/route.ts`
- `src/app/api/monitoring/enhanced-dashboard/route.ts`
- `src/app/api/payment/create-order/route.ts`
- `src/app/api/payment/verify/route.ts`
- `src/app/api/payment/webhook/route.ts`
- `src/app/api/process-embedded-payment/route.ts`
- `src/app/api/setup-database/route.ts`
- `src/app/api/setup/create-db-table/route.ts`
- `src/app/api/setup/init-tokens-table/route.ts`
- `src/app/api/setup/route.ts`
- `src/app/api/verify-setup/route.ts`
- `src/app/api/vertex-ai/route.ts`

### Untracked But Referenced (Not Scanned)

UI code calls `/api/proxy/...` (e.g., `src/components/auth/AuthProvider.tsx`), implying a catch-all proxy route exists.

- `src/app/api/[...path]/route.ts` is present in the working tree but is currently untracked (excluded from scan).

## Backend (FastAPI) Routers

Most backend docs and integration points refer to a versioned API prefix of `/api/v1/*` (see `backend/README_PRODUCTION.md`, `backend/Dockerfile`, `backend/app/auth_middleware.py`).

Routers discovered via `APIRouter(...)` declarations:

### `backend/api/v1/*` Routers

| Router Prefix | File |
| --- | --- |
| `(none)` | `backend/api/v1/admin.py` |
| `/agents` | `backend/api/v1/agents.py` |
| `/agents` | `backend/api/v1/agents_stream.py` |
| `/ai-inference` | `backend/api/v1/ai_inference.py` |
| `/ai` | `backend/api/v1/ai_proxy.py` |
| `/analytics` | `backend/api/v1/analytics.py` |
| `/analytics-v2` | `backend/api/v1/analytics_v2.py` |
| `/approvals` | `backend/api/v1/approvals.py` |
| `(none)` | `backend/api/v1/audit.py` |
| `/bcm` | `backend/api/v1/bcm_endpoints.py` |
| `/blackbox` | `backend/api/v1/blackbox.py` |
| `/business-contexts` | `backend/api/v1/business_contexts.py` |
| `/campaigns` | `backend/api/v1/campaigns.py` |
| `""` | `backend/api/v1/cognitive.py` |
| `/config` | `backend/api/v1/config.py` |
| `/context` | `backend/api/v1/context.py` |
| `/council` | `backend/api/v1/council.py` |
| `/daily_wins` | `backend/api/v1/daily_wins.py` |
| `/dashboard` | `backend/api/v1/dashboard.py` |
| `/database/automation` | `backend/api/v1/database_automation.py` |
| `/database` | `backend/api/v1/database_health.py` |
| `/episodes` | `backend/api/v1/episodes.py` |
| `/evolution` | `backend/api/v1/evolution.py` |
| `/foundation` | `backend/api/v1/foundation.py` |
| `/graph` | `backend/api/v1/graph.py` |
| `(none)` | `backend/api/v1/health.py` |
| `/health` | `backend/api/v1/health_comprehensive.py` |
| `(none)` | `backend/api/v1/health_simple.py` |
| `/icps` | `backend/api/v1/icps.py` |
| `(none)` | `backend/api/v1/infra_health.py` |
| `/memory` | `backend/api/v1/memory.py` |
| `/memory` | `backend/api/v1/memory_endpoints.py` |
| `/metrics` | `backend/api/v1/metrics.py` |
| `/moves` | `backend/api/v1/moves.py` |
| `/muse` | `backend/api/v1/muse.py` |
| `/muse` | `backend/api/v1/muse_vertex_ai.py` |
| `(none)` | `backend/api/v1/ocr.py` |
| `/onboarding` | `backend/api/v1/onboarding.py` |
| `/payments` | `backend/api/v1/payments.py` |
| `/analytics` | `backend/api/v1/payments/analytics.py` |
| `""` | `backend/api/v1/payments_enhanced.py` |
| `""` | `backend/api/v1/payments_v2.py` |
| `""` | `backend/api/v1/payments_v2_secure.py` |
| `/rate-limit` | `backend/api/v1/rate_limit.py` |
| `/admin` | `backend/api/v1/redis_metrics.py` |
| `/search` | `backend/api/v1/search.py` |
| `/sessions` | `backend/api/v1/sessions.py` |
| `(none)` | `backend/api/v1/storage.py` |
| `/strategic` | `backend/api/v1/strategic_command.py` |
| `/titan` | `backend/api/v1/titan.py` |
| `/usage` | `backend/api/v1/usage.py` |
| `/users` | `backend/api/v1/users.py` |
| `(none)` | `backend/api/v1/validation.py` |
| `/workspaces` | `backend/api/v1/workspaces.py` |

Additional routers defined in the same module:

- `backend/api/v1/onboarding.py`
  - `/v2` (router name: `router_v2`)
  - `/migration` (router name: `router_migration`)
- `backend/api/v1/minimal_routers.py`
  - `/health`, `/auth`, `/users`, `/campaigns`, `/moves`, `/blackbox`, `/analytics`, `/ocr` (router names: `health`, `auth`, ...)

### Domain Routers (`backend/domains/*/router.py`)

| Router Prefix | File |
| --- | --- |
| `(none)` | `backend/domains/agents/router.py` |
| `/auth` | `backend/domains/auth/router.py` |
| `(none)` | `backend/domains/onboarding/router.py` |
| `(none)` | `backend/domains/payments/router.py` |

### Other Backend Routers (Non-canonical/Legacy)

| Router Prefix | File | Notes |
| --- | --- | --- |
| `/ocr` | `backend/services/sota_ocr/api.py` | SOTA OCR service router |
| `/api/v1/onboarding` | `backend/onboarding_routes.py` | Prefix includes version (legacy style) |
| `/api/payments` | `backend/backend-clean/services/payment_endpoints.py` | Prefix includes `/api` (legacy style) |

## Supabase Edge Function Endpoints (Deno)

- `supabase/functions/phonepe-webhook/index.ts` (Deno runtime)

## Other FastAPI Apps (Standalone)

These are separate `FastAPI()` app objects (not routers), each with their own entrypoint module:

- `backend/simple_backend.py`
- `backend/muse_test_server.py`
- `backend/standalone_phonepe_test.py`
- `backend/agents/tools/ocr_complex/api.py`
- `cloud-scraper/production_service.py`
- `cloud-scraper/production_search_service.py`
- `cloud-scraper/scraper_service.py`
- `cloud-scraper/enhanced_scraper_service.py`
- `cloud-scraper/ultra_fast_scraper.py`
- `cloud-scraper/free_web_search.py`
- `cloud-scraper/visual_intelligence_extractor.py`
- `minimal_gemini_backend.py`
- `secure_gemini_backend.py`
- `unlimited_backend.py`
- `legacy/unlimited_backend.py`
