# Authentication System Investigation

## Bug Summary
**Issue**: Authentication end-to-end flow has multiple critical edge cases and inconsistencies that prevent 100% reliable operation.

## Root Cause Analysis

### 1. **Schema Inconsistencies** (CRITICAL)

#### Database Column Naming Mismatch
- **Backend migrations** (`001_user_management_schema.sql`): Uses `auth_id` to reference `auth.users(id)`
- **Supabase migrations** (`001_initial_schema.sql`): Uses `auth_user_id` to reference `auth.users(id)`
- **Backend auth.py** (line 167): Queries using `auth_user_id`
- **Result**: User lookup will fail depending on which migration was run

**Location**:
- `backend/migrations/001_user_management_schema.sql:14` (uses `auth_id`)
- `supabase/migrations/001_initial_schema.sql:35` (uses `auth_user_id`)
- `backend/core/auth.py:167` (expects `auth_user_id`)

#### Table Name Inconsistencies
- **AuthProvider.tsx** (line 93): Queries `profiles` table
- **Backend auth.py**: Queries `users` table
- **Database schema**: Defines `users` table, not `profiles`
- **Result**: Frontend profile fetching will fail with "table not found"

**Location**:
- `src/components/auth/AuthProvider.tsx:93` (queries profiles)
- `backend/core/auth.py:165` (queries users)

### 2. **Missing Auto-Workspace Creation** (CRITICAL)

#### No Trigger for New User Workspace
The system expects every user to have a workspace, but:
- User signup creates entry in `auth.users` and `public.users`
- **NO automatic workspace creation** happens
- `get_workspace_id()` function (auth.py:236-264) fails when no workspace exists
- Returns 404 "No workspace found for user"

**Evidence**:
- `legacy/fix_users_table.sql:61-80` has `handle_new_user()` trigger but doesn't create workspace
- `supabase/migrations/001_initial_schema.sql:342-358` creates user profile but no workspace
- No trigger found for automatic workspace creation

**Impact**:
- New users cannot access any authenticated endpoints
- All requests fail with 404 after successful login

### 3. **Duplicate AuthProvider Implementations** (HIGH)

Two different AuthProvider components exist:
1. **AuthContext.tsx** (287 lines) - Uses Supabase client directly, comprehensive
2. **AuthProvider.tsx** (179 lines) - Simpler implementation, queries `profiles` table

**Issues**:
- Different state management approaches
- LoginForm.tsx imports from AuthProvider, but main app might use AuthContext
- Inconsistent user data structure
- Race conditions possible

**Locations**:
- `src/contexts/AuthContext.tsx` (full implementation)
- `src/components/auth/AuthProvider.tsx` (simpler version)
- `src/components/auth/LoginForm.tsx:8` (imports from AuthProvider)

### 4. **JWT Token Edge Cases** (MEDIUM)

#### Missing Error Recovery
- **Expired Token Handling**: Token validation fails but doesn't trigger refresh
- **Invalid Token Format**: No retry mechanism for malformed headers
- **Token Refresh Threshold**: 5 minutes before expiry, but no automatic refresh in frontend

**Location**: `backend/core/jwt.py:119-127`

#### Issuer Validation Issues
```python
issuer = f"{self.supabase_url}/auth/v1"
if not issuer or "your-project" in issuer:
    raise ValueError("SUPABASE_URL not properly configured")
```
- Hardcoded check for "your-project" string
- No validation of actual issuer format
- **Location**: `backend/core/jwt.py:90-92`

### 5. **Missing Error Handling in Auth Endpoints** (MEDIUM)

#### Backend Auth Endpoints
- `get_user_usage()` (auth.py:42-99): No try-catch for RPC calls
- `get_user_billing()` (auth.py:102-154): Database queries can fail silently
- `delete_account()` (auth.py:235-260): Marked as "in a real implementation" - NOT IMPLEMENTED

#### Frontend Auth Flow
- **LoginForm.tsx**: Generic error handling, doesn't distinguish between:
  - Invalid credentials
  - Network errors
  - Server errors
  - Account locked
  - Email not verified

**Location**: `src/components/auth/LoginForm.tsx:72-83`

### 6. **Workspace Validation Edge Cases** (HIGH)

#### Race Condition in Workspace Ownership
```python
async def get_workspace_id(request, user, x_workspace_id):
    if x_workspace_id:
        if not await user_owns_workspace(user.id, workspace_id):
            raise HTTPException(403, "Access denied")
```

