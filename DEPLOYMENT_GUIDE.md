# RaptorFlow Deployment Guide

Complete instructions for deploying RaptorFlow to Vercel (Frontend) and Google Cloud Run (Backend) with Supabase (Database).

## Quick Start

### Prerequisites
- Vercel account + CLI installed: `npm install -g vercel`
- Google Cloud SDK installed: `curl https://sdk.cloud.google.com | bash`
- Supabase project (already set up at `vpwwzsanuyhpkvgorcnc`)
- GitHub repository connected to Vercel

## Frontend Deployment (Vercel)

### Option 1: Git Integration (Recommended)

1. **Connect your GitHub repo to Vercel:**
   ```bash
   vercel link
   ```

2. **Set environment variables in Vercel Dashboard:**
   - Go to Project Settings → Environment Variables
   - Add these variables for all environments (Production, Preview, Development):
     ```
     VITE_SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
     VITE_SUPABASE_ANON_KEY=your_anon_key
     VITE_BACKEND_API_URL=https://your-cloud-run-backend.com/api/v1
     VITE_POSTHOG_KEY=your_posthog_key
     VITE_GOOGLE_MAPS_API_KEY=your_google_maps_key
     ```

3. **Push to main branch:**
   ```bash
   git push origin main
   ```
   Vercel will automatically build and deploy!

### Option 2: Manual Deployment

```bash
cd C:\Users\hp\OneDrive\Desktop\Raptorflow
vercel deploy --prod
```

### Verification
- Deployment URL: Check Vercel Dashboard
- Health check: `https://your-deployment.vercel.app`
- API connectivity: Should connect to Cloud Run backend at `VITE_BACKEND_API_URL`

---

## Backend Deployment (Google Cloud Run)

### Step 1: Prepare GCP Project

```bash
# Set your GCP project
gcloud config set project raptorflow-477017

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 2: Set Environment Variables

Create `backend/.env.prod` with production secrets:
```
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING

GOOGLE_CLOUD_PROJECT=raptorflow-477017
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_GEMINI_3_MODEL=gemini-1.5-pro-002

SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
SUPABASE_SERVICE_KEY=your_service_key_here
SUPABASE_JWT_SECRET=your_jwt_secret_here

REDIS_URL=redis://your-redis-host:6379/0
SECRET_KEY=use-a-strong-random-string-here
```

### Step 3: Build and Push Docker Image

```bash
# Build the image
docker build -f Dockerfile.cloudrun -t gcr.io/raptorflow-477017/raptorflow-backend:latest .

# Push to Google Container Registry
docker push gcr.io/raptorflow-477017/raptorflow-backend:latest
```

### Step 4: Deploy to Cloud Run

```bash
gcloud run deploy raptorflow-backend \
  --image gcr.io/raptorflow-477017/raptorflow-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 3600 \
  --env-vars-file backend/.env.prod
```

### Verification
```bash
# Get the service URL
gcloud run services describe raptorflow-backend --region us-central1

# Test the health endpoint
curl https://your-cloud-run-service.run.app/health
```

---

## Database Setup (Supabase)

Your Supabase project is already initialized with:
- **Project ID**: vpwwzsanuyhpkvgorcnc
- **Region**: ap-south-1
- **Database**: PostgreSQL 17

### Migrations Applied
✅ 001_move_system_schema.sql - Core tables (moves, sprints, etc.)
✅ 002_assets_table.sql - Asset management
✅ 003_quests_table.sql - Quest system

### Access Credentials
- **API URL**: https://vpwwzsanuyhpkvgorcnc.supabase.co
- **Anon Key**: Check Supabase dashboard → Project Settings
- **Service Role Key**: For backend API calls

---

## Environment Variables Reference

### Frontend (.env.local or Vercel)
```
VITE_ENVIRONMENT=production
VITE_SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_BACKEND_API_URL=https://your-cloud-run-backend.run.app/api/v1
VITE_POSTHOG_KEY=optional
VITE_GOOGLE_MAPS_API_KEY=optional
```

### Backend (backend/.env.prod)
```
ENVIRONMENT=production
DEBUG=False
GOOGLE_CLOUD_PROJECT=raptorflow-477017
SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
SECRET_KEY=strong-random-string-256-bits
```

---

## Monitoring & Logs

### View Cloud Run Logs
```bash
gcloud run services describe raptorflow-backend --region us-central1
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=raptorflow-backend" --limit 50 --format json
```

### Monitor Supabase
- Dashboard: https://app.supabase.com
- Database logs: Go to Project → Logs
- API stats: Project → API Analytics

### Monitor Vercel
- Dashboard: https://vercel.com/dashboard
- Deployment logs: Select project → Deployments tab
- Performance: Click deployment → Analytics

---

## Scaling & Performance

### Cloud Run Autoscaling
```bash
gcloud run services update raptorflow-backend \
  --min-instances 1 \
  --max-instances 10 \
  --region us-central1
