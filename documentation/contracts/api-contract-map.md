# API Contract Map

- Generated: `2026-02-12T14:35:03.145045+00:00`
- API Prefix: `/api`
- Modules: `13`
- Endpoints: `54`

## `health`

- File: `backend/api/v1/health.py`
- Required: `True`
- Routers: `router` -> `/ops`
- Endpoints:
  - `GET` `/api/ops/health` (health_check, router `router`)
  - `GET` `/api/ops/services` (services_status, router `router`)
  - `GET` `/api/ops/ai-architecture` (ai_architecture, router `router`)
  - `GET` `/api/ops/health/db` (database_health, router `router`)
  - `GET` `/api/ops/health/cache` (cache_health, router `router`)

## `auth`

- File: `backend/api/v1/auth.py`
- Required: `True`
- Routers: `router` -> `/auth`
- Endpoints:
  - `GET` `/api/auth/health` (auth_health, router `router`)
  - `POST` `/api/auth/verify` (verify_access_token, router `router`)

## `communications`

- File: `backend/api/v1/communications.py`
- Required: `True`
- Routers: `router` -> `/communications`
- Endpoints:
  - `POST` `/api/communications/contact` (submit_contact, router `router`)

## `workspaces`

- File: `backend/api/v1/workspaces.py`
- Required: `True`
- Routers: `router` -> `/workspaces`
- Endpoints:
  - `POST` `/api/workspaces` (create_workspace, router `router`)
  - `GET` `/api/workspaces/onboarding/steps` (get_onboarding_steps, router `router`)
  - `GET` `/api/workspaces/{workspace_id}/onboarding/status` (get_onboarding_status, router `router`)
  - `POST` `/api/workspaces/{workspace_id}/onboarding/complete` (complete_onboarding, router `router`)
  - `GET` `/api/workspaces/{workspace_id}` (get_workspace, router `router`)
  - `PATCH` `/api/workspaces/{workspace_id}` (update_workspace, router `router`)

## `campaigns`

- File: `backend/api/v1/campaigns.py`
- Required: `True`
- Routers: `router` -> `/campaigns`
- Endpoints:
  - `GET` `/api/campaigns` (list_campaigns, router `router`)
  - `POST` `/api/campaigns` (create_campaign, router `router`)
  - `GET` `/api/campaigns/{campaign_id}` (get_campaign, router `router`)
  - `GET` `/api/campaigns/{campaign_id}/moves-bundle` (get_campaign_moves_bundle, router `router`)
  - `PATCH` `/api/campaigns/{campaign_id}` (update_campaign, router `router`)
  - `DELETE` `/api/campaigns/{campaign_id}` (delete_campaign, router `router`)

## `moves`

- File: `backend/api/v1/moves.py`
- Required: `True`
- Routers: `router` -> `/moves`
- Endpoints:
  - `GET` `/api/moves` (list_moves, router `router`)
  - `POST` `/api/moves` (create_move, router `router`)
  - `PATCH` `/api/moves/{move_id}` (update_move, router `router`)
  - `DELETE` `/api/moves/{move_id}` (delete_move, router `router`)

## `foundation`

- File: `backend/api/v1/foundation.py`
- Required: `True`
- Routers: `router` -> `/foundation`
- Endpoints:
  - `GET` `/api/foundation` (get_foundation, router `router`)
  - `PUT` `/api/foundation` (save_foundation, router `router`)

## `muse`

- File: `backend/api/v1/muse.py`
- Required: `True`
- Routers: `router` -> `/muse`
- Endpoints:
  - `GET` `/api/muse/health` (muse_health, router `router`)
  - `POST` `/api/muse/generate` (generate, router `router`)

## `assets`

- File: `backend/api/v1/assets.py`
- Required: `True`
- Routers: `router` -> `/assets`
- Endpoints:
  - `POST` `/api/assets/sessions` (create_upload_session, router `router`)
  - `POST` `/api/assets/{asset_id}/confirm` (confirm_upload, router `router`)
  - `GET` `/api/assets` (list_assets, router `router`)
  - `GET` `/api/assets/{asset_id}` (get_asset, router `router`)
  - `DELETE` `/api/assets/{asset_id}` (delete_asset, router `router`)

## `context`

- File: `backend/api/v1/context.py`
- Required: `True`
- Routers: `router` -> `/context`
- Endpoints:
  - `GET` `/api/context` (get_latest_bcm, router `router`)
  - `POST` `/api/context/rebuild` (rebuild_bcm, router `router`)
  - `POST` `/api/context/seed` (seed_bcm, router `router`)
  - `DELETE` `/api/context` (clear_bcm, router `router`)
  - `GET` `/api/context/versions` (list_bcm_versions, router `router`)
  - `POST` `/api/context/reflect` (reflect_bcm, router `router`)

## `bcm_feedback`

- File: `backend/api/v1/bcm_feedback.py`
- Required: `True`
- Routers: `router` -> `/context/feedback`
- Endpoints:
  - `POST` `/api/context/feedback` (submit_feedback, router `router`)
  - `GET` `/api/context/feedback/memories` (list_memories, router `router`)
  - `GET` `/api/context/feedback/memories/summary` (memory_summary, router `router`)
  - `DELETE` `/api/context/feedback/memories/{memory_id}` (delete_memory, router `router`)
  - `GET` `/api/context/feedback/generations` (list_generations, router `router`)

## `scraper`

- File: `backend/api/v1/scraper.py`
- Required: `False`
- Routers: `router` -> `/scraper`
- Endpoints:
  - `POST` `/api/scraper` (scrape_endpoint, router `router`)
  - `GET` `/api/scraper/health` (scraper_health, router `router`)
  - `GET` `/api/scraper/analytics` (scraper_analytics, router `router`)
  - `GET` `/api/scraper/stats` (scraper_stats, router `router`)
  - `GET` `/api/scraper/strategies` (list_strategies, router `router`)
  - `POST` `/api/scraper/strategy` (update_strategy, router `router`)

## `search`

- File: `backend/api/v1/search.py`
- Required: `False`
- Routers: `router` -> `/search`
- Endpoints:
  - `GET` `/api/search` (search_endpoint, router `router`)
  - `GET` `/api/search/health` (search_health, router `router`)
  - `GET` `/api/search/engines` (list_engines, router `router`)
  - `GET` `/api/search/status` (search_status, router `router`)
