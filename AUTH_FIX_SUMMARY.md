# Authentication Fix Summary - December 4, 2025

## Issues Identified

### 1. www vs non-www Domain Mismatch (CRITICAL - Production)
The Supabase auth logs revealed the root cause:
- Some requests came from `https://www.raptorflow.in`
- Some requests came from `https://raptorflow.in`

**Why this breaks authentication:**
- Cookies are domain-specific
- A session cookie set on `raptorflow.in` is NOT accessible on `www.raptorflow.in`
- After OAuth callback, the user lands on a different domain than where they started
- Session is lost, user appears logged out

### 2. Users Created in auth.users but no Profile
- Users were being created successfully in `auth.users`
- But `public.profiles` entries were missing
- This was causing dashboard access issues even after login

## Fixes Applied

### Fix 1: Vercel Domain Redirect (vercel.json)
Added permanent redirect from www to non-www:
```json
{
  "redirects": [
    {
      "source": "/:path*",
      "has": [
        {
          "type": "host",
          "value": "www.raptorflow.in"
        }
      ],
      "destination": "https://raptorflow.in/:path*",
      "permanent": true
    }
  ]
}
```

### Fix 2: Improved OAuth Callback (src/pages/OAuthCallback.jsx)
- Added status messages for better UX
- Improved session detection logic
- Added longer waits for profile creation
- Better error handling

## CRITICAL: Manual Configuration Required

### Supabase Dashboard Configuration
1. Go to https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc/auth/url-configuration
2. Set **Site URL** to: `https://raptorflow.in` (WITHOUT www)
3. Add these **Redirect URLs**:
   - `https://raptorflow.in/auth/callback`
   - `https://raptorflow.in/**`
   - `http://localhost:5173/auth/callback`
   - `http://localhost:5173/**`

### Google Cloud Console Configuration
1. Go to https://console.cloud.google.com/apis/credentials
2. Edit your OAuth 2.0 Client ID
3. **Authorized JavaScript origins** (add all):
   - `https://raptorflow.in`
   - `http://localhost:5173`
   - `http://localhost:3000`
4. **Authorized redirect URIs** (add all):
   - `https://vpwwzsanuyhpkvgorcnc.supabase.co/auth/v1/callback`
   - `https://raptorflow.in/auth/callback`
   - `http://localhost:5173/auth/callback`

## For Localhost Testing

Make sure you have a `.env` file with:
```
VITE_SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

And ensure `http://localhost:5173` is in both:
1. Supabase Redirect URLs
2. Google OAuth Authorized JavaScript origins

## Deployment

After making these changes:
1. Commit and push to trigger Vercel deployment
2. Wait for deployment to complete
3. Test by going to https://raptorflow.in/login (NOT www.raptorflow.in)
4. The www redirect should happen automatically after deployment

## Database Trigger (Already Applied)
A trigger was created to auto-create profiles:
```sql
CREATE TRIGGER create_profile_on_new_user
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();
```

This ensures new users automatically get a profile entry.

