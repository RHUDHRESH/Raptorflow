# 🔍 Production Login Diagnostic Guide

## Your Domain: raptorlow.in (or raptorflow.in?)

**IMPORTANT**: Make sure you're using the correct domain. I see references to both `raptorlow.in` and `raptorflow.in` in your codebase.

---

## ✅ Step-by-Step Fix Checklist

### 1. **Verify Your Actual Domain**
First, confirm which domain you're actually using:
- `https://raptorlow.in` (no 'f')
- `https://raptorflow.in` (with 'f')
- `https://www.raptorlow.in` (with www)
- `https://www.raptorflow.in` (with www)

**Check**: Open your production site and look at the URL bar.

---

### 2. **Supabase Dashboard Configuration** ⚠️ CRITICAL

Go to: **Supabase Dashboard → Authentication → URL Configuration**

#### Site URL:
Set to your **exact production domain** (with or without www, whichever you use):
```
https://raptorlow.in
```
OR
```
https://www.raptorlow.in
```

**Important**: Use the exact domain users access. If users can access both www and non-www, you'll need to handle both.

#### Redirect URLs:
Add **ALL** of these (replace `raptorlow.in` with your actual domain):

```
https://raptorflow.in/auth/callback
https://raptorflow.in/app
https://raptorflow.in/**
https://www.raptorflow.in/auth/callback
https://www.raptorflow.in/app
https://www.raptorflow.in/**
```

**Why both?** Users might access your site with or without `www`, and Supabase needs to allow redirects for both.

---

### 3. **Google Cloud Console OAuth Configuration** ⚠️ CRITICAL

Go to: **Google Cloud Console → APIs & Services → Credentials → Your OAuth 2.0 Client ID**

#### Authorized JavaScript origins:
Add both (with and without www):
```
https://raptorflow.in
https://www.raptorflow.in
```

#### Authorized redirect URIs:
Add these **exact** URLs:
```
https://raptorlow.in/auth/callback
https://www.raptorlow.in/auth/callback
https://[your-supabase-project].supabase.co/auth/v1/callback
```

**Replace `[your-supabase-project]`** with your actual Supabase project reference (e.g., `abcdefghijklmnop`).

---

### 4. **Vercel Environment Variables** ⚠️ CRITICAL

Go to: **Vercel Dashboard → Your Project → Settings → Environment Variables**

Make sure these are set for **Production** environment:
- `VITE_SUPABASE_URL` = `https://[your-project].supabase.co`
- `VITE_SUPABASE_ANON_KEY` = `[your-anon-key]`

**After adding/updating env vars, you MUST redeploy!**

To redeploy:
1. Go to Vercel Dashboard → Your Project → Deployments
2. Click "..." on the latest deployment → "Redeploy"

---

### 5. **Test the Flow**

1. Open your production site: `https://raptorlow.in/login`
2. Open **Browser DevTools → Console** (F12)
3. Click "Continue with Google"
4. After Google auth, check console logs:
   - Should see: `"OAuth callback - URL: ..."`
   - Should see: `"Session set successfully..."`
   - Should redirect to `/app`

---

## 🐛 Common Issues & Solutions

### Issue 1: "redirect_uri_mismatch" Error
**Cause**: Redirect URL doesn't match exactly between Supabase and Google OAuth

**Fix**:
- Check Supabase redirect URLs match Google OAuth redirect URIs **exactly**
- Must include `https://` (not `http://`)
- Case-sensitive
- No trailing slashes (except for wildcard `/**`)

### Issue 2: Redirects to Landing Page (`/`) Instead of `/app`
**Cause**: Site URL in Supabase is set incorrectly

**Fix**: 
- Set Site URL to your exact production domain: `https://raptorlow.in`
- Make sure it matches what users see in the browser

### Issue 3: Session Not Persisting
**Cause**: Cookies not being set (domain/CORS issue)

**Fix**:
- Make sure Site URL matches your domain exactly
- Check browser console for CORS errors
- Verify environment variables are set correctly in Vercel

### Issue 4: Works on Localhost but Not Production
**Cause**: Environment variables not set in production OR Supabase redirect URLs not configured

**Fix**:
- Verify `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` are set in Vercel
- Add production redirect URLs to Supabase (not just localhost)
- Redeploy after changing environment variables

---

## 🔬 Debug Commands

Run these in browser console on your production site (`https://raptorlow.in`):

```javascript
// Check if Supabase is configured
console.log('Supabase URL:', import.meta.env.VITE_SUPABASE_URL)
console.log('Supabase Key exists:', !!import.meta.env.VITE_SUPABASE_ANON_KEY)

// Check current session
const { data } = await supabase.auth.getSession()
console.log('Current session:', data.session)

// Check user
const { data: userData } = await supabase.auth.getUser()
console.log('Current user:', userData.user)
```

---

## 📋 Quick Verification Checklist

- [ ] Supabase Site URL matches your production domain exactly
- [ ] Supabase Redirect URLs include your production domain
- [ ] Google OAuth Authorized JavaScript origins include your production domain
- [ ] Google OAuth Authorized redirect URIs include your production domain
- [ ] Vercel environment variables are set for Production
- [ ] Vercel deployment is redeployed after env var changes
- [ ] Browser console shows no errors during login flow

---

## 🆘 Still Not Working?

If login still doesn't work after checking all above:

1. **Check Browser Console** - Look for specific error messages
2. **Check Supabase Logs** - Dashboard → Logs → Auth Logs
3. **Check Network Tab** - Look for failed requests to Supabase
4. **Verify Domain** - Make absolutely sure you're using the correct domain (raptorlow.in vs raptorflow.in)

---

## 📝 Notes

- The code is already using `window.location.origin` dynamically, which is correct ✅
- The OAuth callback handler supports both hash (#) and query (?) parameters ✅
- The issue is almost certainly in the Supabase/Google OAuth configuration, not the code ✅

