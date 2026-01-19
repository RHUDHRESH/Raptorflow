# 🔐 RAPTORFLOW AUTHENTICATION OVERHAUL MASTERPLAN

## Executive Summary

This document provides a **complete audit** of Raptorflow's authentication system and a **step-by-step implementation plan** to fix all authentication issues once and for all.

---

# PART 1: CRITICAL AUDIT FINDINGS

## 🚨 CRITICAL ISSUES (Must Fix Immediately)

### 1. AUTH BYPASS MODE - SECURITY VULNERABILITY
**Location:** `src/lib/auth.ts` and `frontend/src/lib/auth.ts`
**Severity:** CRITICAL

```typescript
// Current code - COMPLETELY INSECURE
// Check if user is authenticated - ALWAYS TRUE (BYPASS MODE)
export function isAuthenticated(): boolean {
  // ... always returns true and creates mock users
}
```

**Impact:** Anyone can access protected routes without authentication. Mock users are created automatically with `soar` plan access.

### 2. DUPLICATE FRONTEND CODEBASES
**Issue:** Two separate frontend directories exist:
- `src/` - Main Next.js app
- `frontend/src/` - Secondary Next.js app

**Impact:** Confusing, inconsistent behavior, double maintenance.

### 3. RLS POLICY MISMATCH
**Location:** `supabase/migrations/20240101_users_rls.sql`
```sql
-- INCORRECT: Using auth.uid() = id
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);
```

**Problem:** The `users.id` is the Supabase auth user ID, but some code uses `auth_user_id` column. This creates inconsistency.

### 4. PRICING MISMATCH
**Database has:**
- Ascent: ₹2,900/mo
- Glide: ₹7,900/mo  
- Soar: ₹19,900/mo

**User requires:**
- Ascent: ₹5,000/mo
- Glide: ₹7,000/mo
- Soar: ₹10,000/mo

### 5. EMAIL NOT WORKING
**Issue:** Using Resend API with unverified domain, falling back to console logs in development.

---

## 📋 CURRENT STATE MATRIX

| Component | Status | Working? | Notes |
|-----------|--------|----------|-------|
| Email/Password Login | Exists | ⚠️ Partial | Bypassed in auth.ts |
| Google OAuth | Exists | ⚠️ Partial | Configured but may not work |
| Magic Links | Not Implemented | ❌ No | - |
| MFA/TOTP | Database Only | ❌ No | Tables exist, no frontend |
| Forgot Password | Exists | ⚠️ Partial | Custom impl, not Supabase native |
| Email Verification | Exists | ⚠️ Partial | Resend API issues |
| RLS Policies | Exists | ⚠️ Buggy | Inconsistent user ID references |
| Workspaces | Exists | ⚠️ Partial | Auto-created but not fully integrated |
| Pricing Tiers | Exists | ❌ Wrong | Wrong prices |
| PhonePe Payment | Extensive | ✅ Yes | Well implemented |
| Rate Limiting | Middleware | ✅ Yes | In middleware.ts |

---

# PART 2: COMPLETE AUTHENTICATION ARCHITECTURE

## 🏗️ Target Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     RAPTORFLOW AUTH SYSTEM                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Frontend   │  │   Supabase   │  │   Backend    │          │
│  │   Next.js    │──│     Auth     │──│   FastAPI    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                 │                   │
│         ▼                 ▼                 ▼                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    AUTH METHODS                          │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐│   │
│  │  │Email/  │ │ Google │ │ Magic  │ │  MFA   │ │Password│ │   │
│  │  │Password│ │  OAuth │ │ Links  │ │ (TOTP) │ │  less  │ │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘│   │
│  └─────────────────────────────────────────────────────────┘   │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  DATA ISOLATION (RLS)                    │   │
│  │  User → Workspace → All Data (ICPs, Campaigns, etc.)    │   │
│  └─────────────────────────────────────────────────────────┘   │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │               SUBSCRIPTION & PAYMENTS                    │   │
│  │  Ascent (₹5k) → Glide (₹7k) → Soar (₹10k)              │   │
│  │                    via PhonePe                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

