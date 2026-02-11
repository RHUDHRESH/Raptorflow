# REPO_MAP.md

Generated: 2026-02-09. Source: working tree inspection.

## Commands

### Frontend (Next.js — repo root)

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server (port 3000) |
| `npm run build` | Lint + typecheck + production build |
| `npm run start` | Serve production build |
| `npm run lint` | ESLint |
| `npm run type-check` | TypeScript `--noEmit` |
| `npm run test` | Vitest |
| `npm run test:e2e` | Playwright |
| `npm run smoke` | Repo structure smoke test |
| `npm run health-check` | Backend + proxy health check |

### Backend (FastAPI — `backend/`)

| Command | Description |
|---------|-------------|
| `python -m backend.run_simple` | Dev server (port 8000) |
| `uvicorn backend.main:app` | Production ASGI |

## Entrypoints

### Frontend

- **Root layout**: `src/app/layout.tsx`
- **Landing page**: `src/app/page.tsx`
- **App shell**: `src/app/(shell)/layout.tsx` (authenticated app wrapper)
- **API proxy**: `src/app/api/[...path]/route.ts` (proxies to backend)
- **Global CSS**: `src/app/globals.css`
- **Error boundaries**: `src/app/error.tsx`, `src/app/global-error.tsx`

### Backend

- **ASGI app**: `backend/main.py` (imports `create_app` from `app_factory`)
- **App factory**: `backend/app_factory.py` (middleware, CORS, routers, Sentry)
- **Router registry**: `backend/api/registry.py` (mounts all v1 routers)
- **System routes**: `backend/api/system.py` (`GET /`, `GET /health`)

## Directory Map

