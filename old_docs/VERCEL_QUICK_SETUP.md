# ⚡ Quick Vercel Setup - 3 Steps

## Your build is running! Here's what to do next:

### 🔴 STEP 1: Add Environment Variables (CRITICAL)

Go to: **Vercel Dashboard → Your Project → Settings → Environment Variables**

Add these 3 variables:

| Variable Name | Value |
|--------------|-------|
| `VITE_SUPABASE_URL` | `https://vpwwzsanuyhpkvgorcnc.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI3Nzk1OTEsImV4cCI6MjA0ODM1NTU5MX0.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw` |
| `VITE_ENVIRONMENT` | `production` |

✅ Select: **Production**, **Preview**, **Development** for each

### 🟡 STEP 2: Redeploy

After adding variables:
1. Go to **Deployments** tab
2. Click **⋯** on latest deployment
3. Click **Redeploy**

### 🟢 STEP 3: Update Supabase

Go to: https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc/auth/url-configuration

Add your Vercel URL:
- **Site URL**: `https://your-app.vercel.app`
- **Redirect URLs**: `https://your-app.vercel.app/**`

---

## ✅ Done!

Your app should now work on Vercel with:
- ✅ Login/Signup
- ✅ Google OAuth
- ✅ Dashboard access
- ✅ Database integration

---

**Full Guide:** See `VERCEL_DEPLOYMENT.md` for detailed instructions
