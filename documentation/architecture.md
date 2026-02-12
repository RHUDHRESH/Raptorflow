# System Architecture

## Runtime Surfaces

- Frontend app: Next.js in `src/`.
- Backend app: FastAPI in `backend/`.
- AI orchestration runtime: LangGraph in `backend/agents/`.
- Database and storage schema: Supabase migrations in `supabase/migrations/`.
- Test and automation surface: `tests/` and `scripts/`.

## Primary Entrypoints

- Frontend development: `npm run dev`
- Frontend production build: `npm run build`
- Backend ASGI app: `backend/main.py` -> `backend/app_factory.py`
- Container runtime: `Dockerfile` + `docker-entrypoint.sh`

## API Baseline

- Canonical backend prefix: `/api`
- Auth: `/api/auth/*`
- Assets: `/api/assets/*`
- Workspaces: `/api/workspaces/*`
- Operations: `/api/ops/*`
- Muse generation: `/api/muse/*` backed by `LangGraphMuseOrchestrator`.

## Storage Baseline

- App uploads are Supabase Storage-backed.
- Asset metadata is persisted through `assets` table migrations.
