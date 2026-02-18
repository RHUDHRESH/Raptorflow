# RAPTORFLOW AUTHENTICATION - COMPREHENSIVE IMPLEMENTATION PLAN

## EXECUTIVE SUMMARY

**Current State:** 
- Multiple security vulnerabilities in demo mode
- Missing frontend auth
- No proper token handling
- Wrong Supabase credentials in .env

**Target State:**
- Secure HTTP-only cookie-based auth
- Dual mode (demo/supabase via ENV)
- Full test coverage
- Production-ready

---

## PHASE 1: ENVIRONMENT FIX (Foundation)

### 1.1 Fix Supabase Credentials

| File | Current Issue | Fix |
|------|---------------|-----|
| `.env` | Wrong URL & outdated keys | Update to `vpwwzsanuhpkvgorgncnc` |
| `.env.local` | Same issues | Mirror .env |
| `backend/.env` | Same issues | Mirror .env |
| `.env.example` | Missing auth vars | Add complete template |

**Required Variables:**
```
# Supabase (FIXED)
SUPABASE_URL=https://vpwwzsanuhpkvgorgncnc.supabase.co
NEXT_PUBLIC_SUPABASE_URL=https://vpwwzsanuhpkvgorgncnc.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzOTk1OTEsImV4cCI6MjA3Nzk3NTU5MX0.-clyTrDDlCNpUGg-MEgXIki70uBt4oIFPuSA8swNuTU
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzOTk1OTEsImV4cCI6MjA3Nzk3NTU5MX0.-clyTrDDlCNpUGg-MEgXIki70uBt4oIFPuSA8swNuTU
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw
SUPABASE_DB_URL=postgresql://postgres:[YOUR-PASSWORD]@db.vpwwzsanuhpkvgorgncnc.supabase.co:5432/postgres

# Auth Mode
AUTH_MODE=supabase

# Session
ACCESS_TOKEN_EXPIRY=3600      # 1 hour
REFRESH_TOKEN_EXPIRY=604800   # 7 days
```

### 1.2 Create .env Verification Script

- [ ] Create `scripts/verify_env_auth.py`
- [ ] Checks all required env vars present
- [ ] Verifies Supabase URL matches project ref in keys
- [ ] Validates keys are valid JWT format
- [ ] Validates AUTH_MODE is valid
- [ ] Validates database URL is valid

### 1.3 Verify Supabase Connection

- [ ] Run verify script
- [ ] Ping Supabase API
- [ ] Verify database connection
- [ ] Confirm RLS status

---

## PHASE 2: BACKEND AUTH (Core)

### 2.1 Fix SupabaseAuthService

**File:** `backend/services/auth/supabase.py`

| Issue | Fix |
|-------|-----|
| get_user() creates new event loop | Make fully async |
| No token expiry check | Add expiry validation |
| Uses anon_key for verification | Use service_role for sensitive ops |
| Missing error handling | Add comprehensive error handling |

**New Methods:**
- [ ] `verify_token()` - Check token, call Supabase /auth/v1/user, validate response
- [ ] `refresh_session()` - Validate refresh_token, call Supabase token refresh, rotate tokens
- [ ] `sign_out()` - Invalidate refresh token in Supabase, clear local session

### 2.2 Fix DemoAuthService

**File:** `backend/services/auth/demo.py`

| Issue | Fix |
|-------|-----|
| Accepts ANY password | Validate password format |
| Tokens too easy to guess | Use cryptographically secure tokens |
| No proper response format | Align with Supabase response |

**Security Fix:**
- [ ] Replace insecure token check with cryptographically secure tokens
- [ ] Validate password format in demo mode
- [ ] Align response format with Supabase

### 2.3 Add HTTP-Only Cookie Support

**File:** `backend/api/v1/auth/routes.py`

- [ ] Add Set-Cookie header for access_token (HttpOnly, Secure, SameSite=Lax, max_age=3600)
- [ ] Add Set-Cookie header for refresh_token (HttpOnly, Secure, SameSite=Lax, max_age=604800)
- [ ] Apply to /auth/login endpoint
- [ ] Apply to /auth/signup endpoint

### 2.4 Fix Auth Dependencies

**File:** `backend/api/dependencies/auth.py`

| Issue | Fix |
|-------|-----|
| Demo mode returns user without token | Require token always |
| Mixed async/sync handling | Standardize to async |
| No token expiry | Add expiry validation |

- [ ] Remove demo mode auto-login without token
- [ ] Standardize all auth to async
- [ ] Add token expiry validation

### 2.5 Add Rate Limiting

- [ ] Add rate limiting to /auth/login (5 attempts per minute)
- [ ] Add rate limiting to /auth/signup (3 attempts per IP per hour)
- [ ] Add rate limiting to /auth/verify (30 attempts per minute)

### 2.6 Add Input Validation

