# Raptorflow Deployment Quick Reference

Quick commands for deploying Raptorflow to production.

## Prerequisites Checklist

- [ ] Supabase project created and schema deployed
- [ ] Vercel account connected to repository
- [ ] GCP project created with billing enabled
- [ ] PostHog project created
- [ ] All environment variables configured
- [ ] Dependencies installed (`npm install`)

## Environment Variables

### Required for Frontend (Vercel)
```bash
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_GOOGLE_MAPS_API_KEY=
VITE_POSTHOG_KEY=
VITE_POSTHOG_HOST=https://app.posthog.com
VITE_ENVIRONMENT=production
```

### Required for Backend (GCP)
```bash
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
POSTHOG_KEY=
POSTHOG_HOST=https://app.posthog.com
NODE_ENV=production
```

## Quick Deploy

### Frontend to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod

# Or push to main branch for auto-deploy
git push origin main
```

### Backend to GCP Cloud Run

#### Option 1: Automatic (via Cloud Build)
```bash
# Push to trigger Cloud Build
git push origin main
```

#### Option 2: Manual Docker Deploy
```bash
# Authenticate
gcloud auth login
gcloud config set project raptorflow-prod

# Build and deploy
gcloud builds submit --config cloudbuild.yaml

# Or deploy directly
gcloud run deploy raptorflow \
  --image gcr.io/raptorflow-prod/raptorflow:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```

#### Option 3: Local Docker Test
```bash
# Build
docker build -t raptorflow-backend .

# Test locally
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

## Database Deployment (Supabase)

### Initial Setup
```bash
# Install Supabase CLI
npm install -g supabase

# Link to project
supabase link --project-ref your-project-ref

# Push schema
supabase db push
```

### Migrations
```bash
# Create migration
supabase migration new migration_name

# Apply migration
supabase db push

# Or apply via Supabase Dashboard SQL Editor
```

## Post-Deployment Checks

### 1. Frontend Health
```bash
# Check deployment
curl https://your-app.vercel.app

# Expected: HTML response
```

### 2. Backend Health
```bash
# Check health endpoint
curl https://raptorflow-xxxxx-uc.a.run.app/health

# Expected: {"status": "ok"}
```

### 3. Database Connection
```bash
# Test from frontend console
const { data, error } = await supabase.from('companies').select('*').limit(1)
console.log(data, error)
```

### 4. PostHog Analytics
- Visit PostHog dashboard
- Verify events are being received
- Check real-time activity

## Rollback Procedures

### Frontend (Vercel)
```bash
# List deployments
vercel list

# Rollback to previous deployment
vercel rollback [deployment-url]
```

### Backend (GCP)
```bash
# List revisions
gcloud run revisions list --service raptorflow --region us-central1

# Rollback to previous revision
gcloud run services update-traffic raptorflow \
  --to-revisions=raptorflow-00002-xxx=100 \
  --region us-central1
```

### Database (Supabase)
```bash
# Revert last migration
supabase db reset

# Or manually via SQL Editor
```

## Monitoring Commands

### View Logs
```bash
# Vercel logs
vercel logs [deployment-url]

# GCP Cloud Run logs
gcloud run logs read raptorflow --region us-central1 --limit 50

# Follow logs in real-time
gcloud run logs tail raptorflow --region us-central1

# Docker logs
docker-compose logs -f
```

### Check Resource Usage
```bash
# GCP Cloud Run metrics
gcloud run services describe raptorflow --region us-central1

# Supabase usage
# Check dashboard: Database > Usage
```

## Scaling Configuration

### GCP Cloud Run Auto-scaling
Edit `app.yaml`:
```yaml
automatic_scaling:
  min_instances: 2
  max_instances: 20
  target_cpu_utilization: 0.65
```

Deploy:
```bash
gcloud app deploy app.yaml
```

## Common Issues

### Issue: "Missing environment variables"
**Solution:** Check all required variables are set in deployment platform

```bash
# Vercel - check in dashboard or:
vercel env ls

# GCP - check secrets:
gcloud secrets list
```

### Issue: CORS errors
**Solution:** Add CORS headers in backend or configure in GCP

```bash
# Update Cloud Run service
gcloud run services update raptorflow \
  --set-env-vars="CORS_ORIGIN=https://your-app.vercel.app" \
  --region us-central1
```

### Issue: Database connection timeout
**Solution:**
1. Check Supabase project is active
2. Verify connection pooling settings
3. Check RLS policies aren't blocking queries

### Issue: High costs
**Solution:**
1. Review GCP usage in Billing dashboard
2. Adjust min_instances in auto-scaling
3. Optimize database queries
4. Enable Vercel edge caching

## Security Checklist

- [ ] All `.env` files in `.gitignore`
- [ ] HTTPS enforced on all domains
- [ ] Supabase RLS policies enabled
- [ ] API keys rotated regularly
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Monitoring alerts configured
- [ ] Backup strategy in place

## Performance Optimization

### Frontend
```bash
# Check bundle size
npm run build
# Review dist/ folder size

# Optimize if needed
npm install -D vite-plugin-compression
```

### Backend
```bash
# Enable Cloud CDN
gcloud compute backend-services update raptorflow \
  --enable-cdn \
  --global
```

### Database
- Add indexes for frequently queried columns
- Use connection pooling
- Monitor slow queries in Supabase Dashboard

## Backup and Recovery

### Database Backups
```bash
# Supabase provides automatic daily backups
# Manual backup:
supabase db dump -f backup.sql

# Restore:
supabase db reset
psql -h db.xxx.supabase.co -U postgres < backup.sql
```

### Code Backups
```bash
# Git is your backup
# Tag releases:
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0
```

## Update Deployment

```bash
# 1. Make changes locally
git add .
git commit -m "feat: new feature"

# 2. Run tests (when available)
npm test

# 3. Push to deploy
git push origin main

# Both Vercel and GCP will auto-deploy via their respective CI/CD
```

## Cost Monitoring

```bash
# GCP billing
gcloud billing accounts list
gcloud billing projects describe raptorflow-prod

# Set budget alerts in GCP Console
```

## Emergency Contacts

- **GCP Support**: Cloud Console > Support
- **Vercel Support**: dashboard.vercel.com/support
- **Supabase Support**: app.supabase.com/support
- **PostHog Support**: app.posthog.com/support

---

For detailed setup instructions, see [INFRASTRUCTURE_SETUP.md](./INFRASTRUCTURE_SETUP.md)
