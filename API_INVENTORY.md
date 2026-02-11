# API_INVENTORY.md

Updated: 2026-02-11
Source of truth:
- `backend/api/system.py`
- `backend/api/registry.py`
- `backend/api/v1/*.py`
- `src/app/api/**/route.ts`

## Frontend Route Handlers

| Method | Path | File | Purpose |
|---|---|---|---|
| ALL | `/api/[...path]` | `src/app/api/[...path]/route.ts` | Canonical proxy to backend API |
| POST | `/api/analytics/vitals` | `src/app/api/analytics/vitals/route.ts` | Web vitals ingestion |
| POST | `/api/analytics/metrics` | `src/app/api/analytics/metrics/route.ts` | Custom frontend metric ingestion |

## Backend System Routes

Mounted directly and under `/api` in `backend/app_factory.py`.

| Method | Path |
|---|---|
| GET | `/` |
| GET | `/health` |
| GET | `/api/` |
| GET | `/api/health` |

## Backend Canonical API Routers

All of the following are mounted under `/api` by `include_universal(..., prefix="/api")`.

### Ops Health (`backend/api/v1/health.py`)

| Method | Path |
|---|---|
| GET | `/api/ops/health` |
| GET | `/api/ops/health/db` |
| GET | `/api/ops/health/cache` |

### Workspaces (`backend/api/v1/workspaces.py`)

| Method | Path |
|---|---|
| POST | `/api/workspaces/` |
| GET | `/api/workspaces/{workspace_id}` |
| PATCH | `/api/workspaces/{workspace_id}` |

### Campaigns (`backend/api/v1/campaigns.py`)

Requires header: `x-workspace-id`

| Method | Path |
|---|---|
| GET | `/api/campaigns/` |
| POST | `/api/campaigns/` |
| GET | `/api/campaigns/{campaign_id}` |
| PATCH | `/api/campaigns/{campaign_id}` |
| DELETE | `/api/campaigns/{campaign_id}` |

### Moves (`backend/api/v1/moves.py`)

Requires header: `x-workspace-id`

| Method | Path |
|---|---|
| GET | `/api/moves/` |
| POST | `/api/moves/` |
| PATCH | `/api/moves/{move_id}` |
| DELETE | `/api/moves/{move_id}` |

### Foundation (`backend/api/v1/foundation.py`)

Requires header: `x-workspace-id`

| Method | Path |
|---|---|
| GET | `/api/foundation/` |
| PUT | `/api/foundation/` |

### Muse (`backend/api/v1/muse.py`)

Requires header: `x-workspace-id`

| Method | Path |
|---|---|
| GET | `/api/muse/health` |
| POST | `/api/muse/generate` |

### Context / BCM (`backend/api/v1/context.py`)

Requires header: `x-workspace-id`

| Method | Path |
|---|---|
| GET | `/api/context/` |
| POST | `/api/context/rebuild` |
| POST | `/api/context/seed` |
| DELETE | `/api/context/` |
| GET | `/api/context/versions` |
| POST | `/api/context/reflect` |

### BCM Feedback (`backend/api/v1/bcm_feedback.py`)

Requires header: `x-workspace-id`

| Method | Path |
|---|---|
| POST | `/api/context/feedback/` |
| GET | `/api/context/feedback/memories` |
| GET | `/api/context/feedback/memories/summary` |
| DELETE | `/api/context/feedback/memories/{memory_id}` |
| GET | `/api/context/feedback/generations` |

### Scraper (`backend/api/v1/scraper.py`)

| Method | Path |
|---|---|
| POST | `/api/scraper/` |
| GET | `/api/scraper/health` |
| GET | `/api/scraper/analytics` |
| GET | `/api/scraper/stats` |
| GET | `/api/scraper/strategies` |
| POST | `/api/scraper/strategy` |

### Search (`backend/api/v1/search.py`)

| Method | Path |
|---|---|
| GET | `/api/search/` |
| GET | `/api/search/health` |
| GET | `/api/search/engines` |
| GET | `/api/search/status` |
