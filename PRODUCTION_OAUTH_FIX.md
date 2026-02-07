# ✅ Production OAuth Redirect URLs - Fixed

## Summary

All OAuth redirect URLs in the codebase now use **dynamic `window.location.origin`** instead of hardcoded localhost URLs. This ensures the application works correctly in both development and production environments.

## ✅ Code Changes Made

### 1. Fixed `src/pages/Start.jsx`
- **Before**: Redirected directly to `/onboarding/intro` 
- **After**: Now uses `/auth/callback` consistently (same as other OAuth flows)
- **Impact**: All OAuth flows now go through the centralized callback handler

### 2. Verified All OAuth Redirect URLs
All OAuth redirect configurations use `window.location.origin`:
- ✅ `src/lib/supabase.js` - Uses `${window.location.origin}/auth/callback`
- ✅ `src/contexts/AuthContext.jsx` - Uses `${window.location.origin}/auth/callback`
- ✅ `src/pages/Start.jsx` - Now uses `${window.location.origin}/auth/callback`
- ✅ `src/pages/OAuthCallback.jsx` - Handles callback correctly

**No hardcoded localhost URLs found in source code!**

## ⚠️ CRITICAL: Supabase Dashboard Configuration

You **MUST** verify these settings in your Supabase Dashboard:

### Step 1: Authentication → URL Configuration

**Site URL:**
```
https://www.raptorflow.in
```

**Redirect URLs** (add ALL of these - both with and without www):
```
https://www.raptorflow.in/auth/callback
https://www.raptorflow.in/app
https://www.raptorflow.in/**
https://raptorflow.in/auth/callback
https://raptorflow.in/app
https://raptorflow.in/**
```

**Why both?** Users might access your site with or without `www`, and Supabase needs to allow redirects for both.

### Step 2: Verify Google OAuth Provider

1. Go to **Authentication → Providers → Google**
2. Ensure Google provider is **enabled**
3. Verify Client ID and Client Secret are set correctly

## ⚠️ CRITICAL: Google Cloud Console Configuration

### OAuth 2.0 Client IDs → Authorized JavaScript origins

Add both:
```
https://www.raptorflow.in
https://raptorflow.in
```

### OAuth 2.0 Client IDs → Authorized redirect URIs

Add these **exact** URLs:
```
https://www.raptorflow.in/auth/callback
https://raptorflow.in/auth/callback
https://vpwwzsanuyhpkvgorcnc.supabase.co/auth/v1/callback
```

**Important:** The Supabase callback URL (`https://vpwwzsanuyhpkvgorcnc.supabase.co/auth/v1/callback`) is required because Google redirects to Supabase first, then Supabase redirects to your app.

## 🧪 Testing Checklist

### 1. Test OAuth Flow from Login Page
- [ ] Go to `https://www.raptorflow.in/login`
- [ ] Click "Continue with Google"
- [ ] Complete Google authentication
- [ ] Should redirect to `/auth/callback`
- [ ] Should then redirect to `/app`
- [ ] Check browser console for errors

### 2. Test OAuth Flow from Signup Page
- [ ] Go to `https://www.raptorflow.in/start` (or signup page)
- [ ] Click "Continue with Google"
- [ ] Complete Google authentication
- [ ] Should redirect to `/auth/callback`
- [ ] Should then redirect to `/app`
- [ ] Check browser console for errors

### 3. Test Without www
- [ ] Try accessing `https://raptorflow.in/login` (without www)
- [ ] Test OAuth flow
- [ ] Should work identically

### 4. Verify Console Logs

Open browser DevTools → Console and look for:
```
OAuth callback - URL: https://www.raptorflow.in/auth/callback?...
OAuth callback - Hash: ...
OAuth callback - Search: ...
Found tokens, setting session...
Session set successfully, user: [user-id]
```

## 🐛 Troubleshooting

### Issue: "redirect_uri_mismatch" Error

**Symptoms:** Google shows error about redirect URI not matching

**Causes:**
1. Redirect URL in Google Cloud Console doesn't match exactly
2. Supabase redirect URL not configured correctly
3. Missing `www` variant

**Fix:**
1. Check Google Cloud Console → OAuth 2.0 → Authorized redirect URIs
2. Ensure all three URLs are listed exactly:
   - `https://www.raptorflow.in/auth/callback`
   - `https://raptorflow.in/auth/callback`
   - `https://vpwwzsanuyhpkvgorcnc.supabase.co/auth/v1/callback`
3. Check Supabase → Authentication → URL Configuration
4. Ensure Site URL is `https://www.raptorflow.in`

### Issue: Redirects to Landing Page Instead of App

**Symptoms:** After OAuth, user ends up on `/` instead of `/app`

**Causes:**
1. Site URL in Supabase is wrong
2. Redirect URLs not configured

**Fix:**
1. Set Site URL to `https://www.raptorflow.in` (with www!)
2. Add redirect URLs as listed above

### Issue: Session Not Persisting

**Symptoms:** User gets logged out immediately or session doesn't save

**Causes:**
1. Cookie domain mismatch
2. CORS issues
3. Site URL mismatch

**Fix:**
1. Ensure Site URL matches your domain exactly (`https://www.raptorflow.in`)
2. Check browser console for CORS errors
3. Verify cookies are being set (DevTools → Application → Cookies)

### Issue: OAuth Callback Shows Error

**Symptoms:** `/auth/callback` page shows error or redirects to login with error

**Check:**
1. Browser console for error messages
2. Supabase Dashboard → Logs → Auth Logs
3. Verify tokens are being received (check URL hash/query params)

## 📋 Verification Commands

Run these in browser console on `https://www.raptorflow.in`:

```javascript
// Check environment variables
console.log('Supabase URL:', import.meta.env.VITE_SUPABASE_URL)
console.log('Current origin:', window.location.origin)

// Check session
const { data } = await supabase.auth.getSession()
console.log('Current session:', data.session)

// Check user
const { data: userData } = await supabase.auth.getUser()
console.log('Current user:', userData.user)
```

## ✅ Code Verification

All OAuth redirect URLs in the codebase use dynamic `window.location.origin`:

```javascript
// ✅ CORRECT - Dynamic origin
redirectTo: `${window.location.origin}/auth/callback`

// ❌ WRONG - Hardcoded (not found in codebase)
redirectTo: 'http://localhost:5173/auth/callback'
```

## 📝 Next Steps

1. ✅ Code is production-ready (no hardcoded localhost)
2. ⚠️ **Verify Supabase configuration** (see Step 1 above)
3. ⚠️ **Verify Google Cloud Console** (see Step 2 above)
4. 🧪 **Test OAuth flow** on production domain
5. 📊 **Monitor Supabase Auth Logs** for any issues

## 🔗 Quick Links

- Supabase Dashboard: https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc/auth/url-configuration
- Google Cloud Console: https://console.cloud.google.com/apis/credentials
- Production Site: https://www.raptorflow.in

