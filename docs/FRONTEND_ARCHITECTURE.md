# Frontend Architecture

## Current shape

- Next.js 15 App Router
- Route groups for public, auth, and app surfaces
- Clerk for auth and route protection
- TanStack Query for server state
- Zustand for local UI state
- PixiJS for the Office canvas
- Typed API calls through `@raptorflow/contracts` and `apps/web/src/lib/api.ts`

## Active services

- API base URL from `NEXT_PUBLIC_API_BASE_URL`
- Clerk provider in the root layout
- Protected app routes use `apps/web/src/middleware.ts`
- Health hook lives in `apps/web/src/features/shared/hooks/useHealth.ts`

## Removed from the active stack

- Offline mock mode
- Removed offline adapter references
- Removed external inference references
- Removed legacy cache references
- Local mock Office server
