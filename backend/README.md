# RaptorFlow Backend

FastAPI backend for the RaptorFlow marketing operating system.

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python -m backend.run_simple    # http://localhost:8000
```

Production: `uvicorn backend.main:app --host 0.0.0.0 --port 8080`

## Structure

```
backend/
├── main.py               # ASGI entrypoint (imports create_app)
├── app_factory.py         # App factory (middleware, CORS, routers, Sentry)
├── config.py              # Config module
├── run_simple.py          # Dev runner
├── api/
│   ├── registry.py        # Mounts all v1 routers under /api
│   ├── system.py          # GET / and GET /health
│   └── v1/
│       ├── workspaces.py  # Workspace CRUD
│       ├── campaigns.py   # Campaign CRUD (x-workspace-id)
│       ├── moves.py       # Move CRUD (x-workspace-id)
│       ├── foundation.py  # Foundation get/save (x-workspace-id)
│       ├── muse.py        # AI content generation (x-workspace-id)
│       ├── context.py     # BCM manifest (x-workspace-id)
│       ├── bcm_feedback.py # Feedback + memories (x-workspace-id)
│       ├── scraper.py     # Unified web scraper
│       └── search.py      # Unified web search
├── app/
│   ├── lifespan.py        # Startup/shutdown lifecycle
│   └── middleware.py      # Request middleware
├── core/
│   ├── supabase_mgr.py    # Supabase client
│   ├── redis_mgr.py       # Upstash Redis client
│   └── storage_mgr.py     # GCS storage
├── services/              # Business logic (BCM orchestration, caching, memory)
├── schemas/               # Pydantic models (BusinessContext)
├── config/settings.py     # App settings (Pydantic BaseSettings)
├── fixtures/              # Seed data (JSON)
├── templates/email/       # Email templates (HTML)
└── tests/                 # Unit + integration tests
```

## Auth

No auth. Tenant isolation is via `x-workspace-id` header. See `AUTH_INVENTORY.md` at repo root.

## Docker

- `Dockerfile` — dev image (gunicorn)
- `Dockerfile.production` — production image (uvicorn, health check on `/health`)
