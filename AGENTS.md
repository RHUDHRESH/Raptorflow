# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-15
**Commit:** 2c6860077
**Branch:** main

## OVERVIEW
RaptorFlow - Full-stack marketing automation platform with Next.js frontend and FastAPI backend. Features AI-powered campaign orchestration via LangGraph, Supabase database, and Google Cloud integration.

## STRUCTURE
```
raptorflow/
├── src/                    # Next.js 14 frontend (TypeScript)
│   ├── app/               # App Router pages (39 routes)
│   ├── components/       # React components (20+ subdirs)
│   ├── lib/              # Utilities (Supabase, GSAP, AI)
│   ├── hooks/            # Custom React hooks
│   ├── stores/           # Zustand state management
│   └── middleware/      # Next.js middleware
├── backend/              # FastAPI backend (Python 3.11+)
│   ├── api/             # REST API routes
│   ├── features/        # Domain modules (clean architecture)
│   │   ├── auth/        # Authentication
│   │   ├── campaign/    # Campaign management
│   │   ├── workspace/   # Workspace management
│   │   └── asset/       # Asset management
│   ├── services/        # Business services
│   ├── ai/              # AI orchestration (LangGraph)
│   ├── infrastructure/  # Storage, tasks, rate limiting
│   └── bcm/             # Business context memory
├── tests/               # Frontend tests (Vitest, Playwright)
└── documentation/       # Auth documentation
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Frontend UI | `src/components/` | 20+ subdirs, large component library |
| Page routes | `src/app/` | Next.js App Router, 39 pages |
| Backend API | `backend/api/v1/` | FastAPI routes |
| Auth logic | `backend/features/auth/` | JWT, sessions, Supabase |
| AI orchestration | `backend/ai/` | LangGraph workflows |
| State management | `src/stores/` | Zustand stores |
| Testing | `tests/` (frontend), `backend/tests/` | Vitest + Playwright |

## CODE MAP
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| AgentChat | component | `src/components/AgentChat.tsx` | Main AI chat UI |
| WorkflowBuilder | component | `src/components/WorkflowBuilder.tsx` | Campaign workflow builder |
| campaign_service | service | `backend/services/campaign_service.py` | Campaign CRUD |
| auth_service | service | `backend/features/auth/application/services.py` | Auth logic |
| vertex_ai_service | service | `backend/services/vertex_ai_service.py` | Google Vertex AI |

## CONVENTIONS
- **Frontend**: Next.js App Router, Tailwind CSS, Zustand, Framer Motion
- **Backend**: FastAPI, Pydantic v2, clean architecture (domain/application/adapters)
- **Testing**: Vitest (unit), Playwright (e2e), pytest (backend)
- **Linting**: ESLint (JS/TS), Ruff/Black (Python)
- **State**: Zustand for client state, React Query patterns where needed

## ANTI-PATTERNS (THIS PROJECT)
- NO direct Supabase client in components - use via `src/lib/supabase/`
- NO API keys in frontend code - use Next.js API routes
- NO hardcoded environment variables - use `.env` files
- NO synchronous AI calls in request handlers - use async patterns

## UNIQUE STYLES
- Hexagonal architecture in `backend/features/`
- AI runtime profiles for different LLM configurations
- Business Context Memory (BCM) for persistent context
- LangGraph for orchestrating multi-step AI workflows

## COMMANDS
```bash
# Frontend
npm run dev          # Start Next.js dev server
npm run build        # Build for production
npm run test         # Run Vitest tests
npm run test:e2e     # Run Playwright e2e tests
npm run lint         # ESLint check

# Backend
cd backend
python -m pytest     # Run backend tests
python main.py       # Start FastAPI server

# Docker
docker-compose up    # Start all services
```

## NOTES
- Multi-language project: TypeScript (frontend) + Python (backend)
- Deep directory structure (max depth: 10)
- Supabase for auth + database
- Redis (Upstash) for caching
- Sentry for error tracking
