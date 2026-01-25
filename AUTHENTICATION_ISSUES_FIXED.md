# 🔧 Authentication Issues Fixed

## Summary

This document outlines the critical authentication bugs that were identified and fixed in the RaptorFlow codebase.

---

## 🐛 Issues Found and Fixed

### 1. **AuthContext useEffect Infinite Loop** (CRITICAL)
**File:** `src/contexts/AuthContext.tsx`

**Problem:** The `useEffect` that initializes auth had `user` in its dependency array. Since it also called `setUser()`, this created an infinite loop of auth initialization.

```typescript
// BEFORE (broken)
useEffect(() => {
  initializeAuth() // calls setUser()
  setInterval(() => { if (user) refreshUser() })
}, [user]) // <-- user changes → re-runs → user changes → ...
```

**Fix:** Split into two effects:
- Effect #1: Runs once on mount (`[]`) to initialize auth
- Effect #2: Periodic refresh depends on `session`, not `user`

---

### 2. **Session Age Calculation Bug** (CRITICAL)
**File:** `src/lib/auth-service.ts`

**Problem:** The session rotation logic was completely wrong:
```typescript
// BEFORE (broken)
const sessionAge = Date.now() - (session.expires_at ? new Date(session.expires_at).getTime() : Date.now())
// This calculated "time since session expired" not "session age"
// Also: expires_at is unix seconds, not ISO string
```

**Fix:** Proper expiry-based rotation:
```typescript
// AFTER (correct)
const expiresAtMs = typeof session.expires_at === 'number' 
  ? session.expires_at * 1000 
  : new Date(session.expires_at).getTime()
const timeUntilExpiry = expiresAtMs - Date.now()
if (timeUntilExpiry < 5 * 60 * 1000) {
  needsRotation = true
}
```

---

### 3. **ServiceRoleAuthService Module-Level Crash** (CRITICAL)
**File:** `src/lib/auth-service.ts`

**Problem:** `serviceAuth` was instantiated at module import time:
```typescript
// BEFORE (broken)
export const serviceAuth = ServiceRoleAuthService.getInstance()
// Crashes immediately if SUPABASE_SERVICE_ROLE_KEY is missing
// Can also leak into client bundles
```

**Fix:** Lazy initialization with server-only guard:
```typescript
// AFTER (safe)
export function getServiceAuth(): ServiceRoleAuthService {
  if (typeof window !== 'undefined') {
    throw new Error('ServiceRoleAuthService can only be used on the server')
  }
  if (!_serviceAuth) {
    _serviceAuth = ServiceRoleAuthService.getInstance()
  }
  return _serviceAuth
}
```

---

### 4. **Cross-Tab SignOut Race Conditions** (HIGH)
**File:** `src/lib/auth-service.ts`

**Problems:**
- Non-idempotent signout handler could redirect multiple times
- Listener leak due to `.bind(this)` creating new functions
- Both BroadcastChannel AND localStorage firing simultaneously

**Fixes:**
- Added `isSigningOut` flag to prevent duplicate handling
- Check if already on `/login` before redirecting
- Store bound handlers as class fields for proper cleanup
- Use only one communication mechanism (BC preferred, localStorage fallback)

---

### 5. **Duplicate Supabase Client Creation** (HIGH)
**File:** `src/lib/auth.ts`

**Problem:** Created its own Supabase client at module level instead of using the shared singleton.

**Fix:** Use the shared `createClient()` from `@/lib/supabase/client` with lazy initialization via Proxy.

---

### 6. **Inconsistent expires_at Handling** (MEDIUM)
**File:** `src/lib/auth.ts`

**Problem:** Two different interpretations in the same file:
- `getSession()` used `new Date(session.expires_at)` (wrong if seconds)
- `onAuthStateChange()` used `session.expires_at * 1000` (correct for seconds)

**Fix:** Unified handling that checks if value is number (seconds) or string (ISO):
```typescript
const expiresAtMs = session.expires_at 
  ? (typeof session.expires_at === 'number' ? session.expires_at * 1000 : new Date(session.expires_at).getTime())
  : undefined
```

---

### 7. **Type Mismatch in Onboarding Check** (MEDIUM)
**File:** `src/contexts/AuthContext.tsx`

