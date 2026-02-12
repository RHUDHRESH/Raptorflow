# Module Boundaries

## Root Modules

- `src/`: UI, client-side services, frontend state and routes.
- `backend/`: API routes, service layer, schemas, backend core.
- `backend/agents/`: canonical LangGraph orchestration nodes and graph entrypoints.
  - `langgraph_muse_orchestrator.py`: Muse content generation flow.
  - `langgraph_context_orchestrator.py`: BCM seed/rebuild/reflect flow.
  - `langgraph_campaign_moves_orchestrator.py`: campaign/move domain orchestration.
  - `langgraph_optional_orchestrator.py`: search/scraper optional-module gate.
- `supabase/`: SQL migrations and Supabase project state.
- `scripts/`: operational scripts, inventory tools, deployment helpers.
- `tests/`: test suites and verification utilities.
- `public/`: static assets served by frontend.

## Dependency Rules

- Frontend code in `src/` must not import from `backend/`.
- Backend code in `backend/` must not depend on frontend files.
- Agent orchestration must run through `backend/agents/` (LangGraph only).
- `scripts/` may read both frontend and backend but should remain non-runtime.
- Schema changes must land first in `supabase/migrations/`, then app code.

## Cleanup Rules

- No legacy archives at root.
- No duplicate top-level component trees outside `src/components`.
- Build cache directories stay untracked and disposable.