# PART 3: PRICING TIERS SPECIFICATION

## 💰 Subscription Plans

### ASCENT - ₹5,000/month (₹50,000/year - 2 months free)
**Target:** Founders just getting started

| Feature | Limit |
|---------|-------|
| Moves per week | 3 |
| Active Campaigns | 3 |
| ICPs (Cohorts) | 3 |
| Team Seats | 1 (Solo) |
| Muse AI | Basic |
| Matrix Analytics | Basic |
| Storage | 5 GB |
| API Access | ❌ No |
| Priority Support | ❌ No |

**Rate Limits:**
- API calls: 100/hour
- AI generations: 10/day
- File uploads: 50 MB/file

---

### GLIDE - ₹7,000/month (₹70,000/year - 2 months free)
**Target:** Founders scaling their marketing

| Feature | Limit |
|---------|-------|
| Moves per week | Unlimited |
| Active Campaigns | Unlimited |
| ICPs (Cohorts) | 10 |
| Team Seats | 5 |
| Muse AI | Advanced (Voice Training) |
| Matrix Analytics | Full |
| Blackbox Vault | ✅ Yes |
| Storage | 25 GB |
| API Access | ❌ No |
| Priority Support | ✅ Yes |

**Rate Limits:**
- API calls: 500/hour
- AI generations: 50/day
- File uploads: 200 MB/file

---

### SOAR - ₹10,000/month (₹100,000/year - 2 months free)
**Target:** Teams running multi-channel campaigns

| Feature | Limit |
|---------|-------|
| Moves per week | Unlimited |
| Active Campaigns | Unlimited |
| ICPs (Cohorts) | Unlimited |
| Team Seats | Unlimited |
| Muse AI | Custom Training |
| Matrix Analytics | Full + Export |
| Blackbox Vault | ✅ Yes |
| White-label Exports | ✅ Yes |
| Storage | 100 GB |
| API Access | ✅ Yes |
| Dedicated Success Manager | ✅ Yes |
| Custom Integrations | ✅ Yes |

**Rate Limits:**
- API calls: 2000/hour
- AI generations: Unlimited
- File uploads: 500 MB/file

---

# PART 4: AUTHENTICATION METHODS SPECIFICATION

## 1. Email/Password Authentication

### Sign Up Flow
```
User enters email + password + name
         ↓
Frontend validates (min 8 chars, 1 uppercase, 1 number)
         ↓
Supabase auth.signUp() called
         ↓
User record created in auth.users
         ↓
Trigger creates public.users record
         ↓
Trigger creates workspace
         ↓
Verification email sent
         ↓
User clicks link → email confirmed
         ↓
Redirect to /onboarding
```

### Sign In Flow
```
User enters email + password
         ↓
Supabase auth.signInWithPassword()
         ↓
Check if MFA required (AAL2)
         ↓
If MFA: Show MFA challenge
         ↓
Session created with JWT
         ↓
Check subscription status
         ↓
If no subscription: → /pricing
If subscription + no onboarding: → /onboarding
If subscription + onboarding done: → /dashboard
```

### Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character (!@#$%^&*)
- Not in common password list

---

## 2. Google OAuth (Single Sign-On)

### Configuration Required
```
Supabase Dashboard → Authentication → Providers → Google
- Client ID: from Google Cloud Console
- Client Secret: from Google Cloud Console
- Redirect URL: https://your-domain.com/auth/callback
```

### Flow
```
User clicks "Continue with Google"
         ↓
Redirect to Google OAuth consent
         ↓
User authorizes
         ↓
Google redirects to /auth/callback
         ↓
Supabase exchanges code for tokens
         ↓
User created/updated in auth.users
         ↓
Same post-login flow as email/password
```