**Problem:** Used `user?.onboardingStatus === 'active'` but `AuthUser` has `hasCompletedOnboarding: boolean`.

**Fix:** Support both for compatibility:
```typescript
const hasCompletedOnboarding = user?.hasCompletedOnboarding === true || user?.onboardingStatus === 'active'
```

---

## 🔧 Additional Fixes (Pass 2)

### 8. **"Invalid API key" Error** (CRITICAL)
**Files:** `src/app/api/plans/route.ts`, `src/app/api/onboarding/select-plan/route.ts`

**Problem:** The plans API and select-plan API were using the anon key client which was failing with "Invalid API key" errors due to RLS restrictions.

**Fix:** Changed to use service role client for database operations that need to bypass RLS during onboarding.

---

### 9. **Using getSession() Instead of getUser()** (SECURITY)
**Files:** `src/lib/auth-service.ts`, `src/app/api/onboarding/select-plan/route.ts`

**Problem:** Supabase warns that `getSession()` reads from cookies without validation, which can be spoofed. This is a security vulnerability.

**Fix:** Changed to use `getUser()` which contacts the Supabase Auth server to verify the token.

---

### 10. **Profile Creation Failing Silently** (CRITICAL)
**File:** `src/lib/auth-server.ts`

**Problem:** The `upsertProfileForAuthUser` function was failing silently without logging errors, making debugging impossible.

**Fix:** Added comprehensive error logging and fallback to `users` table if `profiles` and `user_profiles` fail.

---

### 11. **Missing RLS INSERT Policy for Profiles** (CRITICAL)
**File:** `supabase/migrations/20260126_fix_profiles_insert_policy.sql`

**Problem:** The `profiles` table only had SELECT and UPDATE policies. There was NO INSERT policy, so new users couldn't have profiles created.

**Fix:** Created new migration with:
- INSERT policy for profiles (`profiles_self_insert`)
- INSERT/UPDATE policies for subscriptions
- Public read policy for plans table
- INSERT policy for audit_logs

---

## 📋 Remaining Issues (Not Fixed in This Pass)

### Multiple Auth Implementations
The codebase has 3 competing auth files:
- `auth.ts` - Deprecated, kept for compatibility
- `supabase-auth.ts` - Claims to be "single source of truth" but isn't used consistently
- `auth-service.ts` - The actual primary implementation

**Recommendation:** Consolidate to `auth-service.ts` and delete/deprecate others.

### Type Inconsistencies
Different User types across files with different field names and casing:
- `subscriptionPlan` vs `subscription_plan`
- `workspaceId` vs `workspace_id`
- Different enum values for status fields

**Recommendation:** Define one canonical `AuthUser` type and use it everywhere.

### Missing Dependencies
TypeScript found many missing modules (pre-existing, not auth-related):
- `hugeicons-react`
- `motion/react`
- `@radix-ui/*` components
- `@types/jsonwebtoken`
- etc.

---

## ✅ Testing Recommendations

1. **Test login flow** - Ensure no redirect loops
2. **Test session persistence** - Page refresh should maintain session
3. **Test multi-tab behavior** - Signout in one tab should affect all tabs
4. **Test session rotation** - Sessions nearing expiry should refresh
5. **Test server-side auth** - API routes should properly validate sessions

---

## 📝 Files Modified

| File | Changes |
|------|---------|
| `src/contexts/AuthContext.tsx` | Fixed useEffect infinite loop, improved onboarding check |
| `src/lib/auth-service.ts` | Fixed session age calc, lazy serviceAuth, cross-tab races, use getUser() |
| `src/lib/auth.ts` | Deprecated, fixed client creation and expires_at handling |
| `src/lib/auth-server.ts` | Added error logging, fallback to users table, improved getServerUser() |
| `src/app/api/plans/route.ts` | Use service client to bypass RLS |
| `src/app/api/onboarding/select-plan/route.ts` | Use getUser(), service client for DB ops |
| `supabase/migrations/20260126_fix_profiles_insert_policy.sql` | NEW: RLS policies for profile/subscription INSERT |

---

## ⚠️ IMPORTANT: Run Migration

You MUST apply the new migration to fix the RLS policies:

```bash
# If using Supabase CLI
supabase db push

# Or run directly in Supabase SQL editor:
# Copy contents of supabase/migrations/20260126_fix_profiles_insert_policy.sql
```
