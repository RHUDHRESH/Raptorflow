# RaptorFlow Architecture

## Canonical Code Paths
- Frontend (Next.js App Router): `src/`
- Backend (FastAPI): `backend/`
- Duplicate/archived copies: `frontend/`, `backend/backend-clean/` (see `ARCHIVED.md` markers)

## Modules
- Frontend UI: `src/app`, `src/components`, `src/modules`, `src/stores`
- API client + app services: `src/services`, `src/lib`
- Backend API (FastAPI): `backend/app.py` + routers in `backend/api/v1`
- Cognitive engine + workflows: `backend/cognitive`, `backend/services`, `backend/workflows`
- Data access + schemas: `backend/db`, `backend/schemas`
- Infrastructure: `backend/infrastructure` (GCP, storage, secrets), `backend/redis`

## Data Model (Primary Entities)
From `backend/db/*.py` and `backend/schemas/*.py`:
- Workspaces + users/profiles
- Foundations + messaging + positioning
- ICPs + cohorts
- Campaigns + moves + daily_wins
- Business context + evidence
- Payments + subscriptions + audits

## Business Context Contract
Defined in `backend/schemas/business_context.py` as `BusinessContext`.

Required metadata:
- `ucid`, `version`, `created_at`, `updated_at`, `workspace_id`, `user_id`

Core components:
- `identity`: `BrandIdentity`
- `audience`: `StrategicAudience`
- `positioning`: `MarketPosition`

Enhanced components:
- `icp_profiles`: list of `ICPProfile`
- `channel_strategies`: list of `ChannelStrategy`
- `messaging_framework`: `MessagingFramework`
- `competitive_position`: `CompetitivePosition`
- `intelligence`: `Intelligence`

Operational fields:
- `evidence_ids`, `noteworthy_insights`
- `validation_score`, `completion_percentage`
- `status`, `quality_score`
- `ai_generated`, `human_reviewed`
- `metadata` (freeform extension map)

## API Endpoints (Minimal App)
From `backend/app.py` + `backend/api/v1/minimal_routers.py`:
- `GET /health`
- `GET /api/v1/health/`
- `GET /api/v1/health/detailed`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/users/me`
- `GET /api/v1/campaigns/`
- `POST /api/v1/campaigns/`
- `GET /api/v1/moves/`
- `POST /api/v1/moves/`
- `GET /api/v1/blackbox/`
- `POST /api/v1/blackbox/generate`
- `GET /api/v1/analytics/`
- `POST /api/v1/ocr/process`
