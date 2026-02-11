# RaptorFlow

The Founder Marketing Operating System. Converts messy business context into clear positioning, a 90-day marketing war plan, weekly execution moves, and tracked outcomes.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, Framer Motion, Zustand |
| Backend | FastAPI (Python 3.12), Pydantic |
| Database | Supabase (PostgreSQL + RLS) |
| Cache | Upstash Redis |
| AI | Google Vertex AI (Gemini) |
| Monitoring | Sentry (full-stack) |
| Deployment | Vercel (frontend), Render (backend) |

## Quick Start

### Prerequisites

- Node.js 22.x
- Python 3.12+
- npm 10+

### Frontend

```bash
cp .env.example .env.local   # edit with your values
npm install
npm run dev                   # http://localhost:3000
```

### Backend

```bash
cd backend
cp .env.example .env          # edit with your values
pip install -r requirements.txt
python -m backend.run_simple  # http://localhost:8000
```

## Project Structure

```
raptorflow/
├── src/                      # Next.js frontend
│   ├── app/                  # App Router pages
│   │   ├── (shell)/          # Authenticated app shell
│   │   │   ├── dashboard/    # Main dashboard
│   │   │   ├── foundation/   # Brand positioning
│   │   │   ├── campaigns/    # Campaign management
│   │   │   ├── moves/        # Weekly execution
│   │   │   ├── muse/         # AI content generation
│   │   │   ├── settings/     # User settings
│   │   │   └── help/         # Help center
│   │   ├── api/[...path]/    # Backend proxy route
│   │   ├── features/         # Marketing pages
│   │   ├── pricing/          # Pricing page
│   │   └── contact/          # Contact page
│   ├── components/           # React components
│   │   ├── ui/               # Design system (Blueprint)
│   │   ├── shell/            # App shell (nav, sidebar)
│   │   ├── landing/          # Marketing site
│   │   ├── effects/          # Animations & effects
│   │   ├── bcm/              # Business context
│   │   ├── campaigns/        # Campaign UI
│   │   ├── foundation/       # Foundation UI
│   │   ├── moves/            # Moves UI
│   │   ├── muse/             # Muse AI UI
│   │   └── workspace/        # Workspace provider
│   ├── services/             # API service clients
│   ├── stores/               # Zustand state stores
│   ├── types/                # TypeScript types
│   ├── lib/                  # Utilities
│   ├── data/                 # Static data
│   └── styles/               # CSS
├── backend/                  # FastAPI backend
│   ├── api/                  # Route handlers
│   │   ├── v1/               # Versioned API routes
│   │   ├── registry.py       # Router registry
│   │   └── system.py         # Health/root endpoints
│   ├── app/                  # App lifecycle & middleware
│   ├── core/                 # Infrastructure (Supabase, Redis, GCS)
│   ├── services/             # Business logic
│   ├── schemas/              # Pydantic models
│   ├── config/               # Settings
│   ├── fixtures/             # Seed data
│   ├── templates/            # Email templates
│   ├── tests/                # Backend tests
│   ├── main.py               # ASGI entrypoint
│   └── app_factory.py        # App factory
├── supabase/migrations/      # Database migrations (SQL)
├── public/                   # Static assets
├── scripts/                  # Dev scripts (smoke test, health check)
├── ADRs/                     # Architectural Decision Records
├── AGENTS.md                 # Repo constitution
├── REPO_MAP.md               # Directory & entrypoint map
├── API_INVENTORY.md          # API surface inventory
└── AUTH_INVENTORY.md          # Auth/identity model
```

## Scripts

```bash
npm run dev             # Start Next.js dev server
npm run build           # Lint + typecheck + build
npm run start           # Start production server
npm run lint            # ESLint
npm run type-check      # TypeScript check
npm run test            # Vitest unit tests
npm run test:e2e        # Playwright E2E tests
npm run smoke           # Repo structure smoke test
npm run health-check    # Backend + proxy health check
```

## Environment Variables

Copy `.env.example` to `.env.local` and fill in:

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_APP_URL` | Frontend URL (default: `http://localhost:3000`) |
| `NEXT_PUBLIC_API_URL` | Backend URL (default: `http://localhost:8000`) |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key |
| `SENTRY_DSN` | Sentry DSN (optional) |

Backend env vars are in `backend/.env.example`.

## Architecture

The frontend proxies all API calls through `src/app/api/[...path]/route.ts` to avoid CORS issues. The backend registers all routes via `backend/api/registry.py` under the `/api` prefix.

Current mode: **no-auth reconstruction**. Tenant isolation is via `x-workspace-id` header. See `AUTH_INVENTORY.md` for details.

## Deployment

Frontend deploys to **Vercel** via `vercel.json`. Backend deploys separately (Render). See `vercel.json` for build configuration.
