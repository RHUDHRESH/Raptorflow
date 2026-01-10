# 🚀 RAPTORFLOW COMPLETE GCP SETUP GUIDE

## 🏗️ Architecture Overview

```
┌─────────────────┐
│   WFD Frontend   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   GCP Cloud Run │  ← Backend Service
└─────────────────┘
         │
    ┌────┼────┐
    ▼    │    ▼
┌───────┐ ┌───────┐ ┌──────────┐
│  GCS  │ │ Redis │ │ Vertex AI │
└───────┘ └───────┘ └──────────┘
    │         │         │
    └─────────┴─────────┘
┌─────────────────────────────┐
│      Supabase PostgreSQL      │
└─────────────────────────────┘
```

## 📋 Prerequisites

1. **Google Cloud SDK**
   ```bash
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   ```

2. **Terraform**
   ```bash
   # macOS/Linux
   brew install terraform

   # Windows
   choco install terraform
   ```

3. **Docker**
   ```bash
   # Install Docker Desktop
   ```

## 🔧 Step 1: GCP Project Setup

### 1.1 Run Setup Script
```bash
cd gcp/scripts
chmod +x setup-gcp.sh
./setup-gcp.sh
```

### 1.2 Manual Setup (if script fails)
```bash
# Set project
gcloud config set project raptorflow-prod

# Enable APIs
gcloud services enable \
    compute.googleapis.com \
    storage.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    redis.googleapis.com \
    aiplatform.googleapis.com

# Create service account
gcloud iam service-accounts create raptorflow-backend \
    --display-name="RaptorFlow Backend"

# Grant permissions
gcloud projects add-iam-policy-binding raptorflow-prod \
    --member="serviceAccount:raptorflow-backend@raptorflow-prod.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
```

## 🏗️ Step 2: Deploy Infrastructure

### 2.1 Terraform Deployment
```bash
cd gcp/terraform
terraform init
terraform plan
terraform apply
```

### 2.2 What Gets Created:
- **GCS Buckets**: 3 buckets for file storage
- **Cloud Run Service**: Backend API
- **Redis Instance**: Caching layer
- **Vertex AI**: AI/ML capabilities
- **BigQuery Dataset**: Analytics
- **Artifact Registry**: Container storage

## 🚀 Step 3: Deploy Backend

### 3.1 Build and Push Container
```bash
cd backend
docker build -t gcr.io/raptorflow-prod/raptorflow-backend:latest .
docker push gcr.io/raptorflow-prod/raptorflow-backend:latest
```

### 3.2 Deploy to Cloud Run
```bash
gcloud run deploy raptorflow-backend \
  --image gcr.io/raptorflow-prod/raptorflow-backend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --max-instances 10
```

### 3.3 Set Environment Variables
```bash
gcloud run services update raptorflow-backend \
  --region us-central1 \
  --set-env-vars \
  SUPABASE_URL=https://your-project.supabase.co \
  SUPABASE_SERVICE_ROLE_KEY=your-service-role-key \
  GCP_PROJECT_ID=raptorflow-prod \
  GCP_REGION=us-central1 \
  REDIS_HOST=10.0.0.0
```

## 🗄️ Step 4: Database Setup

### 4.1 Supabase Tables
```sql
-- Run in Supabase SQL Editor
CREATE TABLE IF NOT EXISTS public.user_profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  subscription_plan TEXT CHECK (subscription_plan IN ('soar', 'glide', 'ascent')),
  subscription_status TEXT CHECK (subscription_status IN ('active', 'cancelled', 'expired')),
  subscription_expires_at TIMESTAMPTZ,
  storage_quota_mb INTEGER DEFAULT 100,
  storage_used_mb INTEGER DEFAULT 0,
  plan_features JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.payments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  transaction_id TEXT UNIQUE NOT NULL,
  plan_id TEXT NOT NULL CHECK (plan_id IN ('soar', 'glide', 'ascent')),
  amount INTEGER NOT NULL,
  currency TEXT DEFAULT 'INR',
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
  payment_method TEXT DEFAULT 'phonepe',
  phonepe_transaction_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  verified_at TIMESTAMPTZ
);

-- Enable RLS and policies
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile" ON public.user_profiles
  FOR SELECT USING (auth.uid() = id);

-- ... (other policies)
```

## 📦 Step 5: Storage Buckets

### 5.1 GCS Buckets Created:
- `raptorflow-prod-user-avatars` - Profile pictures (2MB limit)
- `raptorflow-prod-user-documents` - Documents (50MB limit)
- `raptorflow-prod-workspace-files` - Workspace files (100MB limit)

