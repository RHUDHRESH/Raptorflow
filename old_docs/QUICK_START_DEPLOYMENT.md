# 🚀 RaptorFlow - Quick Start Deployment

Your entire project has been refactored and optimized for seamless deployment on **Vercel** (frontend), **Google Cloud Run** (backend), and **Supabase** (database).

## ✅ What's Been Done

### Database Setup (Supabase)
- ✅ Created your Supabase project: `vpwwzsanuyhpkvgorcnc` (ap-south-1)
- ✅ Applied 3 core migrations:
  - `001_move_system_schema.sql` - Core system tables (moves, sprints, tech trees)
  - `002_assets_table.sql` - Asset management
  - `003_quests_table.sql` - Quest system with gamification

**Database Status**: ACTIVE_HEALTHY ✅

### Frontend Optimization (Vercel)
- ✅ `vercel.json` - Production deployment config
- ✅ `vite.config.js` - Optimized build with code splitting
- ✅ Security headers configured (XSS, CSRF, Clickjacking protection)
- ✅ Asset caching (1-year immutable for `/assets/*`)
- ✅ Environment variables ready for Vercel secrets

### Backend Optimization (Cloud Run)
- ✅ `Dockerfile.cloudrun` - Multi-stage production build
- ✅ `requirements-prod.txt` - Lean production dependencies
- ✅ Health checks configured for Cloud Run
- ✅ Non-root user execution for security
- ✅ Auto-scaling configuration ready (1-10 instances)

### Configuration Files
- ✅ `.env.example` - Sanitized environment template
- ✅ `cloudbuild-prod.yaml` - CI/CD pipeline for Cloud Build
- ✅ `.gitignore.prod` - Secrets protection

---

## 🎯 Three-Step Deployment

### Step 1: Deploy Frontend to Vercel (5 minutes)

**Windows:**
```cmd
cd C:\Users\hp\OneDrive\Desktop\Raptorflow
deploy-frontend.cmd
```

**Mac/Linux:**
```bash
cd /path/to/Raptorflow
bash deploy-frontend.sh
```

**What this does:**
- Installs Vercel CLI if needed
- Links your GitHub repo to Vercel
- Sets up environment variables:
  - `VITE_SUPABASE_URL`
  - `VITE_SUPABASE_ANON_KEY`
  - `VITE_BACKEND_API_URL`
  - `VITE_POSTHOG_KEY` (optional)
- Builds optimized frontend
- Deploys to Vercel's CDN

**Result**: Your frontend is live at `https://your-project.vercel.app`

---

### Step 2: Deploy Backend to Cloud Run (10 minutes)

**Prepare:**
1. Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

**Create credentials file** `backend/.env.prod`:
```
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING
GOOGLE_CLOUD_PROJECT=raptorflow-477017
VERTEX_AI_LOCATION=us-central1
SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key_from_supabase
SUPABASE_JWT_SECRET=your_jwt_secret_from_supabase
REDIS_URL=redis://your-redis-host:6379/0
SECRET_KEY=generate_a_strong_random_string_here
ALGORITHM=HS256
```

**Windows:**
```cmd
deploy-backend.cmd
```

**Mac/Linux:**
```bash
bash deploy-backend.sh
```

**What this does:**
- Authenticates with Google Cloud
- Enables required APIs (Cloud Run, Container Registry, Cloud Build)
- Builds Docker image with production optimizations
- Pushes to Google Container Registry
- Deploys to Cloud Run with auto-scaling
- Sets up health checks and environment variables

**Result**: Your backend is live at `https://raptorflow-backend-xxxx.run.app`

---

### Step 3: Connect Frontend to Backend (2 minutes)

Once your backend is deployed:

1. Copy the Cloud Run service URL from deployment output
2. Go to Vercel Dashboard → Project → Settings → Environment Variables
3. Update `VITE_BACKEND_API_URL` with your Cloud Run URL:
   ```
   https://raptorflow-backend-xxxx.run.app/api/v1
   ```
4. Trigger a redeploy by pushing to main branch:
   ```bash
   git push origin main
   ```

---

## 📊 Your Deployment Architecture

```
┌─────────────────────┐
│  Your Browser       │
└──────────┬──────────┘
           │
    ┌──────▼────────┐
    │   Vercel CDN  │ (Frontend React App)
    │ raptorflow    │ ✨ Auto-scaling, global cache
    │ .vercel.app   │
    └──────┬────────┘
           │
    ┌──────▼────────────────────────┐
    │  Google Cloud Run             │
    │  (Backend - FastAPI)          │
    │  raptorflow-backend.run.app   │ 🚀 Auto-scales 1-10 instances
    └──────┬────────────────────────┘
           │
    ┌──────▼──────────────────────┐
    │   Supabase (PostgreSQL)     │
    │   Database + Auth + Storage │ 🔐 Secured with RLS
    └─────────────────────────────┘
```

---

## 🔐 Security Features Enabled

### Frontend (Vercel)
- XSS Protection Headers
- CSRF Prevention
- Clickjacking Protection (X-Frame-Options: DENY)
- Strict Content Security Policy
- 1-year cache for immutable assets
- Console logs stripped in production

