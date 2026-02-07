# Entrypoint & Route Audit

## Canonical Entry Point
- backend/main.py
- backend/app_factory.py

## Deprecated Entrypoints / Runners
- backend/main_new.py
- backend/main_minimal.py
- backend/main_production.py
- backend/run.py
- backend/run_simple.py
- backend/run_minimal.py
- backend/start_backend.py

## Canonical Routers (Registry)
- backend\api\v1\admin.py
- backend\api\v1\agents.py
- backend\api\v1\ai_proxy.py
- backend\api\v1\analytics.py
- backend\api\v1\approvals.py
- backend\api\v1\blackbox.py
- backend\api\v1\business_contexts.py
- backend\api\v1\campaigns.py
- backend\api\v1\config.py
- backend\api\v1\context.py
- backend\api\v1\council.py
- backend\api\v1\daily_wins.py
- backend\api\v1\dashboard.py
- backend\api\v1\evolution.py
- backend\api\v1\foundation.py
- backend\api\v1\graph.py
- backend\api\v1\health_comprehensive.py
- backend\api\v1\icps.py
- backend\api\v1\infra_health.py
- backend\api\v1\memory.py
- backend\api\v1\metrics.py
- backend\api\v1\moves.py
- backend\api\v1\muse.py
- backend\api\v1\ocr.py
- backend\api\v1\onboarding.py
- backend\api\v1\payments.py
- backend\api\v1\search.py
- backend\api\v1\sessions.py
- backend\api\v1\storage.py
- backend\api\v1\titan.py
- backend\api\v1\usage.py
- backend\api\v1\users.py
- backend\api\v1\workspaces.py
- backend\domains\auth\router.py

## FastAPI App Definitions (Non-factory)
- backend\agents\tools\ocr_complex\api.py
- backend\api\v1\rate_limit.py
- backend\docs\interactive_docs.py
- backend\muse_test_server.py
- backend\simple_backend.py
- backend\standalone_phonepe_test.py
- backend\tests\test_backend.py
- backend\tests\test_sentry_integration.py
- backend\tests\test_validation.py

## Endpoint Inventory

| Metric | Count |
| --- | --- |
| Total endpoints (scanned) | 622 |
| Endpoints in canonical routers | 276 |
| Endpoints in non-canonical files | 346 |

## Top Non-canonical Endpoint Files

| Endpoints | File |
| --- | --- |
| 21 | backend\api\v1\onboarding_v2.py |
| 20 | backend\api\v1\health.py |
| 18 | backend\api\v1\muse_vertex_ai.py |
| 17 | backend\api\v1\onboarding_migration.py |
| 16 | backend\api\v1\cognitive.py |
| 14 | backend\api\v1\bcm_endpoints.py |
| 14 | backend\api\v1\database_automation.py |
| 14 | backend\api\v1\memory_endpoints.py |
| 13 | backend\api\v1\minimal_routers.py |
| 13 | backend\api\v1\validation.py |
| 11 | backend\services\sota_ocr\api.py |
| 10 | backend\api\v1\episodes.py |
| 10 | backend\api\v1\onboarding_enhanced.py |
| 8 | backend\api\v1\agents_stream.py |
| 8 | backend\api\v1\database_health.py |
| 8 | backend\onboarding_routes.py |
| 8 | backend\simple_backend.py |
| 7 | backend\api\v1\onboarding_sync.py |
| 7 | backend\api\v1\payments_v2_secure.py |
| 6 | backend\api\v1\ai_inference.py |

## Top Canonical Endpoint Files

| Endpoints | File |
| --- | --- |
| 38 | backend\api\v1\onboarding.py |
| 20 | backend\api\v1\graph.py |
| 19 | backend\api\v1\metrics.py |
| 16 | backend\api\v1\campaigns.py |
| 15 | backend\api\v1\users.py |
| 13 | backend\api\v1\moves.py |
| 12 | backend\api\v1\sessions.py |
| 11 | backend\api\v1\admin.py |
| 11 | backend\api\v1\agents.py |
| 11 | backend\api\v1\workspaces.py |
| 10 | backend\api\v1\icps.py |
| 9 | backend\api\v1\memory.py |
| 9 | backend\api\v1\storage.py |
| 9 | backend\domains\auth\router.py |
| 8 | backend\api\v1\approvals.py |
| 7 | backend\api\v1\config.py |
| 6 | backend\api\v1\analytics.py |
| 6 | backend\api\v1\blackbox.py |
| 6 | backend\api\v1\context.py |
| 6 | backend\api\v1\health_comprehensive.py |
