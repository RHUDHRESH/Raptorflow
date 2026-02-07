# ☁️ Cloud Run Backend Deployment Guide

## Current Status

**Google Cloud Project**: `raptorflow-477017`
**Region**: `us-central1`
**Current Services**: 0 deployed

---

## Prerequisites

Before deploying, ensure you have:

✅ **Google Cloud SDK** installed: https://cloud.google.com/sdk/docs/install
✅ **Docker Desktop** installed: https://www.docker.com/products/docker-desktop
✅ **Service credentials** from Supabase
✅ **GCP project access** to raptorflow-477017

---

## Step 1: Authenticate with Google Cloud

Run on your local machine:

```bash
# Login to Google Cloud
gcloud auth login

# Set project
gcloud config set project raptorflow-477017

# Verify authentication
gcloud auth list
```

---

## Step 2: Enable Required APIs

```bash
# Enable Cloud Run
gcloud services enable run.googleapis.com

# Enable Container Registry
gcloud services enable containerregistry.googleapis.com

# Enable Cloud Build
gcloud services enable cloudbuild.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled | grep -E "run|container|cloudbuild"
```

---

## Step 3: Create Backend Credentials File

Create `backend/.env.prod` in your Raptorflow directory:

```bash
# Windows: Create file in C:\Users\hp\OneDrive\Desktop\Raptorflow\backend\.env.prod
# Mac/Linux: Create file in ~/Raptorflow/backend/.env.prod

# Add these contents:
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING

# Google Cloud
GOOGLE_CLOUD_PROJECT=raptorflow-477017
VERTEX_AI_LOCATION=us-central1

# Supabase (get from https://app.supabase.com → Settings → API)
SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
SUPABASE_SERVICE_KEY=PASTE_YOUR_SERVICE_ROLE_KEY_HERE
SUPABASE_JWT_SECRET=PASTE_YOUR_JWT_SECRET_HERE

# Redis (optional - for local dev only)
REDIS_URL=redis://localhost:6379/0

# Security (MUST CHANGE TO STRONG RANDOM STRING)
SECRET_KEY=GENERATE_A_STRONG_32_CHAR_RANDOM_STRING_HERE
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

---

## Step 4: Build Docker Image

```bash
# Navigate to Raptorflow directory
cd C:\Users\hp\OneDrive\Desktop\Raptorflow

# Build the image
docker build -f Dockerfile.cloudrun -t gcr.io/raptorflow-477017/raptorflow-backend:latest .

# This will:
# 1. Download Python 3.11-slim base image
# 2. Install dependencies from requirements-prod.txt
# 3. Copy your backend code
# 4. Create non-root user
# 5. Set health checks
# 6. Create optimized final image (~800MB)

# Expected output:
# Successfully tagged gcr.io/raptorflow-477017/raptorflow-backend:latest
```

**Time**: 5-10 minutes (first time, slower due to downloads)

---

## Step 5: Configure Docker Authentication

```bash
# Configure Docker to push to Google Container Registry
gcloud auth configure-docker

# You should see:
# Adding credentials for gcr.io
# Credentials configured for all Docker repositories
```

---

## Step 6: Push Image to Container Registry

```bash
# Push the image
docker push gcr.io/raptorflow-477017/raptorflow-backend:latest

# This uploads your image to Google Cloud
# Expected output:
# The push refers to repository [gcr.io/raptorflow-477017/raptorflow-backend]
# latest: digest: sha256:xxxxxxx size: xxxxx
```

**Time**: 3-5 minutes

---

## Step 7: Deploy to Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy raptorflow-backend \
  --image gcr.io/raptorflow-477017/raptorflow-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 3600 \
  --max-instances 10 \
  --min-instances 1 \
  --env-vars-file backend/.env.prod

# Expected output:
# Deploying container to Cloud Run service [raptorflow-backend] in project [raptorflow-477017] region [us-central1]
# ⠏ Creating Revision...
# ✓ Revision deployed successfully. Service URL: https://raptorflow-backend-xxxxx.run.app
```

**Time**: 2-5 minutes

---

## Step 8: Verify Deployment

```bash
# Get service details
gcloud run services describe raptorflow-backend --region us-central1

# You should see:
# ✓ Service URL: https://raptorflow-backend-xxxxx.run.app

# Test health endpoint
curl https://raptorflow-backend-xxxxx.run.app/health

# Expected response:
# {"status":"healthy","timestamp":"2025-11-24T..."}

# View deployment logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=raptorflow-backend" --limit 50 --format json
```

---

## Using Automated Script (Easier)

Instead of manual steps, run:

**Windows:**
```bash
deploy-backend.cmd
```

**Mac/Linux:**
```bash
bash deploy-backend.sh
```

This script does all the above steps automatically!

---

## Troubleshooting

### Issue: "docker: command not found"
**Solution**: Install Docker Desktop from https://www.docker.com/products/docker-desktop

