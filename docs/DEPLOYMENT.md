# RaptorFlow - Deployment Guide

Complete guide for deploying RaptorFlow to production with Supabase, Vercel, and Google Cloud Platform.

---

## 🚀 Quick Deployment (30 Minutes)

###Prerequisites
- Supabase account
- Vercel account  
- Google Cloud account (with billing for backend AI features)
- Node.js 20+
- Git

### Quick Start Checklist

- [ ] Supabase project created and schema deployed
- [ ] Vercel account connected to repository
- [ ] GCP project created (optional, for backend)
- [ ] Environment variables configured
- [ ] Dependencies installed

---

## 📋 Step 1: Database Setup (Supabase) - 15 min

### 1.1 Create Supabase Project

1. Visit [app.supabase.com](https://app.supabase.com)
2. Click **New Project**
3. Configure:
   - Name: `raptorflow-prod`
   - Database Password: (secure password)
   - Region: (closest to users)
4. Wait ~2 minutes for provisioning

### 1.2 Run Database Migrations

In Supabase Dashboard → **SQL Editor**, run these files in order:

```sql
-- 1. Core workspace setup
-- Copy/paste: database/setup-workspace.sql

-- 2. Move System schema  
-- Copy/paste: database/migrations/001_move_system_schema.sql

-- 3. Assets table
-- Copy/paste: database/migrations/002_assets_table.sql

-- 4. Quests table
-- Copy/paste: database/migrations/003_quests_table.sql

-- 5. Additional core tables
-- Copy/paste: database/migrations/004_core_missing_tables.sql

-- 6. Seed capability nodes (UPDATE workspace_id first!)
-- Copy/paste: database/seed-capability-nodes.sql

-- 7. Seed maneuver types
-- Copy/paste: database/seed-maneuver-types.sql

-- 8. Row Level Security policies
-- Copy/paste: database/rls-policies.sql
```

### 1.3 Configure Workspace Function

For **development** (single workspace):

```sql
CREATE OR REPLACE FUNCTION get_user_workspace_id()
RETURNS UUID AS $$
BEGIN
  RETURN 'YOUR_DEV_WORKSPACE_ID'::uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

Generate UUID at: https://www.uuidgenerator.net/

For **production** (multi-tenant):

```sql
CREATE OR REPLACE FUNCTION get_user_workspace_id()
RETURNS UUID AS $$
BEGIN
  RETURN (
    SELECT workspace_id 
    FROM user_workspaces 
    WHERE user_id = auth.uid() 
    LIMIT 1
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 1.4 Get API Credentials

1. Navigate to **Settings** → **API**
2. Copy:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public** key (for frontend)
   - **service_role** key (for backend only, keep secret!)

### 1.5 Configure Google OAuth (Optional)

1. Go to **Authentication** → **Providers** → **Google**
2. Toggle **Enable**
3. Enter Client ID and Secret from Google Cloud Console
4. Save

For detailed OAuth setup, see `docs/GOOGLE_OAUTH_SETUP.md`

---

## 📦 Step 2: Frontend Deployment (Vercel) - 10 min

### 2.1 Connect Repository

1. Visit [vercel.com](https://vercel.com)
2. Click **Add New Project**
3. Import your Git repository
4. Configure:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### 2.2 Configure Environment Variables

In Vercel Dashboard → **Settings** → **Environment Variables**, add:

```bash
# Supabase
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ... (your anon key)

# Optional: For Vertex AI features
VITE_VERTEX_AI_API_KEY=your-vertex-ai-key

# Environment
VITE_ENVIRONMENT=production
```

### 2.3 Deploy

```bash
# Option 1: Push to main branch (auto-deploy)
git push origin main

# Option 2: Manual deploy with Vercel CLI
npm i -g vercel
vercel --prod
```

### 2.4 Configure Custom Domain (Optional)

1. In Vercel Dashboard → **Settings** → **Domains**
2. Add your domain
3. Update DNS records as instructed
4. Wait for SSL certificate provisioning

---

## 🔧 Step 3: Backend Deployment (Google Cloud Run) - Optional

Skip this if you're only using frontend features. Required for AI-powered multi-agent system.

### 3.1 Install Google Cloud SDK

```bash
# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash

# Windows: Download from https://cloud.google.com/sdk/docs/install
```

### 3.2 Initialize GCP Project

```bash
# Login
gcloud auth login

# Create project
gcloud projects create raptorflow-prod --name="RaptorFlow Production"

# Set current project
gcloud config set project raptorflow-prod

# Enable billing (required)
# Visit: https://console.cloud.google.com/billing

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  aiplatform.googleapis.com
```

### 3.3 Deploy Backend

```bash
# Navigate to backend directory
cd backend

# Build and deploy using the deployment script
chmod +x ../scripts/deploy-backend.sh
../scripts/deploy-backend.sh
```

The script will:
1. Build Docker image
2. Push to Google Container Registry
3. Deploy to Cloud Run with auto-scaling
4. Set environment variables
5. Output service URL

### 3.4 Set Backend Environment Variables

Create secrets in Google Secret Manager:

```bash
# Create secrets
echo -n "your-supabase-service-key" | gcloud secrets create SUPABASE_SERVICE_KEY --data-file=-
echo -n "your-jwt-secret" | gcloud secrets create SUPABASE_JWT_SECRET --data-file=-
echo -n "redis://your-redis-url" | gcloud secrets create REDIS_URL --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding SUPABASE_SERVICE_KEY \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### 3.5 Configure Backend Environment

Set environment variables in Cloud Run:

```bash
gcloud run services update raptorflow-backend \
  --region us-central1 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=raptorflow-prod" \
  --set-env-vars="VERTEX_AI_LOCATION=us-central1" \
  --set-env-vars="SUPABASE_URL=https://xxxxx.supabase.co"
```

---

## ✅ Step 4: Verification (5 min)

### 4.1 Check Frontend

1. Visit your Vercel URL
2. Verify pages load without errors
3. Check browser console (F12) for errors
4. Test authentication (sign up/login)

### 4.2 Check Backend (if deployed)

```bash
# Health check
curl https://your-backend-url/health

# Expected response:
# {"status": "healthy", "timestamp": "..."}

# API docs
# Visit: https://your-backend-url/docs
```

### 4.3 Check Database

```bash
# In browser console on frontend
const { data, error } = await supabase.from('capability_nodes').select('*').limit(5)
console.log(data, error)

# Should return 5 capability nodes
```

### 4.4 Test Key Features

- [ ] Sign up with Google OAuth
- [ ] Create an ICP/Cohort
- [ ] Browse Move Library (should show maneuvers)
- [ ] Create a move
- [ ] View War Room
- [ ] Check Tech Tree
- [ ] Test content creation (if backend deployed)

---

## 📊 Step 5: Monitoring & Maintenance

### Health Checks

```bash
# Frontend (Vercel)
curl https://your-app.vercel.app

# Backend (GCP)
curl https://your-backend-url/health

# Database (Supabase Dashboard)
# Check: Database → Health
```

### View Logs

```bash
# Vercel logs
vercel logs your-app.vercel.app

# GCP Cloud Run logs
gcloud run logs read raptorflow-backend --region us-central1 --limit 50

# Follow logs in real-time
gcloud run logs tail raptorflow-backend --region us-central1

# Supabase logs
# Dashboard → Logs → Select service
```

### Performance Monitoring

- **Frontend**: Vercel Analytics (automatic)
- **Backend**: GCP Cloud Monitoring
- **Database**: Supabase Dashboard → Reports
- **User Analytics**: Add PostHog or similar

---

## 🔄 CI/CD Setup

### Automatic Deployments

**Frontend (Vercel)**:
- Automatic on push to `main` branch
- Preview deployments for PRs
- Rollback via Vercel Dashboard

**Backend (GCP Cloud Build)**:

Create `.github/workflows/deploy-backend.yml`:

```yaml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: raptorflow-prod
      
      - name: Build and Deploy
        run: |
          gcloud builds submit --config cloudbuild.yaml
```

---

## 🚨 Troubleshooting

### "Supabase not configured"
- Verify `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` in Vercel
- Restart deployment after adding env vars
- Check browser console for specific errors

### "No data in Move Library"
- Verify seed data was run successfully in Supabase
- Check RLS policies are enabled
- Verify workspace_id matches in code and database

### Build failures on Vercel
- Check build logs in Vercel Dashboard
- Test build locally: `npm run build`
- Ensure all dependencies are in `package.json`

### Backend not responding
- Check Cloud Run logs for errors
- Verify all environment variables are set
- Check Redis connection (if using)
- Verify Vertex AI API is enabled

### Permission denied errors
- Check RLS policies in Supabase
- Verify `get_user_workspace_id()` function exists
- Check user authentication status
- Review table permissions

### High costs
- Review GCP billing dashboard
- Adjust Cloud Run min/max instances
- Optimize database queries
- Enable caching where possible

---

## 💰 Cost Estimates

### Development
- **Supabase**: Free tier (500MB DB, 2GB bandwidth)
- **Vercel**: Free tier (100GB bandwidth)
- **GCP**: Free tier ($300 credit for 90 days)
- **Total**: $0/month

### Production (Low Traffic)
- **Supabase**: Pro plan ~$25/month (8GB DB)
- **Vercel**: Pro plan ~$20/month (1TB bandwidth)
- **GCP Cloud Run**: ~$10-30/month (depends on usage)
- **Redis** (if needed): ~$10/month (Upstash or similar)
- **Total**: ~$65-85/month

### Production (High Traffic)
- **Supabase**: Team/Enterprise plan $100+/month
- **Vercel**: Enterprise custom pricing
- **GCP**: $100-500+/month based on usage
- **Redis**: $30+/month
- **Total**: $230-1000+/month

---

## 🔐 Security Checklist

- [ ] All `.env` files in `.gitignore`
- [ ] HTTPS enforced (automatic on Vercel/GCP)
- [ ] Supabase RLS policies enabled on all tables
- [ ] API keys stored in Secret Manager (GCP)
- [ ] Service account keys not committed to git
- [ ] CORS properly configured
- [ ] Rate limiting enabled (if applicable)
- [ ] Regular security audits: `npm audit`
- [ ] Dependencies kept up to date
- [ ] Backup strategy in place

---

## 🔄 Rollback Procedures

### Frontend (Vercel)
```bash
# List deployments
vercel list

# Promote previous deployment to production
vercel promote [deployment-url]

# Or use Vercel Dashboard → Deployments → Previous deployment → Promote
```

### Backend (GCP)
```bash
# List revisions
gcloud run revisions list --service raptorflow-backend --region us-central1

# Route traffic to previous revision
gcloud run services update-traffic raptorflow-backend \
  --to-revisions=raptorflow-backend-00002-xxx=100 \
  --region us-central1
```

### Database (Supabase)
```bash
# Create backup before migrations
supabase db dump -f backup-$(date +%Y%m%d).sql

# Restore if needed
psql -h db.xxx.supabase.co -U postgres -f backup-20231115.sql
```

---

## 📚 Additional Resources

- **Implementation Guide**: `docs/IMPLEMENTATION_GUIDE.md`
- **Google OAuth Setup**: `docs/GOOGLE_OAUTH_SETUP.md`
- **Database Setup**: `database/DATABASE_SETUP_GUIDE.md`
- **Security Guide**: `docs/SECURITY.md`
- **Architecture**: `ARCHITECTURE_DIAGRAM.txt`

---

## 📞 Support

For deployment issues:
1. Check relevant documentation above
2. Review service logs (Vercel, GCP, Supabase)
3. Check GitHub Issues
4. Contact support team

---

**Version**: 2.0  
**Last Updated**: November 2025




