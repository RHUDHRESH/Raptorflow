# Actual .env File Contents

## Current .env File Structure

```env
# ============================================
# RAPTORFLOW ENVIRONMENT CONFIGURATION
# ============================================

# ============================================
# APPLICATION CONFIGURATION
# ============================================
NODE_ENV=development
PORT=3000
FRONTEND_PUBLIC_URL=http://localhost:5173

# ============================================
# SUPABASE CONFIGURATION
# ============================================
# Frontend variables (Vite requires VITE_ prefix)
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=

# Backend service role key (backend will use VITE_SUPABASE_URL as fallback)
SUPABASE_SERVICE_ROLE_KEY=

# ============================================
# GOOGLE CLOUD / VERTEX AI CONFIGURATION
# ============================================
GOOGLE_CLOUD_PROJECT_ID=
GOOGLE_CLOUD_LOCATION=us-central1

# ============================================
# REDIS / UPSTASH CONFIGURATION
# ============================================
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=

# ============================================
# PHONEPE PAYMENT GATEWAY CONFIGURATION
# ============================================
# Frontend variables (Vite requires VITE_ prefix)
VITE_PHONEPE_MERCHANT_ID=
VITE_PHONEPE_SALT_KEY=
VITE_PHONEPE_SALT_INDEX=1
VITE_PHONEPE_ENV=SANDBOX
```

## Variables Summary

### Total Variables: 13

1. **NODE_ENV** - Application environment (development/production)
2. **PORT** - Server port (default: 3000)
3. **FRONTEND_PUBLIC_URL** - Frontend URL (default: http://localhost:5173)
4. **VITE_SUPABASE_URL** - Supabase project URL (frontend)
5. **VITE_SUPABASE_ANON_KEY** - Supabase anonymous key (frontend)
6. **SUPABASE_SERVICE_ROLE_KEY** - Supabase service role key (backend only)
7. **GOOGLE_CLOUD_PROJECT_ID** - Google Cloud project ID
8. **GOOGLE_CLOUD_LOCATION** - Google Cloud region (default: us-central1)
9. **UPSTASH_REDIS_REST_URL** - Upstash Redis REST URL
10. **UPSTASH_REDIS_REST_TOKEN** - Upstash Redis REST token
11. **VITE_PHONEPE_MERCHANT_ID** - PhonePe merchant ID
12. **VITE_PHONEPE_SALT_KEY** - PhonePe salt key
13. **VITE_PHONEPE_SALT_INDEX** - PhonePe salt index (default: 1)
14. **VITE_PHONEPE_ENV** - PhonePe environment (default: SANDBOX)

## Notes

- All variables are currently **unfilled** (empty values)
- Backend uses `VITE_SUPABASE_URL` as fallback (no duplicate needed)
- Backend uses `VITE_PHONEPE_*` variables directly (no duplicates)
- **Removed**: YouTube, Facebook, Instagram, LinkedIn, Twitter, Maps, PostHog, Stripe, OpenAI variables (not used in code)

