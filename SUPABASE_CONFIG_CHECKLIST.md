# 🔴 CRITICAL: Supabase Configuration Checklist

## ⚠️ This MUST be configured correctly for auth to work on raptorflow.in

### Step 1: Supabase Dashboard → Authentication → URL Configuration

**Site URL:**
```
https://www.raptorflow.in
```

**Redirect URLs** (add ALL of these):
```
https://www.raptorflow.in/auth/callback
https://www.raptorflow.in/app
https://www.raptorflow.in/**
https://raptorflow.in/auth/callback
https://raptorflow.in/app
https://raptorflow.in/**
```

### Step 2: Google Cloud Console → OAuth 2.0 Client IDs

**Authorized JavaScript origins:**
```
https://www.raptorflow.in
https://raptorflow.in
```

**Authorized redirect URIs:**
```
https://www.raptorflow.in/auth/callback
https://raptorflow.in/auth/callback
https://[your-supabase-project].supabase.co/auth/v1/callback
```

### Step 3: Verify Environment Variables in Vercel

Go to Vercel Dashboard → Your Project → Settings → Environment Variables

Make sure these are set:
- `VITE_SUPABASE_URL` = `https://[your-project].supabase.co`
- `VITE_SUPABASE_ANON_KEY` = `[your-anon-key]`

**After adding/updating env vars, you MUST redeploy!**

### Step 4: Test the Flow

1. Go to `https://www.raptorflow.in/login`
2. Open browser DevTools → Console
3. Click "Continue with Google"
4. After Google auth, check console logs:
   - Should see: "OAuth callback - URL: ..."
   - Should see: "Session set successfully..."
   - Should redirect to `/app`

### Common Issues

**Issue: Redirects to landing page (`/`)**
- **Cause**: Site URL in Supabase is set to `/` or wrong domain
- **Fix**: Set Site URL to `https://www.raptorflow.in` (with www!)

**Issue: "redirect_uri_mismatch" error**
- **Cause**: Redirect URL doesn't match exactly
- **Fix**: Check both Supabase redirect URLs and Google OAuth redirect URIs match exactly

**Issue: Session not persisting**
- **Cause**: Cookies not being set (domain/CORS issue)
- **Fix**: Make sure Site URL matches your domain exactly

### Debug Commands

Run these in browser console on `https://www.raptorflow.in`:

```javascript
// Check Supabase client
console.log('Supabase URL:', import.meta.env.VITE_SUPABASE_URL)

// Check session
const { data } = await supabase.auth.getSession()
console.log('Current session:', data.session)

// Check user
const { data: userData } = await supabase.auth.getUser()
console.log('Current user:', userData.user)
```

