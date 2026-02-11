# REPO_MAP.md

Updated: 2026-02-11
Source: repository filesystem + backend router inspection.

## Runtime Commands

### Frontend (repo root)

| Command | Purpose |
|---|---|
| `npm run dev` | Next.js dev server |
| `npm run build` | Lint + type-check + Next build |
| `npm run start` | Run production build |
| `npm run lint` | ESLint on `src/**` |
| `npm run type-check` | TypeScript no-emit check |
| `npm run smoke` | Structural smoke check |
| `npm run health-check` | Backend + proxy health ping |

### Backend

| Command | Purpose |
|---|---|
| `python -m backend.run_simple` | Dev API server |
| `uvicorn backend.main:app` | ASGI server |

## Entrypoints

### Frontend

- App layout: `src/app/layout.tsx`
- Shell layout: `src/app/(shell)/layout.tsx`
- Landing page: `src/app/page.tsx`
- API proxy: `src/app/api/[...path]/route.ts`
- Analytics handlers:
  - `src/app/api/analytics/vitals/route.ts`
  - `src/app/api/analytics/metrics/route.ts`

### Backend

- ASGI entry: `backend/main.py`
- App factory: `backend/app_factory.py`
- System routes: `backend/api/system.py`
- Canonical router registry: `backend/api/registry.py`

## Directory Map (Condensed)

```text
raptorflow/
  src/
    app/                    # Next.js app router pages + API handlers
    components/             # UI/components used by app pages
    services/               # frontend API clients
    stores/                 # state stores
    lib/                    # shared frontend helpers
    tests/                  # migrated frontend test/debug scripts
  backend/
    api/
      v1/                   # canonical API routers
      system.py             # root + health
      registry.py           # router registration list
      dependencies.py       # shared route deps
    app/                    # middleware + lifespan + app internals
    core/                   # infra adapters (supabase, redis, rate limiter, cache, db pool)
    services/               # business logic/services
    tests/
      verification/         # migrated backend verification scripts
      debug/                # backend debug scripts
    main.py
    app_factory.py
  scripts/
    smoke_test.js
    quick_check.js
    audit/
  supabase/migrations/      # SQL migrations
  ADRs/                     # architecture decisions
  docs/                     # audits and architecture docs
```

## Canonical Architecture Notes

- Single backend API layer (FastAPI) exposed through Next proxy.
- Identity model is workspace-header based (`x-workspace-id`) in no-auth mode.
- Legacy `cloud-scraper/` has been removed from active repository state in this consolidation.