```
raptorflow/
├── src/                          # Next.js frontend source
│   ├── app/                      # App Router
│   │   ├── (shell)/              # Authenticated app pages
│   │   │   ├── campaigns/        # Campaign CRUD
│   │   │   ├── dashboard/        # Main dashboard
│   │   │   ├── foundation/       # Brand positioning
│   │   │   ├── help/             # Help center
│   │   │   ├── moves/            # Weekly moves
│   │   │   ├── muse/             # AI content gen
│   │   │   └── settings/         # User settings
│   │   ├── api/[...path]/        # Backend proxy
│   │   ├── contact/              # Contact page
│   │   ├── features/             # Feature pages
│   │   └── pricing/              # Pricing page
│   ├── components/               # React components
│   │   ├── analytics/            # Analytics widgets
│   │   ├── animation/            # Animation components
│   │   ├── bcm/                  # Business context UI
│   │   ├── campaigns/            # Campaign UI
│   │   ├── compass/              # Compass branding
│   │   ├── dashboard/            # Dashboard components
│   │   ├── effects/              # Visual effects (cursor, magnetic, etc.)
│   │   ├── error/                # Error boundaries
│   │   ├── foundation/           # Foundation UI
│   │   ├── landing/              # Marketing site components
│   │   ├── moves/                # Moves UI
│   │   ├── muse/                 # Muse AI UI
│   │   ├── notifications/        # Notification system
│   │   ├── positioning/          # Positioning UI
│   │   ├── providers/            # Context providers
│   │   ├── shell/                # App shell (TopNav, Sidebar)
│   │   ├── ui/                   # Blueprint design system
│   │   └── workspace/            # Workspace provider
│   ├── services/                 # API service clients
│   │   ├── http.ts               # Base HTTP client
│   │   ├── bcm.service.ts
│   │   ├── campaigns.service.ts
│   │   ├── cohorts.service.ts
│   │   ├── feedback.service.ts
│   │   ├── foundation.service.ts
│   │   ├── moves.service.ts
│   │   ├── muse.service.ts
│   │   ├── scraper.service.ts
│   │   ├── search.service.ts
│   │   └── workspaces.service.ts
│   ├── stores/                   # Zustand stores
│   │   ├── bcmStore.ts
│   │   ├── campaignStore.ts
│   │   ├── foundationStore.ts
│   │   ├── movesStore.ts
│   │   └── notificationStore.ts
│   ├── types/                    # TypeScript type definitions
│   ├── lib/                      # Utilities
│   ├── data/                     # Static data (templates)
│   ├── styles/                   # Additional CSS
│   ├── assets/                   # Images (artwork)
│   └── test/                     # Test setup
│
├── backend/                      # FastAPI backend
│   ├── api/
│   │   ├── v1/                   # Versioned route handlers
│   │   │   ├── workspaces.py     # Workspace CRUD
│   │   │   ├── campaigns.py      # Campaign CRUD
│   │   │   ├── moves.py          # Move CRUD
│   │   │   ├── foundation.py     # Foundation get/save
│   │   │   ├── muse.py           # AI content generation
│   │   │   ├── context.py        # BCM manifest
│   │   │   ├── bcm_feedback.py   # User feedback + memories
│   │   │   ├── scraper.py        # Unified web scraper
│   │   │   └── search.py         # Unified web search
│   │   ├── registry.py           # Router mount registry
│   │   └── system.py             # Health + root
│   ├── app/                      # Lifecycle + middleware
│   │   ├── lifespan.py
│   │   └── middleware.py
│   ├── core/                     # Infrastructure adapters
│   │   ├── supabase_mgr.py       # Supabase client
│   │   ├── redis_mgr.py          # Upstash Redis client
│   │   └── storage_mgr.py        # GCS storage
│   ├── services/                 # Business logic layer
│   │   ├── bcm_service.py        # BCM orchestration
│   │   ├── bcm_cache.py          # BCM caching
│   │   ├── bcm_memory.py         # BCM memory
│   │   ├── bcm_reducer.py        # BCM reduction
│   │   ├── bcm_reflector.py      # BCM reflection
│   │   ├── bcm_generation_logger.py
│   │   └── base_service.py
│   ├── schemas/                  # Pydantic models
│   │   └── business_context.py
│   ├── config/                   # App settings
│   │   └── settings.py
│   ├── fixtures/                 # Seed/demo data (JSON)
│   ├── templates/email/          # Email templates (HTML)
│   ├── tests/                    # Backend tests
│   ├── main.py                   # ASGI entrypoint
│   ├── app_factory.py            # App factory
│   ├── config.py                 # Config module
│   ├── run_simple.py             # Dev runner
│   ├── Dockerfile                # Dev Docker image
│   ├── Dockerfile.production     # Production Docker image
│   ├── requirements.txt          # Python dependencies
│   ├── requirements-dev.txt      # Dev dependencies
│   └── pyproject.toml            # Project config
│
├── supabase/migrations/          # SQL migrations (19 files)
├── public/                       # Static assets (SVG, PNG)
├── scripts/                      # Dev scripts
│   ├── smoke_test.js             # Repo structure check
│   └── quick_check.js            # Health check
├── ADRs/                         # Architectural Decision Records (7)
│
├── AGENTS.md                     # Repo constitution (rules)
├── REPO_MAP.md                   # This file
├── API_INVENTORY.md              # API surface
├── AUTH_INVENTORY.md              # Auth/identity model
├── README.md                     # Project overview
│
├── package.json                  # Node dependencies + scripts
├── tsconfig.json                 # TypeScript config
├── next.config.js                # Next.js config
├── tailwind.config.js            # Tailwind config
├── eslint.config.js              # ESLint config
├── vercel.json                   # Vercel deployment config
├── vitest.config.ts              # Vitest config
├── sentry.edge.config.ts         # Sentry edge config
├── sentry.server.config.ts       # Sentry server config
└── .env.example                  # Environment template
```

## API Client Flow

```
Browser → Next.js API proxy (src/app/api/[...path]/route.ts)
       → Backend FastAPI (backend/main.py)
       → Supabase / Redis / Vertex AI
```

Frontend services in `src/services/*.service.ts` call the backend through the base HTTP client (`src/services/http.ts`).
