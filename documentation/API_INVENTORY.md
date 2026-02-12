# API Inventory

Canonical backend API inventory (served under `/api/*`).

## System and Operations

- `GET /api/`: Root metadata.
- `GET /api/health`: Base health summary.
- `GET /api/ops/health`: Detailed ops health.
- `GET /api/ops/services`: Integration/service readiness.
- `GET /api/ops/ai-architecture`: Active AI architecture map.
- `GET /api/ops/health/db`: Database health detail.
- `GET /api/ops/health/cache`: Cache health detail.

## Workspace and Onboarding

- `POST /api/workspaces/`: Create workspace with onboarding defaults.
- `GET /api/workspaces/{workspace_id}`: Get workspace.
- `PATCH /api/workspaces/{workspace_id}`: Update workspace.
- `GET /api/workspaces/onboarding/steps`: Canonical onboarding schema.
- `GET /api/workspaces/{workspace_id}/onboarding/status`: Onboarding + BCM readiness.
- `POST /api/workspaces/{workspace_id}/onboarding/complete`: Generate business context and seed BCM.

## BCM / Context

- `GET /api/context/{workspace_id}`: Get latest BCM.
- `POST /api/context/{workspace_id}/seed`: Seed BCM.
- `POST /api/context/{workspace_id}/rebuild`: Rebuild BCM.
- `POST /api/context/{workspace_id}/reflect`: Reflect BCM into memory.
- `GET /api/context/{workspace_id}/versions`: BCM version history.

## Muse / Generation

- `POST /api/muse/generate`: Content generation with intensity + execution mode.
- `GET /api/muse/health`: Muse service health.

## Campaigns / Moves / Foundation

- `GET|POST|PATCH|DELETE /api/campaigns/*`: Campaign CRUD and related actions.
- `GET|POST|PATCH|DELETE /api/moves/*`: Moves CRUD and execution data.
- `GET|POST|PATCH /api/foundation/*`: Foundation data management.

## Assets

- `POST /api/assets/sessions`: Create upload session.
- `POST /api/assets/{asset_id}/confirm`: Confirm upload.
- `GET /api/assets`: List workspace assets.
- `GET /api/assets/{asset_id}`: Get asset metadata.
- `DELETE /api/assets/{asset_id}`: Delete asset.

## Optional Modules

- `GET /api/search`: Unified web search.
- `GET /api/search/health`: Search engine health.
- `GET /api/search/engines`: Available search engines.
- `GET /api/search/status`: Search service status.
- `POST /api/scraper`: Unified scraper endpoint.
- `GET /api/scraper/health`: Scraper health.
- `GET /api/scraper/analytics`: Scraper analytics.
- `GET /api/scraper/stats`: Scraper stats.
- `GET /api/scraper/strategies`: Scraping strategies.
- `POST /api/scraper/strategy`: Update active scraping strategy.

## Communications and Auth

- `POST /api/communications/contact`: Contact form email pipeline.
- `GET /api/auth/health`: Auth integration health.
- `POST /api/auth/verify`: Verify Supabase access token.
