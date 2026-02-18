# Authentication System - Architecture

## Overview

RaptorFlow uses a **dual-mode authentication system** that supports both development and production environments:

- **Demo Mode**: For local development (any credentials work)
- **Supabase Mode**: Production-ready email/password authentication
- **Disabled Mode**: No authentication (development only)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Login Page   │  │ Signup Page  │  │ Auth Store  │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             ▼                                   │
│                   ┌───────────────┐                            │
│                   │ Supabase JS   │                            │
│                   │ (HTTP Cookies)│                            │
│                   └───────┬───────┘                            │
└───────────────────────────┼───────────────────────────────────┘
                            │
                    HTTP + Cookies
                            │
┌───────────────────────────┼───────────────────────────────────┐
│                     BACKEND                                     │
│                   ┌───────┴───────┐                           │
│                   │  Auth Routes  │                           │
│                   │ /auth/login   │                           │
│                   │ /auth/signup  │                           │
│                   │ /auth/refresh │                           │
│                   │ /auth/logout   │                           │
│                   └───────┬───────┘                           │
│                           │                                   │
│         ┌─────────────────┼─────────────────┐                 │
│         ▼                 ▼                 ▼                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │   Demo Auth  │ │Supabase Auth│ │ Disabled Auth│       │
│  │   Service   │ │   Service   │ │   Service   │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
│                           │                                   │
│                           ▼                                   │
│                   ┌───────────────┐                           │
│                   │   Supabase    │                           │
│                   │ Auth API      │                           │
│                   └───────────────┘                           │
└───────────────────────────────────────────────────────────────┘
```

## Authentication Flow

### Login Flow

```
User → Login Page → API /auth/login → Auth Service → Supabase
                                                          ↓
User ← Response ← Set Cookies ← Session Created ←──────────┘
```

### Token Refresh Flow

```
Request → Expired Token Detect → API /auth/refresh → Supabase
                                              ↓
New Tokens ← Response ← Refresh Token Valid ←─────┘
                                              ↓
                                   Set New Cookies
```

### Protected Route Flow

```
Request → Middleware → Check Cookie → Invalid → Redirect /login
                                        ↓
                                  Valid Token
                                        ↓
                              Verify with Supabase
                                        ↓
                              Allow Request
```

## Security Features

### 1. HTTP-Only Cookies
- Tokens stored in `HttpOnly` cookies
- JavaScript cannot access tokens
- Protected from XSS attacks

### 2. Token Expiry
- Access token: 1 hour (3600s)
- Refresh token: 7 days (604800s)
- Auto-refresh before expiry

### 3. Rate Limiting
- Login: 5 attempts per minute
- Signup: 3 attempts per hour

### 4. Password Requirements
- Minimum 8 characters
- Maximum 72 characters (bcrypt limit)
- Email format validation

### 5. Row Level Security (RLS)
- Database-level access control
- Users can only access their workspace data
- Service role bypass for admin operations

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Public anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Secret service role key |
| `AUTH_MODE` | Yes | `demo`, `supabase`, or `disabled` |

## Related Files

- **Backend**: `backend/services/auth/`
- **API**: `backend/api/v1/auth/routes.py`
- **Frontend**: `src/stores/authStore.ts`
- **Middleware**: `src/middleware.ts`
- **Database**: `scripts/migrations/rls_policies.sql`