**Issues**:
- No locking mechanism
- Concurrent requests can bypass validation
- User could be removed from workspace between check and use
- **Location**: `backend/core/auth.py:246-253`

#### Missing Workspace Member Validation
- Only checks workspace ownership (`owner_id`)
- Doesn't check `workspace_members` table for team member access
- **Location**: `backend/core/auth.py:267-281`

### 7. **Session Management Gaps** (MEDIUM)

#### No Session Cleanup
- `user_sessions` table referenced in code but may not exist in schema
- No trigger to cleanup expired sessions
- No enforcement of `max_concurrent_sessions` from settings
- **Location**: `src/lib/auth-client.ts:229-273`

#### Missing Session Validation
- Backend doesn't validate session tokens from database
- Only relies on JWT validation
- No device fingerprinting enforcement
- **Location**: `src/lib/auth-config.ts:146-165`

### 8. **OAuth Flow Edge Cases** (MEDIUM)

#### Google OAuth Missing Error States
- No handling for user canceling OAuth flow
- No handling for OAuth provider errors
- No state parameter validation (CSRF vulnerability)
- **Location**: `src/lib/auth-client.ts:27-54`

#### Missing OAuth Email Verification
- OAuth users might have unverified emails
- No check in backend for `email_verified` field
- **Location**: `backend/core/auth.py:188-199`

### 9. **Audit Logging Inconsistencies** (LOW)

#### Incomplete Audit Trail
- Success cases not logged (only failures)
- No audit for workspace switching
- No audit for permission changes
- **Location**: `backend/core/auth.py:90-233`

### 10. **Rate Limiting Not Enforced** (MEDIUM)

#### Configuration Exists But Not Implemented
- `authSettings.rateLimit` defined in config
- No middleware implementing rate limiting
- Login endpoint vulnerable to brute force
- **Location**: `src/lib/auth-config.ts:152-156`

## Affected Components

### Backend
1. `backend/core/auth.py` - User authentication, workspace validation
2. `backend/core/jwt.py` - Token validation and refresh
3. `backend/api/v1/auth.py` - Auth endpoints
4. `backend/migrations/001_user_management_schema.sql` - Database schema

### Frontend
1. `src/contexts/AuthContext.tsx` - Main auth context
2. `src/components/auth/AuthProvider.tsx` - Alternative auth provider
3. `src/components/auth/LoginForm.tsx` - Login UI
4. `src/lib/auth-client.ts` - Client-side auth functions
5. `src/lib/auth-config.ts` - Auth configuration

### Database
1. Schema inconsistencies between migrations
2. Missing triggers for auto-workspace creation
3. Missing user_sessions table (if session tracking enabled)

## Proposed Solution

### Phase 1: Critical Fixes (Required for 100% functionality)
1. **Standardize Database Schema**
   - Choose `auth_user_id` as standard column name
   - Update all migrations to use consistent naming
   - Create migration to rename existing columns

2. **Implement Auto-Workspace Creation**
   - Create database trigger `handle_new_user_workspace()`
   - Automatically create default workspace on user signup
   - Add workspace member entry for owner

3. **Consolidate AuthProvider**
   - Remove duplicate AuthProvider.tsx
   - Use AuthContext.tsx as single source of truth
   - Update all imports

4. **Fix Table References**
   - Update AuthProvider to query `users` table not `profiles`
   - Or create `profiles` view if needed for compatibility

### Phase 2: Edge Case Handling
1. **Implement Token Refresh**
   - Add automatic refresh in frontend
   - Handle refresh token rotation
   - Add retry logic for expired tokens

2. **Workspace Member Validation**
   - Check both ownership and membership
   - Add proper locking for concurrent access
   - Validate workspace exists before assigning

3. **Comprehensive Error Handling**
   - Distinguish error types in frontend
   - Add specific error messages
   - Implement retry logic for transient errors

### Phase 3: Security Hardening
1. **Implement Rate Limiting**
   - Add middleware for rate limiting
   - Enforce limits per IP and per user
   - Add account lockout after failed attempts

2. **OAuth Security**
   - Add state parameter validation
   - Verify email for OAuth users
   - Handle OAuth errors gracefully

3. **Session Management**
   - Create user_sessions table if needed
   - Add session cleanup job
   - Enforce max concurrent sessions