---

## 3. Magic Links (Passwordless)

### Flow
```
User enters email
         ↓
Supabase auth.signInWithOtp({ email })
         ↓
Magic link email sent
         ↓
User clicks link
         ↓
Redirect to /auth/confirm?token_hash=xxx&type=magiclink
         ↓
Supabase verifies token
         ↓
Session created
         ↓
Redirect to dashboard
```

### Email Template
```html
<h2>Your RaptorFlow Login Link</h2>
<p>Click below to sign in to your account:</p>
<a href="{{ .SiteURL }}/auth/confirm?token_hash={{ .TokenHash }}&type=magiclink">
  Sign In to RaptorFlow
</a>
<p>This link expires in 1 hour.</p>
```

---

## 4. Multi-Factor Authentication (MFA)

### Supported Methods
1. **TOTP (Authenticator Apps)** - Google Authenticator, Authy, 1Password
2. **SMS** - OTP via SMS (requires Twilio)
3. **Email** - OTP via Email
4. **Backup Codes** - 10 one-time use codes

### Enrollment Flow
```
User goes to Settings → Security → Enable MFA
         ↓
Choose method (TOTP recommended)
         ↓
Display QR code for authenticator app
         ↓
User scans and enters verification code
         ↓
Generate 10 backup codes
         ↓
User confirms they saved backup codes
         ↓
MFA enabled for account
```

### Authentication Flow with MFA
```
User completes primary auth (email/password or OAuth)
         ↓
Check if MFA enabled for user
         ↓
If enabled: Set session to AAL1 (not fully authenticated)
         ↓
Show MFA challenge screen
         ↓
User enters TOTP code or backup code
         ↓
Verify code against stored secret
         ↓
Upgrade session to AAL2 (fully authenticated)
         ↓
Continue to dashboard
```

---

## 5. Forgot Password / Reset Password

### Flow
```
User clicks "Forgot Password"
         ↓
Enter email address
         ↓
Supabase auth.resetPasswordForEmail(email, {
  redirectTo: 'https://domain.com/auth/reset-password'
})
         ↓
Reset email sent
         ↓
User clicks link → /auth/reset-password?code=xxx
         ↓
Exchange code for session
         ↓
Show new password form
         ↓
Supabase auth.updateUser({ password: newPassword })
         ↓
Redirect to login with success message
```

---

# PART 5: WORKSPACE & MULTI-TENANCY

## Data Model

```
auth.users (Supabase managed)
    │
    ▼
public.users
    │ 1:1
    ▼
public.workspaces
    │ 1:N
    ├── public.icp_profiles
    ├── public.campaigns
    ├── public.moves
    ├── public.muse_assets
    ├── public.blackbox_strategies
    ├── public.daily_wins
    └── ... all other user data
```

## Workspace Creation
- Automatically created when user signs up
- Named: `{username}'s Workspace`
- Slug: `ws-{8-char-uuid}`

## RLS Pattern (Correct Implementation)
```sql
-- All tables should follow this pattern
CREATE POLICY "workspace_isolation" ON table_name
    FOR ALL USING (
        workspace_id IN (
            SELECT id FROM workspaces 
            WHERE user_id = auth.uid()
        )
    );
```

---

# PART 6: ROW LEVEL SECURITY (RLS) COMPLETE POLICIES

## Core Principle
Every table with user data must:
1. Have RLS enabled
2. Have policies that isolate data by workspace_id
3. Use `auth.uid()` to get current user

## Master RLS Migration

