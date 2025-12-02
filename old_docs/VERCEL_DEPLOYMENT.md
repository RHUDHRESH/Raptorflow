# 🚀 Vercel Deployment Guide - Raptorflow

## Current Build Status
✅ Dependencies installed successfully
⏳ Build in progress...

## ⚠️ CRITICAL: Environment Variables Required

Your build will likely **succeed**, but the app **won't work** without environment variables set in Vercel.

### **Step 1: Add Environment Variables to Vercel**

1. Go to your Vercel Dashboard: https://vercel.com/dashboard
2. Select your **Raptorflow** project
3. Click **Settings** → **Environment Variables**
4. Add the following variables:

#### **Required Variables:**

```env
# Supabase Configuration (REQUIRED)
VITE_SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI3Nzk1OTEsImV4cCI6MjA0ODM1NTU5MX0.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw

# Environment
VITE_ENVIRONMENT=production

# Backend API (Update with your backend URL when deployed)
VITE_BACKEND_API_URL=https://your-backend-url.com/api/v1
```

#### **Optional Variables:**

```env
# PostHog Analytics (Optional)
VITE_POSTHOG_KEY=your_posthog_key_here
VITE_POSTHOG_HOST=https://app.posthog.com

# Google Maps (Optional)
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_key_here
```

### **Step 2: Set Environment for All Environments**

When adding each variable, select:
- ✅ **Production**
- ✅ **Preview**
- ✅ **Development**

This ensures the variables work in all deployment contexts.

### **Step 3: Redeploy After Adding Variables**

After adding environment variables:
1. Go to **Deployments** tab
2. Click **⋯** (three dots) on the latest deployment
3. Click **Redeploy**
4. ✅ Variables will now be included in the build

---

## Build Configuration

Your `vercel.json` is correctly configured:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "./dist",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

This ensures:
- ✅ SPA routing works (all routes → index.html)
- ✅ Static assets cached properly
- ✅ Security headers applied

---

## Expected Build Output

```
✅ Dependencies installed (609 packages)
✅ Running vite build
✅ Transforming files...
✅ Rendering chunks...
✅ Computing gzip size...
✅ dist/index.html created
✅ dist/assets/* created
✅ Build completed
```

---

## Post-Deployment Checklist

### 1. **Verify Environment Variables**
- Go to Vercel Dashboard → Settings → Environment Variables
- Confirm all `VITE_*` variables are set
- Check they're enabled for Production/Preview/Development

### 2. **Test the Deployed App**
Visit your Vercel URL (e.g., `raptorflow.vercel.app`) and check:

- ✅ Login page loads
- ✅ No "Configuration Missing" warning
- ✅ Google OAuth button works
- ✅ Can sign up/login
- ✅ Dashboard loads after login

### 3. **Configure OAuth Redirect URLs**

In Supabase Dashboard:
1. Go to: https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc/auth/url-configuration
2. Add your Vercel URL to **Site URL**:
   ```
   https://your-app.vercel.app
   ```
3. Add to **Redirect URLs**:
   ```
   https://your-app.vercel.app
   https://your-app.vercel.app/**
   ```

### 4. **Set Up Custom Domain (Optional)**

1. Go to Vercel Dashboard → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Update Supabase redirect URLs with new domain

---

## Troubleshooting

### Build Fails with "Module not found"
- Check `package.json` has all dependencies
- Run `npm install` locally to verify
- Commit `package-lock.json` to git

### Build Succeeds but App Shows Errors
- ⚠️ **Environment variables not set**
- Go to Vercel → Settings → Environment Variables
- Add all `VITE_*` variables
- Redeploy

### "Configuration Missing" Warning on Deployed App
- Environment variables not set in Vercel
- Variables must have `VITE_` prefix
- Redeploy after adding variables

### Google OAuth Not Working
- Update Supabase redirect URLs
- Add Vercel domain to allowed URLs
- Check OAuth credentials in Supabase Dashboard

### 404 on Page Refresh
- ✅ Already fixed with `vercel.json` rewrites
- All routes redirect to `index.html`

---

## Quick Commands

### Deploy from CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy to production
vercel --prod

# Deploy to preview
vercel
```

### Check Build Locally
```bash
# Build locally to test
npm run build

# Preview production build
npm run preview
```

### View Logs
```bash
# View deployment logs
vercel logs <deployment-url>
```

---

## Environment Variables Quick Copy

For easy copy-paste into Vercel:

**Variable Name:** `VITE_SUPABASE_URL`  
**Value:** `https://vpwwzsanuyhpkvgorcnc.supabase.co`

**Variable Name:** `VITE_SUPABASE_ANON_KEY`  
**Value:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI3Nzk1OTEsImV4cCI6MjA0ODM1NTU5MX0.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw`

**Variable Name:** `VITE_ENVIRONMENT`  
**Value:** `production`

**Variable Name:** `VITE_BACKEND_API_URL`  
**Value:** `https://your-backend-url.com/api/v1` (update when backend is deployed)

---

## Security Notes

### ✅ Safe to Expose (Frontend)
- `VITE_SUPABASE_URL` - Public URL
- `VITE_SUPABASE_ANON_KEY` - Public anon key (RLS protects data)
- `VITE_ENVIRONMENT` - Environment name

### ⚠️ Never Expose (Backend Only)
- `SUPABASE_SERVICE_KEY` - Keep in backend only
- `SUPABASE_JWT_SECRET` - Keep in backend only
- API keys with write access

The `VITE_` prefix makes variables available to the browser, which is intentional for these public keys. Supabase's Row Level Security (RLS) protects your data even with public keys.

---

## Next Steps After Deployment

1. ✅ Add environment variables to Vercel
2. ✅ Redeploy
3. ✅ Test login/signup flow
4. ✅ Update Supabase redirect URLs
5. 🔄 Deploy backend (if needed)
6. 🔄 Update `VITE_BACKEND_API_URL`
7. 🔄 Set up custom domain
8. 🔄 Configure monitoring/analytics

---

**Need Help?**
- Vercel Docs: https://vercel.com/docs
- Supabase Docs: https://supabase.com/docs
- Check deployment logs in Vercel Dashboard
