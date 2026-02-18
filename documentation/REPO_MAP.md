# RaptorFlow Repository Map

Last updated: 2026-02-18

## Runtime Entry Points

- Frontend app shell: `src/app/layout.tsx`
- Frontend landing route: `src/app/page.tsx`
- Frontend API proxy: `src/app/api/[...path]/route.ts`
- Frontend middleware: `src/middleware.ts`
- Backend ASGI entrypoint: `backend/main.py`
- Backend app factory: `backend/app_factory.py`
- Backend router registry: `backend/api/registry.py`

## Backend Modules

- API system routes: `backend/api/system.py`
- API domain routes (modular): `backend/api/v1/*/routes.py`
- AI hub kernel: `backend/ai/hub/`
- BCM core: `backend/bcm/core/`

## Frontend Modules

- Shell routes: `src/app/(shell)/`
- Public routes: `src/app/(public)/`
- Auth routes: `src/app/login/`, `src/app/signup/`, `src/app/auth/`
- Client stores: `src/stores/`

## Test Surface

- Backend tests: `backend/tests/`
- Frontend/e2e tests: `tests/`

## Documentation Contracts

- `documentation/REPO_MAP.md`
- `documentation/API_INVENTORY.md`
- `documentation/AUTH_INVENTORY.md`
- `documentation/AI_HUB_BEDROCK.md`
