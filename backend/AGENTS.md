# backend/ - Backend Root

**Parent:** `./AGENTS.md`

## OVERVIEW
FastAPI Python backend with clean architecture, LangGraph AI orchestration, and Supabase integration.

## STRUCTURE
```
backend/
├── api/v1/           # REST API routes
├── features/          # Domain modules (clean architecture)
│   ├── auth/         # JWT + session auth
│   ├── campaign/     # Campaign CRUD
│   ├── workspace/    # Workspace management
│   └── asset/        # Asset management
├── services/         # Business services
├── ai/               # LangGraph orchestration
├── infrastructure/   # Storage, tasks, rate limiting
├── bcm/             # Business Context Memory
└── tests/           # pytest test suite
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| API routes | `backend/api/v1/` | FastAPI routers |
| Auth logic | `backend/features/auth/` | JWT, sessions |
| Business logic | `backend/services/` | Campaign, Move, Muse services |
| AI orchestration | `backend/ai/` | LangGraph workflows |
| Domain models | `backend/features/*/domain/` | Entities |

## CONVENTIONS
- Clean architecture: `domain/` → `application/` → `adapters/`
- Pydantic v2 for validation
- Async/await for I/O operations
- pytest for testing

## ANTI-PATTERNS
- NO sync DB calls in route handlers
- NO hardcoded config - use `config.py`
- NO API keys in code - use environment variables
- NO blocking calls in request handlers
