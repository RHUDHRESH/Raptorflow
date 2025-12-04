# Environment Variables Analysis Report

## 🔍 Analysis Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## ✅ Variables Actually Used in Code

### Backend Variables (from `backend/src/config/env.ts`)
1. `NODE_ENV` - Application environment
2. `PORT` - Server port
3. `FRONTEND_PUBLIC_URL` - Frontend URL
4. `SUPABASE_URL` - Supabase project URL
5. `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key (backend only)
6. `GOOGLE_CLOUD_PROJECT_ID` - GCP project ID
7. `GOOGLE_CLOUD_LOCATION` - GCP region location
8. `UPSTASH_REDIS_REST_URL` - Redis REST URL
9. `UPSTASH_REDIS_REST_TOKEN` - Redis REST token
10. `PHONEPE_MERCHANT_ID` - PhonePe merchant ID (backend)
11. `PHONEPE_MERCHANT_KEY` - PhonePe merchant key (backend)
12. `PHONEPE_ENV` - PhonePe environment (backend)

### Frontend Variables (from actual code usage)
1. `VITE_SUPABASE_URL` - Supabase URL (frontend)
2. `VITE_SUPABASE_ANON_KEY` - Supabase anon key (frontend)
3. `VITE_PHONEPE_MERCHANT_ID` - PhonePe merchant ID (frontend)
4. `VITE_PHONEPE_SALT_KEY` - PhonePe salt key (frontend)
5. `VITE_PHONEPE_SALT_INDEX` - PhonePe salt index (frontend)
6. `VITE_PHONEPE_ENV` - PhonePe environment (frontend)

---

## ⚠️ ISSUES FOUND

### 1. **DUPLICATES / NAMING INCONSISTENCIES**

#### PhonePe Variables - Different Names for Same Purpose
- **Backend**: `PHONEPE_MERCHANT_KEY`
- **Frontend**: `VITE_PHONEPE_SALT_KEY`
- **Issue**: These appear to be the same thing (PhonePe salt key) but named differently
- **Recommendation**: Standardize naming or clarify if they're actually different

#### PhonePe Environment Variables - Duplicate
- **Backend**: `PHONEPE_ENV` (defaults to 'UAT')
- **Frontend**: `VITE_PHONEPE_ENV` (defaults to 'SANDBOX')
- **Issue**: Same variable exists in both backend and frontend with different defaults
- **Recommendation**: Use one source of truth (preferably backend) or ensure they match

#### Supabase URL - Duplicate
- **Backend**: `SUPABASE_URL`
- **Frontend**: `VITE_SUPABASE_URL`
- **Status**: ✅ This is CORRECT - backend needs non-prefixed, frontend needs VITE_ prefix

---

### 2. **UNFILLED / EMPTY VARIABLES**

All variables in `.env` file are currently empty (unfilled):
- All Supabase variables
- All Google Cloud variables
- All Redis/Upstash variables
- All PhonePe variables

**Action Required**: Fill in actual values for production use.

---

### 3. **UNNECESSARY VARIABLES (Documented but Not Used)**

These variables are mentioned in documentation but **NOT used in actual code**:

#### From Documentation (old_docs/docs/ENVIRONMENT_VARIABLES.md):
- ❌ `VITE_API_URL` - Not found in code
- ❌ `VITE_OPENAI_API_KEY` - Not found in code
- ❌ `VITE_GOOGLE_MAPS_API_KEY` - Not found in code
- ❌ `VITE_GOOGLE_CLOUD_PROJECT_ID` - Not used (backend uses non-VITE version)
- ❌ `VITE_GOOGLE_CLOUD_REGION` - Not used (backend uses GOOGLE_CLOUD_LOCATION)
- ❌ `VITE_PUBLIC_POSTHOG_KEY` - Not found in code
- ❌ `VITE_PUBLIC_POSTHOG_HOST` - Not found in code
- ❌ `VITE_INSTAGRAM_CLIENT_ID` - Not found in code
- ❌ `VITE_INSTAGRAM_CLIENT_SECRET` - Not found in code
- ❌ `VITE_LINKEDIN_CLIENT_ID` - Not found in code
- ❌ `VITE_LINKEDIN_CLIENT_SECRET` - Not found in code
- ❌ `VITE_TWITTER_API_KEY` - Not found in code
- ❌ `VITE_TWITTER_API_SECRET` - Not found in code
- ❌ `VITE_YOUTUBE_API_KEY` - Not found in code
- ❌ `VITE_STRIPE_PUBLISHABLE_KEY` - Not found in code
- ❌ `STRIPE_SECRET_KEY` - Not found in code
- ❌ `PHONEPE_SALT_KEY` - Not used (frontend uses VITE_PHONEPE_SALT_KEY)
- ❌ `PHONEPE_SALT_INDEX` - Not used (frontend uses VITE_PHONEPE_SALT_INDEX)
- ❌ `PHONEPE_ENABLED` - Not found in code

#### From Vercel Deployment Docs:
- ❌ `VITE_ENVIRONMENT` - Not found in code
- ❌ `VITE_BACKEND_API_URL` - Not found in code
- ❌ `VITE_POSTHOG_KEY` - Not found in code
- ❌ `VITE_POSTHOG_HOST` - Not found in code

---

## 📋 RECOMMENDATIONS

### 1. **Fix Naming Inconsistencies**
- Clarify if `PHONEPE_MERCHANT_KEY` (backend) and `VITE_PHONEPE_SALT_KEY` (frontend) are the same
- If same: Use consistent naming
- If different: Document the difference clearly

### 2. **Remove Unused Variables from Documentation**
- Update `old_docs/docs/ENVIRONMENT_VARIABLES.md` to only include variables actually used
- Remove references to unused services (Instagram, LinkedIn, Twitter, YouTube, Stripe, PostHog, etc.)

### 3. **Standardize PhonePe Environment Variable**
- Decide on single source of truth for `PHONEPE_ENV` / `VITE_PHONEPE_ENV`
- Ensure both backend and frontend use the same value

### 4. **Clean .env File**
The `.env` file should only contain variables that are:
- ✅ Actually used in code
- ✅ Not hardcoded with fallback values
- ✅ Required for the application to function

---

## ✅ CORRECT .env FILE STRUCTURE

Based on actual code usage, your `.env` should contain:

```env
# Application Configuration
NODE_ENV=development
PORT=3000
FRONTEND_PUBLIC_URL=http://localhost:5173

# Supabase (Backend)
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=

# Supabase (Frontend)
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=

# Google Cloud / Vertex AI
GOOGLE_CLOUD_PROJECT_ID=
GOOGLE_CLOUD_LOCATION=us-central1

# Redis / Upstash
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=

# PhonePe (Backend)
PHONEPE_MERCHANT_ID=
PHONEPE_MERCHANT_KEY=
PHONEPE_ENV=UAT

# PhonePe (Frontend)
VITE_PHONEPE_MERCHANT_ID=
VITE_PHONEPE_SALT_KEY=
VITE_PHONEPE_SALT_INDEX=1
VITE_PHONEPE_ENV=SANDBOX
```

---

## 🎯 SUMMARY

- **Total Variables Used**: 18
- **Duplicates Found**: 2 (PhonePe key naming, PhonePe env variable)
- **Unused Variables in Docs**: 20+
- **Unfilled Variables**: All (need to be filled with actual values)