```sql
-- CORRECTED RLS POLICIES FOR ALL TABLES

-- 1. Users table
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
CREATE POLICY "users_select_own" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "users_update_own" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- 2. Workspaces table
DROP POLICY IF EXISTS "workspace_select" ON public.workspaces;
CREATE POLICY "workspaces_select_own" ON public.workspaces
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "workspaces_update_own" ON public.workspaces
    FOR UPDATE USING (user_id = auth.uid());

-- 3. Generic workspace-scoped table policy template
-- Apply to: icp_profiles, campaigns, moves, etc.
CREATE OR REPLACE FUNCTION get_user_workspace_ids()
RETURNS SETOF UUID AS $$
    SELECT id FROM workspaces WHERE user_id = auth.uid();
$$ LANGUAGE SQL SECURITY DEFINER STABLE;

-- Example for icp_profiles
CREATE POLICY "icp_workspace_isolation" ON public.icp_profiles
    FOR ALL USING (
        workspace_id IN (SELECT get_user_workspace_ids())
    );
```

---

# PART 7: PHONOPE PAYMENT INTEGRATION

## Current Status: ✅ WELL IMPLEMENTED

The PhonePe integration is the most complete part of the system.

## Payment Flow for Subscriptions

```
User selects plan (Ascent/Glide/Soar)
         ↓
Frontend calls /api/payments/initiate
         ↓
Backend creates PhonePe order
         ↓
User redirected to PhonePe payment page
         ↓
User completes payment
         ↓
PhonePe webhook: /api/payments/webhook
         ↓
Verify signature & update subscription
         ↓
Create user_subscriptions record
         ↓
Initialize plan_usage_limits
         ↓
Redirect to /onboarding
```

## Required Fixes
1. Update prices in subscription_plans table
2. Connect subscription to user journey
3. Ensure webhook properly activates subscription

---

# PART 8: IMPLEMENTATION ROADMAP

## Phase 1: Critical Fixes (Day 1-2)

### Step 1.1: Remove Auth Bypass
**Files to modify:**
- `src/lib/auth.ts`
- `frontend/src/lib/auth.ts`

**Action:** Delete bypass code, use real Supabase auth

### Step 1.2: Consolidate Frontend
**Decision needed:** Keep `frontend/` or `src/`?
**Recommendation:** Keep `frontend/` (more complete)

### Step 1.3: Fix RLS Policies
Run corrected RLS migration

### Step 1.4: Update Pricing
```sql
UPDATE subscription_plans SET 
    price_monthly = 500000,  -- ₹5000 in paise
    price_annual = 5000000   -- ₹50000 in paise
WHERE slug = 'ascent';

UPDATE subscription_plans SET 
    price_monthly = 700000,  -- ₹7000 in paise
    price_annual = 7000000   -- ₹70000 in paise
WHERE slug = 'glide';

UPDATE subscription_plans SET 
    price_monthly = 1000000, -- ₹10000 in paise
    price_annual = 10000000  -- ₹100000 in paise
WHERE slug = 'soar';
```

---

## Phase 2: Email Setup (Day 2-3)

### Step 2.1: Configure Supabase SMTP
**Option A: Use Resend (Recommended)**
1. Verify domain in Resend
2. Configure Supabase to use Resend SMTP:
   - SMTP Host: smtp.resend.com
   - SMTP Port: 465
   - SMTP User: resend
   - SMTP Password: your-resend-api-key

**Option B: Use Supabase Built-in**
- Limited to 4 emails/hour on free tier
- Good for testing only

### Step 2.2: Configure Email Templates
In Supabase Dashboard → Authentication → Email Templates:
- Confirmation email
- Magic link email
- Password reset email
- Email change confirmation

---

## Phase 3: Auth Implementation (Day 3-5)

### Step 3.1: Create Unified Auth Library
Create `src/lib/supabase-auth.ts`:
```typescript
// Proper auth implementation using Supabase
import { createBrowserClient } from '@supabase/ssr'

export const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

// Sign up with email/password
export async function signUp(email: string, password: string, fullName: string) {
  return supabase.auth.signUp({
    email,
    password,
    options: {
      data: { full_name: fullName },
      emailRedirectTo: `${window.location.origin}/auth/callback`
    }
  })
}

// Sign in with email/password
export async function signIn(email: string, password: string) {
  return supabase.auth.signInWithPassword({ email, password })
}

// Sign in with Google
export async function signInWithGoogle() {
  return supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: `${window.location.origin}/auth/callback`
    }
  })
}

// Sign in with magic link
export async function signInWithMagicLink(email: string) {
  return supabase.auth.signInWithOtp({
    email,
    options: {
      emailRedirectTo: `${window.location.origin}/auth/callback`
    }
  })
}

// Reset password
export async function resetPassword(email: string) {
  return supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${window.location.origin}/auth/reset-password`
  })
}

