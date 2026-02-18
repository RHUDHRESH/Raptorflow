# Salvation Plan - Auth & Demo Mode

## Overview
Shed broken auth, create clean demo/development mode, fix workspace creation.

---

## PHASE 1: DELETE BROKEN AUTH CODE - ✅ COMPLETED

### Tasks
- [X] Remove "No-Auth Reconstruction Mode" comments from all files
- [X] Remove bypass logic in `services/auth/service.py`
- [X] Clean up `api/v1/auth/routes.py` for new auth flow
- [X] Remove any hardcoded test/fake auth

---

## PHASE 2: CREATE DEMO/DEVELOPMENT MODE - ✅ COMPLETED

### Tasks
- [X] Add AUTH_MODE to `config/settings.py`
- [X] Create `services/auth/demo.py` - DemoAuthService class
- [X] Create `services/auth/factory.py` - Auth service factory
- [X] Update `services/auth/__init__.py` exports
- [X] Add AUTH_MODE=demo to `.env`

---

## PHASE 3: FIX WORKSPACE CREATION - ✅ COMPLETED

### Tasks
- [X] Add auto-slug generation in workspaces service
- [X] Add auto-workspace creation for demo mode
- [X] Create demo data seeding function

---

## PHASE 4: FIX API ENDPOINTS - ✅ COMPLETED

### Tasks
- [X] Create `api/dependencies/auth.py` - get_current_user dependency
- [X] Update `api/v1/auth/routes.py` - add /login, /logout, /signup
- [X] Update `api/v1/workspaces/routes.py` - add auth dependency
- [X] Update `api/v1/campaigns/routes.py` - add auth dependency
- [X] Update `api/v1/moves/routes.py` - add auth dependency
- [X] Update `api/v1/assets/routes.py` - add auth dependency
- [X] Update `api/v1/muse/routes.py` - add auth dependency

---

## PHASE 5: TESTING - ✅ COMPLETED

### Tasks
- [X] Test demo mode works without Supabase
- [X] Test workspace auto-creation
- [X] Test all protected endpoints
- [X] Verify app creates successfully

---

## ✅ ALL PHASES COMPLETE

---

## Summary

### New Files
- `services/auth/demo.py` - DemoAuthService
- `services/auth/factory.py` - get_auth_service()
- `api/dependencies/auth.py` - get_current_user

### Modified Files
- `config/settings.py` - Add AUTH_MODE
- `.env` - Add AUTH_MODE=demo
- `services/auth/service.py` - Rewrite
- `services/auth/__init__.py` - Update exports
- `api/v1/auth/routes.py` - Add endpoints
- `api/v1/*/routes.py` - Add auth dependencies

---

## Success Criteria
- [X] AUTH_MODE=demo makes everything work
- [X] Workspace auto-creation works
- [X] All protected endpoints require auth
- [X] App creates with 66 routes (was 62, added 4 new auth endpoints)

---

## Summary

### What's Working Now:
- Demo mode auth (no Supabase needed)
- `/api/auth/login` - returns demo token
- `/api/auth/signup` - returns demo token  
- `/api/auth/verify` - verifies demo token
- `/api/auth/me` - returns current user
- `/api/auth/health` - returns auth health status

### Auth Modes:
- `AUTH_MODE=demo` - Local demo mode (default, works without Supabase)
- `AUTH_MODE=supabase` - Real Supabase auth (when configured)
- `AUTH_MODE=disabled` - No auth (development only)