### 5.2 Storage Policies:
```sql
-- Run in Supabase SQL Editor
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES
  ('user-avatars', 'user-avatars', true, 2097152, ARRAY['image/jpeg', 'image/png', 'image/gif', 'image/webp']),
  ('user-documents', 'user-documents', false, 52428800, ARRAY['image/jpeg', 'image/png', 'application/pdf', 'text/plain', 'application/json']),
  ('workspace-files', 'workspace-files', false, 104857600, ARRAY['image/jpeg', 'image/png', 'application/pdf', 'application/vnd.ms-excel', 'text/csv'])
ON CONFLICT (id) DO NOTHING;
```

## 🧠 Step 6: Redis Configuration

### 6.1 Redis Instance:
- **Name**: raptorflow-redis
- **Size**: 4GB
- **Tier**: Standard HA
- **Region**: us-central1
- **Host**: 10.0.0.0

### 6.2 Usage:
- Session caching
- Subscription status cache
- API rate limiting
- Temporary storage

## 🤖 Step 7: Vertex AI Setup

### 7.1 Enable Vertex AI:
```bash
gcloud services enable aiplatform.googleapis.com
```

### 7.2 Available Models:
- **Gemini Pro**: Text generation
- **Gemini Pro Vision**: Image analysis
- **Custom Models**: Train your own models

### 7.3 Usage in Backend:
```python
from vertexai.generative_models import GenerativeModel

model = GenerativeModel("gemini-pro")
response = model.generate_content("Your prompt here")
```

## 📊 Step 8: Analytics Setup

### 8.1 BigQuery Dataset:
```sql
CREATE TABLE `raptorflow-prod.ai_usage.usage_logs` (
  user_id STRING,
  model STRING,
  prompt_length INTEGER,
  response_length INTEGER,
  timestamp TIMESTAMP
);
```

### 8.2 Analytics Dashboard:
- User engagement metrics
- AI usage tracking
- Storage utilization
- Payment analytics

## 🔐 Step 9: Security Configuration

### 9.1 IAM Roles:
- **raptorflow-backend**: Storage admin, AI platform user, Cloud Run admin
- **Users**: Access via Supabase RLS policies

### 9.2 Network Security:
- Cloud Run: No public access (use API Gateway)
- GCS: Signed URLs for uploads/downloads
- Redis: Private network

## 🚀 Step 10: CI/CD Pipeline

### 10.1 Cloud Build Trigger:
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/raptorflow-backend:$COMMIT_SHA', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/raptorflow-backend:$COMMIT_SHA']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'raptorflow-backend']
```

### 10.2 Automated Deployment:
- Push to GitHub → Cloud Build → Docker → Cloud Run

## 📱 Step 11: Frontend Configuration

### 11.1 Environment Variables:
```env
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
NEXT_PUBLIC_API_URL=https://your-backend-url.run.app
```

### 11.2 GCP Integration:
- Storage: `/api/gcp-storage`
- AI: `/api/vertex-ai`
- Analytics: `/api/analytics`

## ✅ Verification Checklist

### Database:
- [ ] Supabase tables created
- [ ] RLS policies applied
- [ ] Triggers working

### Storage:
- [ ] GCS buckets created
- [ ] CORS configured
- [ ] Signed URLs working

### Backend:
- [ ] Cloud Run service deployed
- [ ] Environment variables set
- [ ] Health check passing

### AI:
- [ ] Vertex AI enabled
- [ ] Models accessible
- [ ] Usage tracking working

### Frontend:
- [ ] Authentication working
- [ ] File uploads working
- [ ] AI features working

## 🎯 Production Considerations

1. **Monitoring**: Set up Cloud Monitoring and alerting
2. **Logging**: Configure Cloud Logging for all services
3. **Backup**: Enable database backups and point-in-time recovery
4. **Scaling**: Configure auto-scaling for Cloud Run
5. **Security**: Regular security audits and IAM reviews

## 📞 Support

For issues with:
- **GCP Setup**: Check Cloud Console logs
- **Terraform**: Run `terraform plan` to preview changes
- **Backend**: Check Cloud Run logs
- **Database**: Check Supabase logs
- **Storage**: Check GCS logs

## 🎉 You're Ready!

Your RaptorFlow application is now fully integrated with Google Cloud Platform, providing:
- ✅ Scalable backend on Cloud Run
- ✅ Secure file storage on GCS
- ✅ Fast caching with Redis
- ✅ AI capabilities with Vertex AI
- ✅ Analytics with BigQuery
- ✅ CI/CD with Cloud Build
- ✅ Robust database with Supabase

All services are configured, deployed, and ready for production use!