// Update password
export async function updatePassword(newPassword: string) {
  return supabase.auth.updateUser({ password: newPassword })
}

// Sign out
export async function signOut() {
  return supabase.auth.signOut()
}

// Get current session
export async function getSession() {
  return supabase.auth.getSession()
}

// Get current user
export async function getUser() {
  const { data: { session } } = await supabase.auth.getSession()
  return session?.user ?? null
}
```

### Step 3.2: Create Auth Callback Route
`src/app/auth/callback/route.ts`:
```typescript
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/dashboard'

  if (code) {
    const cookieStore = cookies()
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() { return cookieStore.getAll() },
          setAll(cookiesToSet) {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          },
        },
      }
    )

    const { error } = await supabase.auth.exchangeCodeForSession(code)
    
    if (!error) {
      // Check subscription status
      const { data: { user } } = await supabase.auth.getUser()
      const { data: subscription } = await supabase
        .from('user_subscriptions')
        .select('*, subscription_plans(*)')
        .eq('user_id', user?.id)
        .eq('status', 'active')
        .single()

      if (!subscription) {
        return NextResponse.redirect(new URL('/pricing', request.url))
      }

      // Check onboarding status
      const { data: onboarding } = await supabase
        .from('user_onboarding')
        .select('is_completed')
        .eq('user_id', user?.id)
        .single()

      if (!onboarding?.is_completed) {
        return NextResponse.redirect(new URL('/onboarding', request.url))
      }

      return NextResponse.redirect(new URL(next, request.url))
    }
  }

  return NextResponse.redirect(new URL('/auth/auth-error', request.url))
}
```

---

## Phase 4: MFA Implementation (Day 5-7)

### Step 4.1: Enable Supabase MFA
In Supabase Dashboard → Authentication → Configuration:
- Enable "Multi-factor Authentication (MFA)"
- Set to "Optional" initially (users can enable)

### Step 4.2: Create MFA Setup Component
### Step 4.3: Create MFA Challenge Component
### Step 4.4: Update Login Flow for MFA

---

## Phase 5: Testing & Red-Teaming (Day 7-10)

### Red-Team Checklist

#### Authentication Tests
- [ ] Can access /dashboard without login? → Should redirect to /login
- [ ] Can access other user's data? → Should return empty/403
- [ ] SQL injection in login form? → Should be sanitized
- [ ] XSS in user input fields? → Should be escaped
- [ ] CSRF protection on forms? → Should have tokens
- [ ] Session hijacking possible? → Should use httpOnly cookies
- [ ] Rate limiting working? → Should block after X attempts

#### RLS Tests
```sql
-- Test: User A cannot see User B's data
SET request.jwt.claim.sub = 'user-a-uuid';
SELECT * FROM icp_profiles; -- Should only show User A's profiles

SET request.jwt.claim.sub = 'user-b-uuid';
SELECT * FROM icp_profiles; -- Should only show User B's profiles
```

#### Payment Tests
- [ ] Can bypass payment to get premium features?
- [ ] Can manipulate subscription status?
- [ ] Webhook signature verification working?
- [ ] Rate limits enforced per tier?

---

# PART 9: VERIFICATION CHECKLIST

## How to Know Auth is Working

### 1. Email/Password
```bash
# Test signup
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","fullName":"Test User"}'

