# Raptorflow Repo Map

Canonical repository map for the renovated stack.

## Top-Level Modules

- `src/`: Next.js frontend app, UI components, client-side services, state stores.
- `backend/`: FastAPI backend, LangGraph orchestrators, service layer, schemas.
- `supabase/`: SQL migrations and Supabase local metadata.
- `scripts/`: Operational checks, audits, and helper tooling.
- `tests/`: Cross-cutting test harness directory (backend unit tests are in `backend/tests`).
- `documentation/`: Canonical docs and generated contracts.
- `public/`: Static frontend assets.

## Frontend Entrypoints

- `src/app/layout.tsx`: Next.js app shell layout.
- `src/app/page.tsx`: Landing page.
- `src/app/(shell)/dashboard/page.tsx`: Main app dashboard.
- `src/app/(shell)/onboarding/page.tsx`: BCM-first onboarding workflow.
- `src/app/api/[...path]/route.ts`: Backend API proxy layer.

## Backend Entrypoints

- `backend/main.py`: ASGI entrypoint (`app = create_app()`).
- `backend/app_factory.py`: Canonical FastAPI app builder.
- `backend/api/registry.py`: Router registry for `/api/*`.
- `backend/app/lifespan.py`: Service initialization and shutdown lifecycle.

## AI Orchestration Modules

- `backend/agents/langgraph_muse_orchestrator.py`: Muse generation graph.
- `backend/agents/langgraph_context_orchestrator.py`: BCM seed/rebuild/reflect graph.
- `backend/agents/langgraph_campaign_moves_orchestrator.py`: Campaign and moves graph.
- `backend/agents/langgraph_optional_orchestrator.py`: Search/scraper orchestration gate.
- `backend/agents/ai_runtime_profiles.py`: Topology and intensity profiles.

## Data and Integration Modules

- `backend/core/supabase_mgr.py`: Canonical Supabase client creation.
- `backend/core/storage_mgr.py`: Supabase Storage manager.
- `backend/services/email_service.py`: Resend email integration.
- `backend/services/vertex_ai_service.py`: Vertex AI inference integration.
- `backend/api/v1/workspaces.py`: Onboarding + workspace lifecycle.
- `backend/api/v1/assets.py`: Workspace asset upload/list/delete API.
