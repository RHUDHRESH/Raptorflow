# Migration Guide

## Canonical App Usage
- App import: `backend.main:app`
- Runner: `backend/run_simple.py`

Deprecated runners now call the canonical runner:
- `backend/run.py`
- `backend/run_minimal.py`
- `backend/start_backend.py`

## Legacy Router Access
Legacy, non-canonical routers are now centralized and are mounted under `/api/legacy/<module>`.

Enable via environment:
- `ENABLE_LEGACY_EXPERIMENTAL_ROUTES=true`

Example paths:
- `GET /api/legacy/onboarding-v2/onboarding/...`
- `POST /api/legacy/payments-v2/payments/...`

This avoids conflicts with canonical routes under `/api`.

## Legacy V1 Prefix
If you must retain the `/api/v1/*` prefix for canonical routers:
- `ENABLE_LEGACY_V1=true`

This is implemented via the canonical router list and does not include legacy/experimental routers.

## Endpoint Canonicalization
The canonical routers are defined in `backend/api/registry.py`. Notable deprecated modules include:
- Onboarding variants: `onboarding_v2`, `onboarding_enhanced`, `onboarding_sync`, `onboarding_migration`, `onboarding_finalize`, `onboarding_universal`
- Payments variants: `payments_v2`, `payments_v2_secure`, `payments_enhanced`
- Misc: `muse_vertex_ai`, `health`, `health_simple`, `validation`, `database_health`, `database_automation`, `analytics_v2`

If you relied on these modules directly, move to the canonical routers (e.g., `backend/api/v1/onboarding.py`, `backend/api/v1/payments.py`) or enable legacy routing at `/api/legacy`.

## Notes
- Standalone FastAPI apps (e.g., `backend/api/v1/cognitive.py`, `backend/simple_backend.py`) remain out of the canonical app wiring.
- These standalone apps should be treated as legacy or test-only entry points.
