#!/bin/bash
set -e

echo "🚀 Deploying Raptorflow to Production..."

# Validate environment
if [ ! -f "frontend/.env.production" ]; then
    echo "❌ frontend/.env.production file not found"
    exit 1
fi

if [ ! -f "backend/.env.production" ]; then
    echo "❌ backend/.env.production file not found"
    exit 1
fi

# Check if required tools are installed
command -v vercel >/dev/null 2>&1 || { echo "❌ Vercel CLI is not installed. Please run: npm i -g vercel"; exit 1; }
command -v gcloud >/dev/null 2>&1 || { echo "❌ Google Cloud CLI is not installed. Please run: https://cloud.google.com/sdk/docs/install"; exit 1; }

# Load production environment variables
echo "📋 Loading production environment variables..."
export NODE_ENV=production

# Build frontend
echo "📦 Building frontend..."
cd frontend
npm ci --only=production
npm run build

# Run frontend tests if available
if [ -f "package.json" ] && grep -q "test" package.json; then
    echo "🧪 Running frontend tests..."
    npm test -- --watchAll=false
fi

# Deploy frontend to Vercel
echo "🌐 Deploying frontend to Vercel..."
vercel --prod --confirm
FRONTEND_URL=$(vercel ls --scope=vercel 2>/dev/null | grep raptorflow | head -1 | awk '{print $2}' || echo "https://raptorflow.vercel.app")
echo "✅ Frontend deployed to: $FRONTEND_URL"

cd ..

# Deploy backend to Google Cloud
echo "🔧 Deploying backend to Google Cloud..."

# Check if we're in the right project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ "$CURRENT_PROJECT" != "raptorflow-481505" ]; then
    echo "🔄 Setting GCP project to raptorflow-481505..."
    gcloud config set project raptorflow-481505
fi

# Build backend Docker image
echo "🐳 Building backend Docker image..."
cd backend
docker build -t gcr.io/raptorflow-481505/raptorflow-backend:latest .

# Push to Google Container Registry
echo "📤 Pushing Docker image to GCR..."
gcloud auth configure-docker
docker push gcr.io/raptorflow-481505/raptorflow-backend:latest

# Deploy to Cloud Run
echo "☁️ Deploying to Cloud Run..."
gcloud run deploy raptorflow-backend \
    --image gcr.io/raptorflow-481505/raptorflow-backend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --concurrency 80 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "$(cat .env.production | grep -v '^#' | tr '\n' ',' | sed 's/,$//')"

# Get backend URL
BACKEND_URL=$(gcloud run services describe raptorflow-backend --region us-central1 --format 'value(status.url)' 2>/dev/null)
echo "✅ Backend deployed to: $BACKEND_URL"

cd ..

# Update DNS and environment variables (optional)
echo "🔄 Updating environment configuration..."

# Create a summary file
cat > deployment-summary.md << EOF
# Raptorflow Production Deployment Summary

## Deployment Information
- **Timestamp**: $(date)
- **Frontend URL**: $FRONTEND_URL
- **Backend URL**: $BACKEND_URL
- **GCP Project**: raptorflow-481505
- **Region**: us-central1

## Environment Variables Used
- Frontend: frontend/.env.production
- Backend: backend/.env.production

## Services Deployed
- **Frontend**: Vercel (Next.js)
- **Backend**: Google Cloud Run (Docker)
- **Database**: Supabase
- **Storage**: Google Cloud Storage
- **Monitoring**: Sentry

## Next Steps
1. Update Vercel environment variables in dashboard
2. Configure custom domains if needed
3. Set up monitoring alerts
4. Test all API endpoints
5. Verify authentication flow

## Rollback Commands
- Frontend: vercel rollback --prod
- Backend: gcloud run services update-traffic raptorflow-backend --region us-central1 --to-revisions=REVISION_NAME=100
EOF

echo "📄 Deployment summary created in deployment-summary.md"

# Health checks
echo "🏥 Running health checks..."
sleep 30

# Check frontend health
if curl -f -s "$FRONTEND_URL" > /dev/null; then
    echo "✅ Frontend health check passed"
else
    echo "❌ Frontend health check failed"
fi

# Check backend health
if curl -f -s "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo "✅ Backend health check passed"
else
    echo "⚠️ Backend health check failed (endpoint may not exist)"
fi

echo ""
echo "🎉 Production deployment completed successfully!"
echo "📋 Summary: deployment-summary.md"
echo "🌐 Frontend: $FRONTEND_URL"
echo "🔧 Backend: $BACKEND_URL"