- [ ] Update password minimum to 8 characters
- [ ] Add email regex validation
- [ ] Add password strength validation

### 2.7 Backend Tests

- [ ] `test_supabase_auth_signup_success` - Valid signup returns user
- [ ] `test_supabase_auth_signup_weak_password` - Reject <8 chars
- [ ] `test_supabase_auth_signup_invalid_email` - Reject invalid email
- [ ] `test_supabase_auth_login_success` - Valid login returns tokens
- [ ] `test_supabase_auth_login_wrong_password` - Reject wrong password
- [ ] `test_supabase_auth_login_rate_limit` - Block after 5 attempts
- [ ] `test_supabase_auth_token_verify_valid` - Valid token returns user
- [ ] `test_supabase_auth_token_verify_expired` - Expired token rejected
- [ ] `test_supabase_auth_token_refresh` - Refresh returns new tokens
- [ ] `test_supabase_auth_logout` - Logout invalidates token
- [ ] `test_demo_auth_rejects_weak_password` - Demo mode validates password
- [ ] `test_demo_auth_secure_tokens` - Demo tokens are unpredictable

---

## PHASE 3: FRONTEND AUTH (Integration)

### 3.1 Install Dependencies

- [ ] Install `@supabase/ssr` package
- [ ] Install `@supabase/supabase-js` package
- [ ] Update package.json
- [ ] Run npm install

### 3.2 Create Supabase Client

- [ ] Create `src/lib/supabase/client.ts` (browser client)
- [ ] Create `src/lib/supabase/server.ts` (server client)
- [ ] Configure cookie handling
- [ ] Test client initialization

### 3.3 Create Auth Store

- [ ] Create `src/stores/authStore.ts`
- [ ] Implement user state management
- [ ] Implement session state management
- [ ] Add signOut action

### 3.4 Create Auth Provider

- [ ] Create `src/components/providers/AuthProvider.tsx`
- [ ] Add onAuthStateChange listener
- [ ] Handle session persistence
- [ ] Add route redirection logic

### 3.5 Create Auth Pages

- [ ] Create `src/app/(auth)/login/page.tsx`
- [ ] Create `src/app/(auth)/signup/page.tsx`
- [ ] Create `src/app/(auth)/verify-email/page.tsx`
- [ ] Create `src/app/(auth)/forgot-password/page.tsx`

### 3.6 Add Middleware Route Protection

- [ ] Create `src/middleware.ts`
- [ ] Add authentication check
- [ ] Add protected route redirect
- [ ] Add auth page redirect for logged in users
- [ ] Configure matcher

### 3.7 Frontend Tests

- [ ] `test_login_success` - Valid credentials log in
- [ ] `test_login_invalid` - Invalid credentials show error
- [ ] `test_signup_validation` - Weak password rejected
- [ ] `test_logout` - User logged out and redirected
- [ ] `test_protected_route` - Unauthenticated blocked
- [ ] `test_session_persistence` - Refresh maintains session
- [ ] `test_token_refresh` - Auto-refresh works

---

## PHASE 4: DATABASE SECURITY (RLS)

### 4.1 Audit Current RLS

- [ ] Run `scripts/supabase_production_check.py`
- [ ] Verify all tables have RLS enabled
- [ ] Verify policies exist for each table
- [ ] Verify service role bypass works correctly

### 4.2 Create RLS Policies

- [ ] Enable RLS on profiles table
- [ ] Enable RLS on workspaces table
- [ ] Enable RLS on business_context_manifests table
- [ ] Create "Users can view own profile" policy
- [ ] Create "Users can view own workspace" policy
- [ ] Create "Users can view own BCM" policy

### 4.3 Database Tests

- [ ] `test_rls_profiles` - User cannot read other profiles
- [ ] `test_rls_workspaces` - User cannot read other workspaces
- [ ] `test_rls_bcm` - User cannot read other BCMs
- [ ] `test_service_role_bypass` - Service role can access all

---

## PHASE 5: SECURITY HARDENING

### 5.1 Security Checklist

- [ ] HTTPS enforced in production
- [ ] HttpOnly cookies only
- [ ] Secure flag in production
- [ ] SameSite=Lax
- [ ] Rate limiting on auth endpoints
- [ ] Account lockout after failed attempts
- [ ] Password minimum 8 chars
- [ ] Email validation regex
- [ ] CSRF protection
- [ ] XSS prevention headers

### 5.2 Add Security Headers

- [ ] Add X-Content-Type-Options header
- [ ] Add X-Frame-Options header
- [ ] Add X-XSS-Protection header
- [ ] Add Strict-Transport-Security header

---

## PHASE 6: TESTING & VALIDATION

### 6.1 Manual Test Scenarios

