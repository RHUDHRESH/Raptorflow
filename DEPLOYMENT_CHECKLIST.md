# 📋 RaptorFlow Deployment Checklist

Complete this checklist to successfully deploy your RaptorFlow application.

## Phase 1: Prerequisites ✅ (5 minutes)

### Software Installation
- [ ] Node.js 20+ installed: `node --version`
- [ ] npm 10+ installed: `npm --version`
- [ ] Docker Desktop installed: `docker --version`
- [ ] Google Cloud SDK installed: `gcloud --version`
- [ ] Git installed: `git --version`
- [ ] Vercel CLI installed: `vercel --version`

### Accounts Created
- [ ] Vercel account (https://vercel.com)
- [ ] Google Cloud account with billing enabled
- [ ] Supabase account (already set up: vpwwzsanuyhpkvgorcnc)
- [ ] GitHub account with repo access

### Local Setup
- [ ] Cloned/downloaded RaptorFlow repository
- [ ] Current directory: `C:\Users\hp\OneDrive\Desktop\Raptorflow`
- [ ] All deployment scripts are present:
  - [ ] `deploy-frontend.cmd` / `deploy-frontend.sh`
  - [ ] `deploy-backend.cmd` / `deploy-backend.sh`
  - [ ] `DEPLOYMENT_GUIDE.md`
  - [ ] `QUICK_START_DEPLOYMENT.md`

---

## Phase 2: Collect Credentials 🔐 (10 minutes)

### Supabase Credentials
- [ ] Go to https://app.supabase.com
- [ ] Select project: "Raptorflow"
- [ ] Go to Settings → API → Copy anon key
  - Save as: `VITE_SUPABASE_ANON_KEY`
- [ ] Go to Settings → API → Copy service_role key
  - Save as: `SUPABASE_SERVICE_KEY`
- [ ] Go to Settings → Database → Copy JWT Secret
  - Save as: `SUPABASE_JWT_SECRET`
- [ ] Copy URL: `https://vpwwzsanuyhpkvgorcnc.supabase.co`
  - Save as: `VITE_SUPABASE_URL` and `SUPABASE_URL`

### Google Cloud Credentials
- [ ] Go to https://console.cloud.google.com
- [ ] Select project: `raptorflow-477017`
- [ ] Enable Cloud Run API
  - [ ] Go to APIs & Services → Enable APIs
  - [ ] Search "Cloud Run" → Enable
- [ ] Enable Container Registry
  - [ ] Search "Container Registry" → Enable
- [ ] Create service account (optional, for gcloud auth):
  - [ ] Go to Service Accounts
  - [ ] Create a new service account
  - [ ] Grant "Cloud Run Admin" role
  - [ ] Create and download JSON key

### Optional API Keys
- [ ] Google Maps API Key (optional)
  - URL: https://console.cloud.google.com/google/maps-apis
- [ ] PostHog API Key (optional, for analytics)
  - URL: https://app.posthog.com

---

## Phase 3: Prepare Environment Variables 📝 (5 minutes)

### Create .env files

**Root .env.local** (for local development):
```
VITE_SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
VITE_SUPABASE_ANON_KEY=[paste from Supabase]
VITE_BACKEND_API_URL=http://localhost:8000/api/v1
VITE_ENVIRONMENT=development
```

**backend/.env.prod** (for Cloud Run production):
```
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING
GOOGLE_CLOUD_PROJECT=raptorflow-477017
VERTEX_AI_LOCATION=us-central1
SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
SUPABASE_SERVICE_KEY=[paste service role key from Supabase]
SUPABASE_JWT_SECRET=[paste JWT secret from Supabase]
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=[generate strong random 32+ character string]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

### Checklist
- [ ] Created `.env.local` in project root
- [ ] Created `backend/.env.prod` in backend directory
- [ ] All required variables filled in
- [ ] Secret keys are strong and random
- [ ] `.env` files are in `.gitignore`

---

## Phase 4: Deploy Frontend to Vercel 🎨 (5 minutes)

### Option A: Automated Script
```bash
# Windows
deploy-frontend.cmd

# Mac/Linux
bash deploy-frontend.sh
```

### Option B: Manual Deployment
```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Link to Vercel project
vercel link

# 3. Set environment variables
vercel env add VITE_SUPABASE_URL "https://vpwwzsanuyhpkvgorcnc.supabase.co"
vercel env add VITE_SUPABASE_ANON_KEY "your_anon_key"
vercel env add VITE_BACKEND_API_URL "http://localhost:8000/api/v1"  # Update later

# 4. Deploy
vercel deploy --prod
```

### Verification
- [ ] Vercel project linked
- [ ] Environment variables set in Vercel Dashboard
- [ ] Build succeeds without errors
- [ ] Frontend URL available: `https://your-project.vercel.app`
- [ ] Frontend loads in browser
- [ ] No console errors in browser DevTools

---

## Phase 5: Deploy Backend to Cloud Run ☁️ (10 minutes)

### Authenticate with Google Cloud
```bash
gcloud auth login
gcloud config set project raptorflow-477017
```

- [ ] Authenticated with Google Cloud
- [ ] Project set to `raptorflow-477017`

### Automated Deployment
```bash
# Windows
deploy-backend.cmd

# Mac/Linux
bash deploy-backend.sh
```

### Manual Deployment Steps
```bash
# 1. Build Docker image
docker build -f Dockerfile.cloudrun -t gcr.io/raptorflow-477017/raptorflow-backend:latest .

# 2. Push to Google Container Registry
docker push gcr.io/raptorflow-477017/raptorflow-backend:latest

# 3. Deploy to Cloud Run
gcloud run deploy raptorflow-backend \
  --image gcr.io/raptorflow-477017/raptorflow-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 3600 \
  --max-instances 10 \
  --env-vars-file backend/.env.prod
```

### Verification
- [ ] Docker image built successfully
- [ ] Image pushed to Container Registry
- [ ] Cloud Run service created
- [ ] Service URL obtained: `https://raptorflow-backend-xxxx.run.app`
- [ ] Health check passes: `curl https://service-url/health`
- [ ] No errors in Cloud Run logs

---

## Phase 6: Connect Frontend to Backend 🔗 (2 minutes)

### Update Backend URL in Frontend

1. Copy Cloud Run service URL from Phase 5
2. Go to Vercel Dashboard → Project → Settings → Environment Variables
3. Update `VITE_BACKEND_API_URL`:
   ```
   https://raptorflow-backend-xxxx.run.app/api/v1
   ```
4. Trigger redeploy:
   ```bash
   git push origin main
   ```

### Checklist
- [ ] Copied Cloud Run service URL
- [ ] Updated `VITE_BACKEND_API_URL` in Vercel
- [ ] Redeployed frontend
- [ ] Frontend can reach backend API

---

## Phase 7: Test Full Application 🧪 (10 minutes)

### Frontend Tests
- [ ] Visit Vercel deployment URL
- [ ] Page loads without errors
- [ ] No console errors (F12)
- [ ] Navigation works
- [ ] Forms load properly

### Backend Tests
```bash
# Test health endpoint
curl https://raptorflow-backend-xxxx.run.app/health

# Test API endpoint
curl -X GET https://raptorflow-backend-xxxx.run.app/api/v1/health
```

- [ ] Health endpoint responds with 200
- [ ] API endpoints respond correctly
- [ ] No 500 errors in logs

### Database Tests
- [ ] Can query Supabase from backend
- [ ] Frontend can authenticate
- [ ] Data persists correctly

### Integration Tests
- [ ] Frontend sends requests to backend
- [ ] Backend receives requests from frontend
- [ ] CORS headers correct
- [ ] Responses include proper data

---

## Phase 8: Security Hardening 🔒 (5 minutes)

### Review Security Configuration
- [ ] Changed `SECRET_KEY` from default
- [ ] Vercel environment is production
- [ ] Debug mode disabled (`DEBUG=False`)
- [ ] CORS whitelist configured
- [ ] No sensitive data in logs
- [ ] API keys rotated
- [ ] HTTPS enforced

### Database Security
- [ ] Row-Level Security (RLS) enabled
- [ ] RLS policies configured
- [ ] Service key has appropriate permissions
- [ ] Anon key has restricted permissions
- [ ] No public access to sensitive tables

### Cloud Run Security
- [ ] Health checks configured
- [ ] Non-root user running container
- [ ] Resource limits set (1GB memory)
- [ ] Auto-scaling configured (1-10 instances)
- [ ] Logs enabled for audit

---

## Phase 9: Monitoring Setup 📊 (5 minutes)

### Cloud Run Monitoring
```bash
# View live logs
gcloud logging tail projects/raptorflow-477017/logs/cloud.googleapis.com%2Fcloud-run-resource

# View error logs
gcloud logging read "severity=ERROR" --limit 20
```

- [ ] Set up log alerts in Google Cloud
- [ ] Enable performance monitoring
- [ ] Configure error notifications
- [ ] Test log queries work

### Vercel Monitoring
- [ ] Enable Analytics in Vercel Dashboard
- [ ] Monitor deployment status
- [ ] Set up error tracking
- [ ] Review performance metrics

### Supabase Monitoring
- [ ] Check database logs
- [ ] Monitor API usage
- [ ] Review RLS policy violations
- [ ] Check backup status

---

## Phase 10: Documentation & Handoff 📚 (5 minutes)

### Generate Documentation
- [ ] Review `DEPLOYMENT_GUIDE.md`
- [ ] Review `QUICK_START_DEPLOYMENT.md`
- [ ] Note down all service URLs
- [ ] Document credentials location (secure vault)
- [ ] Create deployment runbook

### Team Communication
- [ ] Share Vercel project access
- [ ] Share Google Cloud project access
- [ ] Share Supabase dashboard access
- [ ] Document deployment process
- [ ] Train team on monitoring

### Backup & Disaster Recovery
- [ ] Download Supabase backup
- [ ] Document recovery procedures
- [ ] Test rollback process
- [ ] Create incident response plan

---

## Phase 11: Post-Deployment (Ongoing)

### Daily Tasks
- [ ] Monitor error rates
- [ ] Check API latency
- [ ] Review logs for issues
- [ ] Test critical flows

### Weekly Tasks
- [ ] Review deployment metrics
- [ ] Check for security updates
- [ ] Test backup restoration
- [ ] Update documentation

### Monthly Tasks
- [ ] Performance optimization review
- [ ] Cost analysis
- [ ] Security audit
- [ ] Dependency updates

---

## 🎉 Completion Summary

When all checkboxes are complete:

✅ Frontend deployed to Vercel
✅ Backend deployed to Cloud Run
✅ Database configured in Supabase
✅ Services connected and communicating
✅ Security hardened across all layers
✅ Monitoring configured
✅ Team trained and equipped

**Status: PRODUCTION READY** 🚀

---

## 📞 Troubleshooting During Deployment

### Issue: Docker build fails
**Solution**: Ensure Docker Desktop is running, then retry build

### Issue: Cloud Run deployment fails
**Solution**: Check `backend/.env.prod` exists and has all required variables

### Issue: Frontend can't reach backend
**Solution**: Verify `VITE_BACKEND_API_URL` is correctly set and backend is running

### Issue: Database connection fails
**Solution**: Verify Supabase credentials in `backend/.env.prod`

### Issue: CORS errors
**Solution**: Add your Vercel URL to CORS whitelist in FastAPI backend

For more help, see `DEPLOYMENT_GUIDE.md`

---

## ✨ You're All Set!

Your RaptorFlow application is ready for production deployment. Follow this checklist step-by-step and you'll have a fully deployed, scalable, and secure application in under an hour!

**Questions? Check the deployment guides or contact support.**