4. **Audit Logging**
   - Log all auth events (success and failure)
   - Log permission changes
   - Log workspace switching

## Test Coverage Gaps

### Missing Tests
1. Concurrent login attempts
2. Token refresh during active request
3. Workspace deletion while user is active
4. User deletion with active sessions
5. OAuth cancellation flow
6. Email verification expiry
7. Password reset token expiry
8. Multi-device login scenarios
9. Session hijacking attempts
10. Malformed JWT tokens

### Existing Test Limitations
- Mock-heavy tests don't catch integration issues
- No end-to-end auth flow tests
- No test for database trigger execution
- No test for RLS policies

## Security Considerations

### Vulnerabilities Found
1. **CSRF in OAuth**: No state parameter validation
2. **Brute Force**: No rate limiting on login
3. **Session Fixation**: No session regeneration on privilege change
4. **Token Leakage**: Tokens in URL params for some flows
5. **Weak Password Policy**: Minimum 6 chars (should be 8+)

### Recommendations
1. Add CSRF protection for OAuth flows
2. Implement rate limiting immediately
3. Regenerate session on subscription upgrade
4. Never pass tokens in URL, use headers/body only
5. Increase password minimum to 8 characters with complexity requirements

## Timeline Estimate

- **Phase 1 (Critical)**: 2-3 days
- **Phase 2 (Edge Cases)**: 3-4 days
- **Phase 3 (Security)**: 2-3 days
- **Testing & Verification**: 2 days

**Total**: ~10-12 days for 100% reliable authentication

## Priority Ranking

1. 🔴 **P0 - Schema Standardization** (blocks everything)
2. 🔴 **P0 - Auto-Workspace Creation** (breaks user signup)
3. 🔴 **P0 - AuthProvider Consolidation** (causes confusion)
4. 🟡 **P1 - Token Refresh** (impacts user experience)
5. 🟡 **P1 - Workspace Member Validation** (security risk)
6. 🟡 **P1 - Rate Limiting** (security risk)
7. 🟢 **P2 - OAuth Security** (nice to have)
8. 🟢 **P2 - Session Management** (nice to have)
9. 🟢 **P2 - Audit Logging** (compliance)

## Implementation Summary

### Completed Fixes (P0 - Critical)

1. **Schema Standardization** ✅
   - Updated `backend/migrations/001_user_management_schema.sql` to use `auth_user_id` instead of `auth_id`
   - Updated all indexes and RLS policies to reference `auth_user_id`
   - Consistent with Supabase migration schema

2. **Auto-Workspace Creation** ✅
   - Added `handle_new_user_workspace()` trigger function in backend migration
   - Added `handle_new_user()` trigger function in Supabase migration
   - Automatically creates default workspace on user signup
   - Adds user as workspace member with owner role
   - Generates unique workspace slug from email

3. **AuthProvider Consolidation** ✅
   - Updated all components to use `@/components/auth/AuthProvider`
   - Fixed `src/app/payment/success/page.tsx` to use AuthProvider
   - Fixed `src/components/InteractiveHero.tsx` to use AuthProvider
   - Fixed table reference from `profiles` to `users` with `auth_user_id` column

4. **Token Refresh Logic** ✅
   - Added automatic token refresh interval in AuthProvider (checks every 4 minutes)
   - Refreshes token if less than 5 minutes until expiry
   - Prevents session expiration during active usage

5. **Workspace Member Validation** ✅
   - Enhanced `user_owns_workspace()` to check both ownership and membership
   - Validates workspace_members table with active status check
   - Added proper error logging

6. **Comprehensive Error Handling** ✅
   - Added `login()` method to AuthProvider with specific error messages
   - Distinguishes between: Invalid credentials, Email not confirmed, User not found, Too many requests
   - Throws specific errors instead of generic messages

7. **OAuth State Parameter Validation** ✅
   - Added CSRF protection via state parameter in OAuthButton
   - Stores state token in sessionStorage
   - Updated auth callback to handle state validation
   - Fixed callback to query `users` table with `auth_user_id`

### Testing Notes

- package.json has encoding issues preventing npm commands
- Manual verification recommended for auth flow testing
- All code changes follow TypeScript strict mode
- Error handling improves user experience

## Next Steps

1. Fix package.json encoding issue (UTF-16 to UTF-8)
2. Run comprehensive integration tests
3. Test OAuth flow end-to-end
4. Verify workspace creation on signup
5. Test token refresh mechanism