### Backend (Cloud Run)
- Non-root user execution
- Health checks enabled
- Automatic HTTPS
- Rate limiting configured
- Input validation with Pydantic
- JWT token authentication
- CORS whitelisting

### Database (Supabase)
- Row-Level Security (RLS) policies
- PostgreSQL native security
- Encrypted connections
- Automatic backups
- IP whitelisting support

---

## 📈 Monitoring & Logging

### View Frontend Logs
```bash
# Vercel
vercel logs
```

### View Backend Logs
```bash
# Cloud Run
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=raptorflow-backend" --limit 50

# Or tail live logs
gcloud logging tail projects/raptorflow-477017/logs/cloud.googleapis.com%2Fcloud-run-resource --limit 50
```

### View Database Logs
- Login to Supabase Dashboard
- Go to Project → Logs
- Select "API" or "Database" for relevant logs

---

## 🎨 Project Structure After Refactoring

```
Raptorflow/
├── 📦 Frontend (Vercel)
│   ├── src/
│   ├── package.json
│   ├── vite.config.js (optimized)
│   ├── vercel.json (production config)
│   └── index.html
│
├── 🐍 Backend (Cloud Run)
│   ├── backend/
│   │   ├── main.py
│   │   ├── agents/ (33+ agents)
│   │   ├── graphs/ (12 orchestration graphs)
│   │   ├── routers/ (12 API endpoints)
│   │   ├── services/ (15 business logic services)
│   │   └── models/ (10 data models)
│   ├── Dockerfile.cloudrun (production)
│   ├── requirements-prod.txt (optimized)
│   └── requirements.txt (full dependencies)
│
├── 🗄️ Database (Supabase)
│   ├── database/
│   │   ├── migrations/
│   │   │   ├── 001_move_system_schema.sql ✅
│   │   │   ├── 002_assets_table.sql ✅
│   │   │   └── 003_quests_table.sql ✅
│   │   └── rls-policies.sql
│
├── 📚 Configuration
│   ├── .env.example (sanitized)
│   ├── vercel.json (frontend deployment)
│   ├── cloudbuild-prod.yaml (CI/CD)
│   ├── DEPLOYMENT_GUIDE.md (detailed docs)
│   └── QUICK_START_DEPLOYMENT.md (this file)
│
└── 🔧 Deployment Scripts
    ├── deploy-frontend.sh / deploy-frontend.cmd
    └── deploy-backend.sh / deploy-backend.cmd
```

---

## 🆘 Troubleshooting

### "Docker command not found"
Solution: Install Docker Desktop from https://www.docker.com/products/docker-desktop

### "gcloud command not found"
Solution: Install Google Cloud SDK from https://cloud.google.com/sdk/docs/install

### Frontend shows blank page
- Check browser console for errors
- Verify `VITE_BACKEND_API_URL` in Vercel environment
- Ensure backend is running and accessible
- Check CORS settings in backend

### Backend returns 500 errors
- Check Cloud Run logs: `gcloud logging tail ...`
- Verify environment variables in Cloud Run service
- Check Supabase connectivity and credentials
- Verify Redis connection if using cache

### Database connection timeouts
- Check Supabase project is active
- Verify service key credentials
- Increase Cloud Run timeout to 3600s
- Enable connection pooling if needed

---

## 💰 Estimated Costs

### Vercel Frontend
- **Free Tier**: 100GB bandwidth/month included
- **Pro**: $20/month (recommended for production)
- Estimate: **$0-20/month**

### Google Cloud Run Backend
- **Free Tier**: 180,000 vCPU-seconds/month
- **Pay-as-you-go**: ~$0.000025 per vCPU-second
- Estimate: **$5-50/month** depending on traffic

### Supabase Database
- **Free Tier**: 500MB database + 1GB bandwidth
- **Pro**: $25/month
- Estimate: **$0-25/month** starting

**Total estimated cost**: **$5-95/month** depending on scale

---

## 🎯 Next Steps

1. **Collect Credentials:**
   ```
   Supabase Anon Key: Dashboard → Settings → API → anon key
   Supabase Service Key: Dashboard → Settings → API → service_role key
   Google Maps API Key: Google Cloud Console → APIs & Services
   ```

2. **Deploy Frontend:**
   ```bash
   deploy-frontend.cmd  (Windows)
   bash deploy-frontend.sh  (Mac/Linux)
   ```

3. **Deploy Backend:**
   ```bash
   deploy-backend.cmd  (Windows)
   bash deploy-backend.sh  (Mac/Linux)
   ```

4. **Update Frontend Config:**
   - Set `VITE_BACKEND_API_URL` to your Cloud Run service URL

5. **Test:**
   - Visit your Vercel deployment
   - Check API connectivity
   - Monitor logs for errors

---

## 📞 Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Supabase Docs**: https://supabase.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev

---

## 🎉 Summary

Your RaptorFlow application is now **production-ready** with:

✅ Automated database migrations
✅ Optimized frontend for Vercel
✅ Containerized backend for Cloud Run
✅ Security hardening across all layers
✅ Auto-scaling configuration
✅ Comprehensive monitoring setup
✅ CI/CD pipeline ready
✅ Environment management system

**Ready to deploy? Start with `deploy-frontend.cmd` or `deploy-frontend.sh`! 🚀**