```

### Vercel Optimization
- Image optimization: Automatic
- Code splitting: Configured in vite.config.js
- Caching: 1 year for `/assets/*`, no-cache for HTML

### Database Optimization
- Connection pooling: Use PgBouncer for Cloud Run
- Indexes: Created on all foreign keys and commonly queried fields
- RLS: Policies in place for multi-tenant isolation

---

## Troubleshooting

### Frontend won't load
1. Check env vars in Vercel: Settings → Environment Variables
2. Clear cache: `vercel env pull`
3. Rebuild: Push to main or `vercel deploy --prod`

### Backend returns 500 errors
1. Check logs: `gcloud logging read ...`
2. Verify env vars: `gcloud run services describe raptorflow-backend`
3. Check database connectivity: Verify SUPABASE_URL

### API connectivity issues
1. Verify CORS is configured in FastAPI
2. Check Cloud Run allows unauthenticated requests: `--allow-unauthenticated`
3. Test directly: `curl https://backend.run.app/health`

### Database connection timeouts
1. Increase Cloud Run timeout: `--timeout 3600`
2. Check Supabase connection limits
3. Enable connection pooling

---

## Security Checklist

- [ ] Change `SECRET_KEY` to a 256-bit random string
- [ ] Rotate all API keys (Supabase, Google Cloud, etc.)
- [ ] Enable Vercel Authentication if needed
- [ ] Set up Cloud Run IAM policies
- [ ] Enable CORS only for your Vercel domain
- [ ] Review Supabase RLS policies
- [ ] Enable rate limiting in backend
- [ ] Set up monitoring alerts

---

## Cost Optimization

### Vercel
- Free tier: 100GB bandwidth/month
- Production: $20/month (included with Pro)

### Cloud Run
- Free tier: 180,000 vCPU-seconds/month
- Estimate: ~$5-50/month depending on traffic

### Supabase
- Free tier: 500MB database + 1GB bandwidth
- Pro: $25/month

---

## Next Steps

1. **Get Credentials:**
   - Supabase Anon Key: Supabase Dashboard → Project Settings → API
   - Supabase Service Key: Same location, Service Role Key
   - Google Maps API Key: Google Cloud Console

2. **Configure Vercel:**
   ```bash
   vercel env add VITE_SUPABASE_URL
   vercel env add VITE_SUPABASE_ANON_KEY
   vercel env add VITE_BACKEND_API_URL
   ```

3. **Deploy Backend:**
   ```bash
   gcloud auth login
   gcloud run deploy raptorflow-backend --image gcr.io/raptorflow-477017/raptorflow-backend:latest --region us-central1
   ```

4. **Update Frontend:**
   Update `VITE_BACKEND_API_URL` in Vercel with your Cloud Run service URL

5. **Test:**
   - Visit your Vercel deployment
   - Check browser console for API errors
   - Verify all API endpoints respond

---

## Support

For issues:
- Vercel Docs: https://vercel.com/docs
- Cloud Run Docs: https://cloud.google.com/run/docs
- Supabase Docs: https://supabase.com/docs
- RaptorFlow Issues: GitHub Issues

