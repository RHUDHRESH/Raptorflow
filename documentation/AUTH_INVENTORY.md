# Auth Inventory

Last updated: 2026-02-18

## Auth Surface Files

- `src/app/login/page.tsx`
- `src/app/signup/page.tsx`
- `src/app/auth/callback/route.ts`
- `src/middleware.ts`
- `src/stores/authStore.ts`
- `src/lib/supabase/client.ts`
- `src/lib/supabase/middleware.ts`
- `backend/api/v1/auth/routes.py`

## Backend Auth Endpoints

- `GET /api/auth/health`
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `POST /api/auth/refresh`
- `POST /api/auth/verify`
- `GET /api/auth/me`
- `POST /api/auth/reset-password`
