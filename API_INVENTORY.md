# API_INVENTORY.md

Updated: 2026-02-09. Source: `backend/api/registry.py`, `backend/api/system.py`, `backend/api/v1/*.py`.

## Frontend Route Handler

| Route | File | Purpose |
|-------|------|---------|
| `/api/*` | `src/app/api/[...path]/route.ts` | Proxies all requests to backend |

This is the only Next.js route handler. All API logic lives in the backend.

## Backend System Routes

Source: `backend/api/system.py` (mounted at `/` and `/api/`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Service info (name, version, env, status) |
| `GET` | `/health` | Health check with service registry status |
| `GET` | `/api/` | Same as `/` |
| `GET` | `/api/health` | Same as `/health` |

## Backend API Routes

Source: `backend/api/registry.py` — all mounted under `/api` prefix.

### Workspaces (`backend/api/v1/workspaces.py`)

No auth required. Workspace is the tenant boundary.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/workspaces/` | Create workspace |
| `GET` | `/api/workspaces/{workspace_id}` | Get workspace |
| `PATCH` | `/api/workspaces/{workspace_id}` | Update workspace |

### Campaigns (`backend/api/v1/campaigns.py`)

Requires header: `x-workspace-id`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/campaigns/` | List campaigns |
| `POST` | `/api/campaigns/` | Create campaign |
| `GET` | `/api/campaigns/{campaign_id}` | Get campaign |
| `PATCH` | `/api/campaigns/{campaign_id}` | Update campaign |
| `DELETE` | `/api/campaigns/{campaign_id}` | Delete campaign |

### Moves (`backend/api/v1/moves.py`)

Requires header: `x-workspace-id`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/moves/` | List moves |
| `POST` | `/api/moves/` | Create move |
| `PATCH` | `/api/moves/{move_id}` | Update move |
| `DELETE` | `/api/moves/{move_id}` | Delete move |

### Foundation (`backend/api/v1/foundation.py`)

Requires header: `x-workspace-id`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/foundation/` | Get foundation data |
| `PUT` | `/api/foundation/` | Save foundation data |

### Muse (`backend/api/v1/muse.py`)

Requires header: `x-workspace-id`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/muse/health` | Muse service health |
| `POST` | `/api/muse/generate` | Generate AI content |

### Context / BCM (`backend/api/v1/context.py`)

Requires header: `x-workspace-id`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/context/` | Get latest BCM manifest |
| `POST` | `/api/context/rebuild` | Rebuild BCM from stored context |
| `POST` | `/api/context/seed` | Seed BCM from raw JSON |
| `GET` | `/api/context/versions` | List BCM versions |

### BCM Feedback (`backend/api/v1/bcm_feedback.py`)

Requires header: `x-workspace-id`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/feedback/` | Submit feedback on generation |
| `GET` | `/api/feedback/memories` | Get accumulated memories |
| `GET` | `/api/feedback/history` | Get generation history |

### Scraper (`backend/api/v1/scraper.py`)

Unified web scraping endpoint.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/scraper/scrape` | Scrape URL(s) with configurable strategy |

### Search (`backend/api/v1/search.py`)

Unified web search endpoint.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/search/` | Web search with multiple backends |

## Router Registration

All routers are registered in `backend/api/registry.py`:

```python
UNIVERSAL_ROUTERS = [
    workspaces.router,
    campaigns.router,
    moves.router,
    foundation.router,
    muse.router,
    context.router,
    bcm_feedback.router,
    scraper.router,
    search.router,
]
```

Mounted by `backend/app_factory.py` via `include_universal(app, prefix="/api")`.
