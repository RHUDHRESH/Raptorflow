# RaptorFlow Codex - Production Deployment Plan

**Target**: Google Cloud Run (Backend), Vercel (Frontend), Supabase (DB), Upstash (Redis)
**Status**: Ready for Execution

---

## 1. Pre-Deployment Checklist

### 1.1 Environment Variables
Ensure you have the following production secrets ready:

| Variable | Description | Source |
|----------|-------------|--------|
| `GOOGLE_CLOUD_PROJECT` | GCP Project ID | GCP Console |
| `SUPABASE_URL` | Database API URL | Supabase Settings |
| `SUPABASE_SERVICE_KEY` | Backend Admin Key | Supabase Settings |
| `SUPABASE_JWT_SECRET` | JWT Signing Secret | Supabase Settings |
| `REDIS_URL` | Upstash Connection String | Upstash Console |
| `SECRET_KEY` | Application Secret | Generate (`openssl rand -hex 32`) |
| `VERTEX_AI_LOCATION` | GCP Region (e.g. us-central1) | GCP Console |

### 1.2 Database Migrations
Run all pending migrations against your production Supabase instance.
```bash
# Assuming you have the CLI configured
supabase db push
```
*Note: Ensure `agent_memories` table supports vector extensions (pgvector).*

---

## 2. Backend Deployment (Google Cloud Run)

### 2.1 Build Container
Navigate to the project root and build the Docker image.
```bash
gcloud auth configure-docker
docker build -f Dockerfile.cloudrun -t gcr.io/raptorflow-477017/raptorflow-backend:latest .
```

### 2.2 Push Container
```bash
docker push gcr.io/raptorflow-477017/raptorflow-backend:latest
```

### 2.3 Deploy Service
Deploy to Cloud Run with environment variables.
```bash
gcloud run deploy raptorflow-backend \
  --image gcr.io/raptorflow-477017/raptorflow-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars "ENVIRONMENT=production" \
  --set-env-vars "SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co" \
  --set-env-vars "REDIS_URL=rediss://[YOUR_UPSTASH_URL]" \
  # Add other secrets using --set-env-vars or --set-secrets
```

### 2.4 Verify Deployment
Check the health endpoint of your new service:
```bash
curl https://[YOUR-CLOUD-RUN-URL]/health
```

---

## 3. Frontend Deployment (Vercel)

### 3.1 Configure Vercel Project
1. Import repository to Vercel.
2. Set **Framework Preset** to `Vite`.
3. Set **Root Directory** to `./` (root).

### 3.2 Set Environment Variables
Add these in Vercel Project Settings:
- `VITE_BACKEND_API_URL`: `https://[YOUR-CLOUD-RUN-URL]/api/v1`
- `VITE_SUPABASE_URL`: `https://vpwwzsanuyhpkvgorcnc.supabase.co`
- `VITE_SUPABASE_ANON_KEY`: `[YOUR_SUPABASE_ANON_KEY]`
- `VITE_ENVIRONMENT`: `production`

### 3.3 Deploy
Trigger a new deployment from the main branch.

---

## 4. Post-Deployment Verification

### 4.1 System Health
- [ ] Backend `/health` returns 200 OK.
- [ ] Redis connection is active (check logs).
- [ ] Database connection is active (check logs).

### 4.2 Functional Testing
1. **Login/Register**: Create a new user on the production frontend.
2. **Onboarding**: Complete the onboarding flow. Verify `MasterOrchestrator` triggers.
3. **Lords**: Access the Strategy Dashboard and verify `Architect`, `Strategos`, etc. load data.
4. **Real-time**: Check if WebSocket connections (e.g., `/ws/lords/herald`) stay open.

### 4.3 Monitoring
- **GCP**: Check Cloud Run metrics (Request count, Latency, CPU).
- **Supabase**: Monitor Database health and API requests.
- **Upstash**: Check Redis command usage.

---

## 5. Troubleshooting

**Issue**: Backend 500 Error on Startup
- **Fix**: Check Cloud Logging for `ImportError` or `KeyError` (missing env vars). Ensure all Lord router files were copied correctly (they are now in `backend/routers/lords/`).

**Issue**: WebSocket Disconnects
- **Fix**: Cloud Run has a default timeout. Ensure your frontend handles reconnection, or increase the timeout if needed (max 60 mins).

**Issue**: CORS Errors
- **Fix**: Ensure `BACKEND_CORS_ORIGINS` in `backend/core/config.py` includes your Vercel domain.

---

## 6. Future Roadmap
- **CI/CD**: Set up Cloud Build triggers on git push.
- **Domain**: Map custom domains to Cloud Run and Vercel.
- **Scaling**: Increase `max_instances` in Cloud Run based on load.