#### Demo Mode Tests
| # | Test | Expected |
|---|------|----------|
| 1 | Set AUTH_MODE=demo | Demo auth activates |
| 2 | POST /auth/login any credentials | Returns demo user |
| 3 | GET /auth/me with demo-token | Returns demo user |
| 4 | POST /auth/logout | Session cleared |

#### Supabase Mode Tests
| # | Test | Expected |
|---|------|----------|
| 1 | Set AUTH_MODE=supabase | Supabase auth activates |
| 2 | POST /auth/signup valid email/password | User created in Supabase |
| 3 | POST /auth/signup weak password | 400 error |
| 4 | POST /auth/login correct credentials | Returns tokens + user |
| 5 | POST /auth/login wrong password | 401 error |
| 6 | GET /auth/me with valid token | Returns user data |
| 7 | GET /auth/me with invalid token | 401 error |
| 8 | POST /auth/logout | Token invalidated |
| 9 | Wait for token expiry | Auto-refresh works |
| 10 | Use expired refresh token | 401 error |

#### Cookie Tests
| # | Test | Expected |
|---|------|----------|
| 1 | Login sets HttpOnly cookies | Cookies present |
| 2 | JavaScript cannot read cookies | httponly confirmed |
| 3 | Logout clears cookies | Cookies removed |
| 4 | Cross-site request with cookie | SameSite=Lax blocks |

#### Integration Tests
| # | Test | Expected |
|---|------|----------|
| 1 | Frontend login flow | Full flow works |
| 2 | Protected route redirect | Unauth → login |
| 3 | Logout redirects | User → login |
| 4 | Session persists on refresh | Auto-login |

### 6.2 Automated Test Suite

- [ ] Run backend auth tests: `pytest backend/tests/unit/test_auth*.py -v`
- [ ] Run frontend tests: `npm run test:auth`
- [ ] Run E2E tests: `npx playwright test auth.spec.ts`

### 6.3 Security Audit Script

- [ ] Create `scripts/security_audit.py`
- [ ] Check demo tokens are unpredictable
- [ ] Check rate limiting enabled
- [ ] Check password minimum 8 chars
- [ ] Check RLS enabled on all tables
- [ ] Check HttpOnly cookies used
- [ ] Check no secrets in frontend

---

## PHASE 7: DOCUMENTATION

### 7.1 Auth Documentation

- [ ] Create `docs/auth/ARCHITECTURE.md` - Auth flow diagrams
- [ ] Create `docs/auth/API.md` - API endpoints
- [ ] Create `docs/auth/SECURITY.md` - Security measures
- [ ] Create `docs/auth/TROUBLESHOOTING.md` - Common issues

### 7.2 Env Var Documentation

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Public key |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Secret key (server only) |
| `AUTH_MODE` | Yes | demo/supabase/disabled |
| `ACCESS_TOKEN_EXPIRY` | No | Default: 3600 |
| `REFRESH_TOKEN_EXPIRY` | No | Default: 604800 |

---

## SUMMARY: COMPLETE CHECKLIST

### Phase 1: Environment
- [ ] Fix .env files with correct Supabase credentials
- [ ] Verify Supabase connection
- [ ] Run env verification script

### Phase 2: Backend
- [ ] Fix SupabaseAuthService
- [ ] Fix DemoAuthService  
- [ ] Add HTTP-only cookie support
- [ ] Fix auth dependencies
- [ ] Add rate limiting
- [ ] Add input validation
- [ ] Run backend auth tests (12 tests)

### Phase 3: Frontend
- [ ] Install @supabase/ssr
- [ ] Create client.ts
- [ ] Create server.ts
- [ ] Create authStore.ts
- [ ] Create AuthProvider.tsx
- [ ] Create login/signup pages
- [ ] Add middleware.ts
- [ ] Run frontend auth tests (7 tests)

### Phase 4: Database
- [ ] Audit RLS
- [ ] Create RLS policies
- [ ] Run database tests (4 tests)

### Phase 5: Security
- [ ] Complete security checklist
- [ ] Add security headers

### Phase 6: Testing
- [ ] Run all 22 manual tests
- [ ] Run automated tests
- [ ] Run security audit

### Phase 7: Documentation
- [ ] Create auth documentation

---

## QUICK START

To start implementation:

1. **Phase 1**: Fix environment variables
   ```bash
   # Update .env with correct Supabase credentials
   ```

2. **Phase 2**: Run backend tests
   ```bash
   pytest backend/tests/unit/test_auth*.py -v
   ```

3. **Phase 3**: Install frontend dependencies
   ```bash
   npm install @supabase/ssr @supabase/supabase-js
   ```

4. **Phase 4**: Run database audit
   ```bash
   python scripts/supabase_production_check.py
   ```

5. **Phase 5**: Run security audit
   ```bash
   python scripts/security_audit.py
   ```

---

*Last Updated: 2026-02-14*
*Version: 1.0*