# Expected: 200 OK, user created, verification email sent
```

### 2. Login
```bash
# Test login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Expected: 200 OK, session token returned
```

### 3. Protected Routes
```bash
# Test without token
curl http://localhost:3000/api/protected/user

# Expected: 401 Unauthorized

# Test with token
curl http://localhost:3000/api/protected/user \
  -H "Authorization: Bearer <token>"

# Expected: 200 OK, user data
```

### 4. RLS Verification
```sql
-- In Supabase SQL Editor
-- Login as test user, then run:
SELECT * FROM icp_profiles;

-- Should ONLY return rows where workspace_id belongs to current user
```

### 5. Rate Limiting
```bash
# Hit login endpoint 11 times rapidly
for i in {1..11}; do
  curl -X POST http://localhost:3000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}'
done

# Expected: First 10 return 401 (wrong password)
# 11th should return 429 (Too Many Requests)
```

---

# PART 10: ENVIRONMENT VARIABLES CHECKLIST

## Required Environment Variables

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-jwt-secret

# Application
NEXT_PUBLIC_APP_URL=https://your-domain.com
NEXT_PUBLIC_API_URL=https://api.your-domain.com

# Email (Resend)
RESEND_API_KEY=re_xxxxx
RESEND_FROM_EMAIL=noreply@your-domain.com
RESEND_VERIFIED_EMAIL=your-verified@email.com

# PhonePe
PHONEPE_CLIENT_ID=your-client-id
PHONEPE_CLIENT_SECRET=your-client-secret
PHONEPE_MERCHANT_ID=MERCHANTXXXXX
PHONEPE_ENV=UAT  # or PRODUCTION

# Google OAuth
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxx
```

---

# PART 11: QUICK REFERENCE COMMANDS

## Database Commands

```sql
-- Check if RLS is enabled on all tables
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';

-- List all RLS policies
SELECT * FROM pg_policies WHERE schemaname = 'public';

-- Test user's accessible workspaces
SELECT * FROM workspaces WHERE user_id = auth.uid();

-- Check subscription status for a user
SELECT 
    u.email,
    sp.name as plan,
    us.status,
    us.expires_at
FROM users u
LEFT JOIN user_subscriptions us ON u.id = us.user_id
LEFT JOIN subscription_plans sp ON us.plan_id = sp.id
WHERE u.email = 'test@example.com';
```

## Supabase CLI Commands

```bash
# Push migrations
supabase db push

# Reset database (WARNING: destructive)
supabase db reset

# Generate types
supabase gen types typescript --local > types/supabase.ts

# Check status
supabase status
```

---

# APPENDIX A: COMPLETE FILE CHANGES REQUIRED

## Files to DELETE (Auth Bypass)
- `src/lib/auth.ts` (replace with proper implementation)
- `frontend/src/lib/simple-auth.ts`

## Files to MODIFY
1. `src/lib/auth-client.ts` - Add magic link, update error handling
2. `src/contexts/AuthContext.tsx` - Add MFA state, subscription state
3. `src/middleware.ts` - Simplify, rely on Supabase session
4. `frontend/src/app/login/page.tsx` - Add magic link option
5. `frontend/src/app/forgot-password/page.tsx` - Use Supabase native

## Files to CREATE
1. `src/lib/supabase-auth.ts` - Unified auth library
2. `src/app/auth/callback/route.ts` - OAuth callback handler
3. `src/app/auth/confirm/route.ts` - Email confirmation handler
4. `src/app/auth/reset-password/page.tsx` - Password reset page
5. `src/components/auth/MFASetup.tsx` - MFA enrollment
6. `src/components/auth/MFAChallenge.tsx` - MFA verification

## Migrations to RUN
1. Fix RLS policies
2. Update pricing
3. Add missing indexes

---

**Document Version:** 1.0
**Created:** January 16, 2026
**Author:** Cascade AI Assistant

This document should be treated as the **single source of truth** for Raptorflow authentication implementation.
