# API Inventory

Last updated: 2026-02-18

## Canonical Prefixes

- System routes: `/`, `/health`, mirrored under `/api/*`
- Product/API routes: `/api/*`
- AI Hub routes: `/api/ai/hub/v1/*`

## AI Hub Public Contract

- `GET /api/ai/hub/v1/health`
- `GET /api/ai/hub/v1/capabilities`
- `GET /api/ai/hub/v1/policies`
- `POST /api/ai/hub/v1/tasks/run`
- `POST /api/ai/hub/v1/tasks/run-async`
- `GET /api/ai/hub/v1/jobs/{job_id}`
- `GET /api/ai/hub/v1/tasks/{run_id}/context`
- `GET /api/ai/hub/v1/tasks/{run_id}/trace`
- `POST /api/ai/hub/v1/feedback`
- `POST /api/ai/hub/v1/evals/execute`

## Registered Route Module Files

- `backend/api/v1/ai_hub/routes.py`
- `backend/api/v1/assets/routes.py`
- `backend/api/v1/auth/routes.py`
- `backend/api/v1/bcm_feedback/routes.py`
- `backend/api/v1/campaigns/routes.py`
- `backend/api/v1/communications/routes.py`
- `backend/api/v1/context/routes.py`
- `backend/api/v1/foundation/routes.py`
- `backend/api/v1/health/routes.py`
- `backend/api/v1/moves/routes.py`
- `backend/api/v1/muse/routes.py`
- `backend/api/v1/scraper/routes.py`
- `backend/api/v1/search/routes.py`
- `backend/api/v1/workspace_guard/routes.py`
- `backend/api/v1/workspaces/routes.py`

## Proxy Boundary

Frontend proxy route:

- `src/app/api/[...path]/route.ts`