### Issue: "gcloud: command not found"
**Solution**: Install Google Cloud SDK from https://cloud.google.com/sdk/docs/install

### Issue: "Permission denied" or authentication errors
**Solution**:
```bash
gcloud auth login
gcloud config set project raptorflow-477017
```

### Issue: Docker build fails
**Solution**:
- Ensure Docker Desktop is running
- Check available disk space (need 5GB minimum)
- Try: `docker system prune -a` to clean up

### Issue: Image push fails
**Solution**: Configure Docker auth:
```bash
gcloud auth configure-docker
```

### Issue: Cloud Run deployment fails
**Solution**: Check logs:
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 100 --format json
```

### Issue: Service returns 500 errors
**Solution**: Check environment variables:
```bash
gcloud run services describe raptorflow-backend --region us-central1
```

Verify all env vars are set correctly in `backend/.env.prod`

---

## Monitoring After Deployment

### View Live Logs
```bash
# Stream logs in real-time
gcloud logging tail projects/raptorflow-477017/logs/cloud.googleapis.com%2Fcloud-run-resource --limit 50
```

### Check Service Status
```bash
# Get service info
gcloud run services describe raptorflow-backend --region us-central1

# View revisions
gcloud run revisions list --region us-central1 --service raptorflow-backend
```

### Update Service
```bash
# To update with new image
gcloud run deploy raptorflow-backend \
  --image gcr.io/raptorflow-477017/raptorflow-backend:latest \
  --region us-central1 \
  --env-vars-file backend/.env.prod
```

---

## Scaling Configuration

### Auto-Scaling
```bash
# Update auto-scaling
gcloud run services update raptorflow-backend \
  --min-instances 1 \
  --max-instances 10 \
  --region us-central1
```

Current settings:
- **Min Instances**: 1 (always running)
- **Max Instances**: 10 (auto-scale up to handle traffic)
- **Memory**: 1Gi per instance
- **CPU**: 1 vCPU per instance
- **Timeout**: 3600 seconds (1 hour for long tasks)
- **Concurrency**: Default (80 requests per instance)

---

## Cost Estimation

**Cloud Run Pricing**:
- **Compute**: $0.000025 per vCPU-second
- **Requests**: $0.40 per million requests
- **Networking**: $0.12 per GB egress

**Example Monthly Cost** (assuming moderate traffic):
- 10 hours/day at 2 instances = ~$20/month
- 1 million API requests = ~$0.40/month
- 10GB data egress = ~$1.20/month
- **Total**: ~$21.60/month

**Free Tier**: 180,000 vCPU-seconds/month (usually covers testing)

---

## Security Considerations

✅ **Non-root user**: Container runs as `raptorflow:1000`
✅ **Health checks**: Auto-restarts failing instances
✅ **HTTPS**: Automatic SSL/TLS
✅ **Unauthenticated**: Set to allow for testing (update if needed)
✅ **Secret management**: Use Cloud Secret Manager for sensitive data
✅ **Environment variables**: Isolated per service

---

## Quick Commands Reference

```bash
# Login and setup
gcloud auth login
gcloud config set project raptorflow-477017

# Build and push
docker build -f Dockerfile.cloudrun -t gcr.io/raptorflow-477017/raptorflow-backend:latest .
docker push gcr.io/raptorflow-477017/raptorflow-backend:latest

# Deploy
gcloud run deploy raptorflow-backend \
  --image gcr.io/raptorflow-477017/raptorflow-backend:latest \
  --region us-central1 \
  --env-vars-file backend/.env.prod

# View logs
gcloud logging tail projects/raptorflow-477017/logs/cloud.googleapis.com%2Fcloud-run-resource

# Get service URL
gcloud run services describe raptorflow-backend --region us-central1 --format="value(status.url)"

# Delete service (if needed)
gcloud run services delete raptorflow-backend --region us-central1
```

---

## Next Steps After Deployment

1. **Get Service URL**: From deployment output or use command above
2. **Test Health Endpoint**: `curl https://your-service-url/health`
3. **Update Frontend**: Set `VITE_BACKEND_API_URL` in Vercel to your service URL
4. **Test API Calls**: Frontend should now reach backend
5. **Monitor Logs**: Keep logs open while testing
6. **Set Up Alerts**: Configure Cloud Monitoring for production

---

## Support

- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Troubleshooting**: https://cloud.google.com/run/docs/troubleshooting
- **Logging**: https://cloud.google.com/logging/docs
- **Pricing**: https://cloud.google.com/run/pricing

---

## Completion Checklist

- [ ] Created `backend/.env.prod` with all credentials
- [ ] Authenticated with Google Cloud
- [ ] Enabled required APIs
- [ ] Built Docker image successfully
- [ ] Pushed image to Container Registry
- [ ] Deployed to Cloud Run
- [ ] Service URL obtained
- [ ] Health check passing (returns 200)
- [ ] Logs accessible and showing info level
- [ ] Ready to connect frontend

**Once all checked**: Your backend is ready for production! 🚀

