# RaptorFlow Security Fix Plan

## Overview
Comprehensive security audit found 22 vulnerabilities (P0-P3). This plan addresses ALL of them.

## Dependencies
- ✅ Upstash Redis already configured
- ✅ python-jose installed
- ✅ passlib installed

---

## PHASE 1: P0 CRITICAL (Day 1)

### 1.1 Demo Mode Production Block + Require AUTH_MODE
**File:** `backend/services/auth/factory.py`
- Block demo mode in production
- Require explicit AUTH_MODE
- Fail fast on misconfiguration

### 1.2 Fix SECRET_KEY
**File:** `backend/config/settings.py`
- Remove empty default
- Add production validation

### 1.3 Move Tokens from localStorage → HTTP-Only Cookies
**Files:** `src/lib/supabase/client.ts`, `src/stores/authStore.ts`
- Use Supabase cookie-only sessions
- Disable localStorage

### 1.4 Demo Mode Password Verification
**File:** `backend/services/auth/demo.py`
- Add credential verification
- Block from production

---

## PHASE 2: P1 HIGH (Days 2-4)

### 2.1 IP Spoofing Protection
**File:** `backend/api/v1/auth/routes.py`
- Validate X-Forwarded-For
- Trusted proxy list

### 2.2 Token Verification Fix
**File:** `backend/services/auth/demo.py`
- Store tokens in dict
- Proper verification

### 2.3 Workspace IDOR Prevention
**File:** `backend/api/dependencies/auth.py`
- Validate workspace permissions
- Return 403 if no access

### 2.4 CORS Fix
**File:** `backend/config/settings.py`
- Never * with credentials
- Whitelist origins

### 2.5 Token Revocation
**Files:** New file + auth services
- Redis blacklist
- Logout invalidates tokens

### 2.6 Refresh Token Separation
**File:** `backend/services/auth/demo.py`
- Separate storage
- Token type validation

### 2.7 Logout Logging
**File:** `backend/api/v1/auth/routes.py`
- Add audit trail

---

## PHASE 3: P2 MEDIUM (Days 5-10)

### 3.1 Distributed Rate Limiting
**File:** `backend/api/v1/auth/routes.py`
- Redis-based rate limiting
- Sliding window

### 3.2 Rate Limit /verify
**File:** `backend/api/v1/auth/routes.py`
- 30 req/min limit

### 3.3 Password Policy
**Files:** demo.py, routes.py
- Min 8 chars
- Complexity requirements

### 3.4 HTTP Status Codes
**File:** `backend/api/v1/auth/routes.py`
- 401 for invalid tokens
- Proper error responses

### 3.5 Hide Sensitive Info
**Files:** demo.py, routes.py
- Remove paths from errors
- Sanitize messages

### 3.6 Email Validation Bypass
**File:** `backend/services/auth/demo.py`
- URL encoding detection
- Unicode normalization

### 3.7 CSRF Protection
**File:** `routes.py`
- SameSite=strict
- Origin header check

### 3.8 Input Length Limits
**File:** `routes.py`
- Email max 254
- Password max 72

---

## PHASE 4: P3 LOW (Days 11-14)

### 4.1 Security Headers
**File:** `backend/app_factory.py`
- HSTS
- X-Content-Type-Options
- X-Frame-Options
- CSP

### 4.2 Cache-Control
**File:** `routes.py`
- No-store on auth

### 4.3 Session Limits
**File:** `demo.py`
- Lower threshold
- Memory monitoring

---

## NEW FILES

| File | Purpose |
|------|---------|
| `backend/services/auth/redis_rate_limiter.py` | Redis rate limiting |
| `backend/services/auth/token_revocation.py` | Token blacklist |

---

## TESTING

1. Pre-fix vulnerability tests
2. Unit tests per fix
3. Integration tests
4. Security tests (SQLi, XSS, bypass)
5. Load tests

---

## ROLLBACK

- Git branches per phase
- Backup before changes
- Test in dev first

---

## EXECUTION ORDER

1. [x] factory.py - AUTH_MODE - REQUIRES EXPLICIT
2. [x] settings.py - SECRET_KEY + AUTH_MODE validation  
3. [x] demo.py - Multiple fixes (password, email, token, health)
4. [x] routes.py - IP spoofing protection
5. [x] dependencies/auth.py - Workspace IDOR
6. [x] app_factory.py - Security headers + CORS
7. [x] NEW: redis_rate_limiter.py - Distributed rate limiting
8. [x] FIX: .env.production - raptorflow.in domain

---

## COMPLETED

- [x] Phase 1 P0 - Critical fixes (AUTH_MODE, SECRET_KEY, tokens)
- [x] Phase 2 P1 - High priority fixes (IP spoofing, rate limiting, IDOR)
- [x] Phase 3 P2 - Medium priority (password policy, CORS, logs)
- [x] Phase 4 P3 - Low priority (headers)
- [x] RED TEAM ROUND 2 - All new vulnerabilities patched

## RED TEAM ROUND 2 - FIXED

- [x] P0: API Key Timing Attack (secrets.compare_digest)
- [x] P1: IP Spoofing (proper CIDR validation)
- [x] P1: /refresh rate limiting (10 req/min)
- [x] P1: Redis rate limiting (created redis_rate_limiter.py)
- [x] P2: CORS headers whitelist
- [x] P2: PII removed from logs
