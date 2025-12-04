# Production Auth Fix - raptorflow.in

## 🔧 Issues Fixed

1. **OAuth Callback Handler** - Now handles both hash (#) and query (?) parameters
2. **Error Handling** - Better error messages and logging
3. **Session Detection** - Improved session detection after OAuth redirect
4. **Redirect URLs** - All using `/auth/callback` consistently

## ⚠️ CRITICAL: Supabase Configuration

You **MUST** configure these in your Supabase Dashboard:

### 1. Site URL
- Go to: **Authentication → URL Configuration**
- **Site URL**: `https://raptorflow.in`

### 2. Redirect URLs
Add these **exact** URLs:
- `https://raptorflow.in/auth/callback`
- `https://raptorflow.in/app`
- `https://raptorflow.in/**` (wildcard for all routes)

### 3. Google OAuth Provider
- Go to: **Authentication → Providers → Google**
- Make sure Google is **enabled**
- **Authorized redirect URIs** in Google Cloud Console should include:
  - `https://raptorflow.in/auth/callback`
  - `https://raptorflow.in/**`

## 🧪 Testing

1. Go to `https://raptorflow.in/login`
2. Click "Continue with Google"
3. After Google auth, you should be redirected to `/auth/callback`
4. Then automatically redirected to `/app`
5. Check browser console for any errors

## 🐛 Debugging

If auth still doesn't work:

1. **Check Browser Console** - Look for:
   - "OAuth callback - URL: ..."
   - "Session set successfully..."
   - Any error messages

2. **Check Supabase Logs**:
   - Dashboard → Logs → Auth Logs
   - Look for OAuth attempts

3. **Verify Redirect URLs Match Exactly**:
   - Supabase redirect URL must match Google OAuth redirect URI
   - Case-sensitive, must include protocol (https://)

4. **Test Session**:
   ```javascript
   // In browser console on raptorflow.in
   const { data } = await supabase.auth.getSession()
   console.log('Session:', data.session)
   ```

## 📝 Environment Variables (Vercel)

Make sure these are set in Vercel Dashboard → Settings → Environment Variables:

- `VITE_SUPABASE_URL` - Your Supabase project URL
- `VITE_SUPABASE_ANON_KEY` - Your Supabase anon key

After updating, **redeploy** the app.

