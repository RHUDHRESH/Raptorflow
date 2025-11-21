# Raptorflow Infrastructure Setup Guide

This guide covers the complete infrastructure setup for Raptorflow with **Supabase** (database), **Vercel** (frontend), **GCP** (backend), and **PostHog** (monitoring).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Supabase Setup](#supabase-setup)
3. [Vercel Setup](#vercel-setup)
4. [GCP Setup](#gcp-setup)
5. [PostHog Setup](#posthog-setup)
6. [Local Development](#local-development)
7. [Environment Variables](#environment-variables)
8. [Deployment](#deployment)

---

## Prerequisites

- Node.js 20+ installed
- npm or yarn package manager
- Git
- Docker and Docker Compose (for local backend development)
- GCP account with billing enabled
- Supabase account
- Vercel account
- PostHog account

---

## Supabase Setup

### 1. Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project" and create a new organization
3. Create a new project:
   - Choose a name (e.g., "raptorflow-prod")
   - Set a secure database password
   - Select a region close to your users
   - Wait for the project to be provisioned (~2 minutes)

### 2. Set Up Database Schema

1. In Supabase Dashboard, go to **SQL Editor**
2. Create a new query and run the schema from `database/schema.sql`:

```sql
-- See database/schema.sql for the complete schema
-- Run the entire schema to create all tables
```

3. Verify tables are created in **Table Editor**

### 3. Configure Row Level Security (RLS)

1. Go to **Authentication** > **Policies**
2. Enable RLS for all tables
3. Run the RLS policies from `database/schema.sql`

### 4. Get API Credentials

1. Go to **Settings** > **API**
2. Copy the following:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **Anon Public Key** (safe for client-side use)
   - **Service Role Key** (keep secret, backend only)

---

## Vercel Setup

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Connect Repository

1. Go to [https://vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your Git repository
4. Configure project:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3. Configure Environment Variables

In Vercel Dashboard > Settings > Environment Variables, add:

```
VITE_SUPABASE_URL=<your_supabase_project_url>
VITE_SUPABASE_ANON_KEY=<your_supabase_anon_key>
VITE_GOOGLE_MAPS_API_KEY=<your_google_maps_api_key>
VITE_POSTHOG_KEY=<your_posthog_project_key>
VITE_POSTHOG_HOST=https://app.posthog.com
VITE_ENVIRONMENT=production
```

### 4. Deploy

```bash
vercel --prod
```

Or push to your main branch for automatic deployment.

---

## GCP Setup

### 1. Install Google Cloud SDK

```bash
# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash

# Windows
# Download from https://cloud.google.com/sdk/docs/install
```

### 2. Initialize GCP Project

```bash
# Login
gcloud auth login

# Create new project
gcloud projects create raptorflow-prod --name="Raptorflow Production"

# Set current project
gcloud config set project raptorflow-prod

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  compute.googleapis.com
```

### 3. Set Up Cloud Build

1. Go to **Cloud Build** > **Triggers**
2. Click "Create Trigger"
3. Configure:
   - **Name**: `deploy-raptorflow`
   - **Event**: Push to branch
   - **Source**: Your Git repository
   - **Branch**: `^main$`
   - **Configuration**: Cloud Build configuration file
   - **Location**: `cloudbuild.yaml`

4. Add substitution variables:
   - `_REGION`: `us-central1`
   - `_SUPABASE_URL`: Your Supabase URL
   - `_SUPABASE_ANON_KEY`: Your Supabase anon key
   - `_SUPABASE_SERVICE_KEY`: Your Supabase service key
   - `_GOOGLE_MAPS_API_KEY`: Your Google Maps key
   - `_POSTHOG_KEY`: Your PostHog key
   - `_POSTHOG_HOST`: `https://app.posthog.com`

### 4. Manual Docker Deployment

For local testing or manual deployment:

```bash
# Build the image
docker build -t raptorflow-backend .

# Test locally
docker run -p 3000:3000 --env-file .env raptorflow-backend

# Or use docker-compose
docker-compose up -d

# Push to GCP Container Registry
docker tag raptorflow-backend gcr.io/raptorflow-prod/raptorflow:latest
docker push gcr.io/raptorflow-prod/raptorflow:latest

# Deploy to Cloud Run
gcloud run deploy raptorflow \
  --image gcr.io/raptorflow-prod/raptorflow:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "SUPABASE_URL=$SUPABASE_URL,SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_KEY"
```

### 5. Set Up Load Balancing (Optional)

For production with custom domain:

```bash
# Reserve static IP
gcloud compute addresses create raptorflow-ip --global

# Create load balancer (follow GCP docs for SSL setup)
```

---

## PostHog Setup

### 1. Create PostHog Account

1. Go to [https://posthog.com](https://posthog.com) or self-host
2. Create a new organization
3. Create a new project: "Raptorflow Production"

### 2. Get Project Key

1. In PostHog Dashboard, go to **Settings** > **Project**
2. Copy your **Project API Key**
3. Note the **API Host** (usually `https://app.posthog.com`)

### 3. Configure Events

PostHog is already integrated in the codebase. It will track:
- Page views (automatic)
- Campaign actions
- OODA loop iterations
- Maneuver selections
- Capability unlocks
- Custom events

See `src/lib/posthog.ts` for all tracking methods.

### 4. Set Up Dashboards

1. Create dashboard for **User Engagement**
2. Create dashboard for **Campaign Performance**
3. Create dashboard for **Feature Usage**
4. Set up alerts for critical events

---

## Local Development

### 1. Clone Repository

```bash
git clone https://github.com/your-org/raptorflow.git
cd raptorflow
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env.local

# Edit .env.local with your credentials
nano .env.local
```

### 4. Run Supabase Locally (Optional)

```bash
# Install Supabase CLI
npm install -g supabase

# Initialize Supabase
supabase init

# Start local Supabase
supabase start

# The local Supabase will be available at:
# API URL: http://localhost:54321
# Studio URL: http://localhost:54323
```

### 5. Start Development Server

```bash
npm run dev
```

Visit `http://localhost:5173`

### 6. Run Backend Locally with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Environment Variables

### Frontend (.env.local)

```bash
# Supabase
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Google Maps
VITE_GOOGLE_MAPS_API_KEY=AIzaSy...

# PostHog
VITE_POSTHOG_KEY=phc_xxx...
VITE_POSTHOG_HOST=https://app.posthog.com

# Environment
VITE_ENVIRONMENT=development
```

### Backend (.env)

```bash
# Node
NODE_ENV=production

# Supabase (backend uses service key for privileged operations)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# PostHog
POSTHOG_KEY=phc_xxx...
POSTHOG_HOST=https://app.posthog.com
```

---

## Deployment

### Frontend (Vercel)

**Automatic Deployment:**
```bash
# Push to main branch
git push origin main
# Vercel will automatically build and deploy
```

**Manual Deployment:**
```bash
vercel --prod
```

### Backend (GCP Cloud Run)

**Via Cloud Build (Recommended):**
```bash
# Push to main branch triggers Cloud Build
git push origin main
```

**Manual Deployment:**
```bash
# Build and push
gcloud builds submit --config cloudbuild.yaml

# Or using Docker directly
docker build -t gcr.io/raptorflow-prod/raptorflow:latest .
docker push gcr.io/raptorflow-prod/raptorflow:latest
gcloud run deploy raptorflow \
  --image gcr.io/raptorflow-prod/raptorflow:latest \
  --region us-central1
```

### Database Migrations (Supabase)

```bash
# Create migration
supabase migration new add_new_feature

# Edit migration file in supabase/migrations/

# Apply migration
supabase db push

# Or apply via Supabase Dashboard SQL Editor
```

---

## Monitoring and Maintenance

### Health Checks

- **Frontend**: Vercel provides automatic monitoring
- **Backend**: Health endpoint at `/health`
- **Database**: Supabase Dashboard > Database > Health

### Logs

```bash
# GCP Cloud Run logs
gcloud run logs read raptorflow --region us-central1 --limit 50

# Follow logs in real-time
gcloud run logs tail raptorflow --region us-central1

# Docker logs
docker-compose logs -f backend
```

### PostHog Monitoring

1. Track user engagement in **PostHog Dashboard**
2. Set up alerts for critical events
3. Monitor feature adoption
4. Analyze user funnels

### Scaling

**Frontend (Vercel):**
- Automatic scaling included
- CDN distribution global

**Backend (GCP Cloud Run):**
- Automatic scaling (1-10 instances)
- Adjust in `app.yaml`:
  ```yaml
  automatic_scaling:
    min_instances: 1
    max_instances: 20
  ```

**Database (Supabase):**
- Monitor usage in Dashboard
- Upgrade plan as needed
- Set up read replicas for scaling

---

## Troubleshooting

### Supabase Connection Issues

```bash
# Test connection
curl https://your-project.supabase.co/rest/v1/

# Check RLS policies if getting 403 errors
# Verify anon key is correct
```

### Vercel Build Failures

```bash
# Check build logs in Vercel Dashboard
# Ensure all environment variables are set
# Test build locally:
npm run build
```

### GCP Deployment Issues

```bash
# Check Cloud Build logs
gcloud builds log <build-id>

# Check Cloud Run logs
gcloud run logs read raptorflow --region us-central1

# Test Docker image locally
docker run -p 3000:3000 gcr.io/raptorflow-prod/raptorflow:latest
```

### PostHog Not Tracking

- Check browser console for errors
- Verify VITE_POSTHOG_KEY is set
- Check PostHog project settings
- Ensure PostHog is not blocked by ad blockers

---

## Security Best Practices

1. **Never commit .env files** - they're in .gitignore
2. **Use secret management** - GCP Secret Manager for production secrets
3. **Enable RLS** - All Supabase tables should have RLS policies
4. **Use HTTPS only** - Enforced in Vercel and Cloud Run
5. **Rotate keys regularly** - Update API keys every 90 days
6. **Monitor logs** - Set up alerts for suspicious activity
7. **Keep dependencies updated** - Run `npm audit` regularly

---

## Cost Estimation

### Development/Testing
- **Supabase**: Free tier (500MB database, 50MB file storage)
- **Vercel**: Free tier (100GB bandwidth)
- **GCP**: Free tier ($300 credit for 90 days)
- **PostHog**: Free tier (1M events/month)
- **Total**: $0/month

### Production (Low Traffic)
- **Supabase**: Pro plan $25/month (8GB database)
- **Vercel**: Pro plan $20/month (1TB bandwidth)
- **GCP Cloud Run**: ~$10-50/month (depends on traffic)
- **PostHog**: Free or $0.00045/event after 1M
- **Total**: ~$55-95/month

### Production (High Traffic)
- **Supabase**: Team plan or higher
- **Vercel**: Enterprise
- **GCP**: Based on usage
- **PostHog**: Scale plan
- **Total**: $500-2000+/month

---

## Next Steps

1. ✅ Set up Supabase project and database
2. ✅ Configure Vercel deployment
3. ✅ Set up GCP project and Cloud Run
4. ✅ Configure PostHog analytics
5. 🔄 Implement backend API endpoints
6. 🔄 Connect frontend to Supabase
7. 🔄 Test end-to-end functionality
8. 🔄 Set up CI/CD pipeline
9. 🔄 Configure monitoring and alerts
10. 🚀 Deploy to production

---

## Support

For issues or questions:
- Documentation: [Your docs URL]
- Repository: [Your GitHub URL]
- Email: support@raptorflow.com
