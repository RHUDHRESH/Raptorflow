#!/bin/bash

# Production Deployment Script
# Deploys Raptorflow to production environment

set -e

# Configuration
PROJECT_ID="raptorflow-prod"
REGION="us-central1"
SERVICE_NAME="raptorflow-api"
FRONTEND_SERVICE="raptorflow-frontend"
BACKUP_SERVICE="raptorflow-backup"

echo "🚀 Starting Production Deployment..."
echo "================================"

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI (gcloud) not installed"
    echo "Please install it first: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if we're authenticated
if ! gcloud auth list 2>/dev/null | grep -q "ACTIVE"; then
    echo "❌ Not authenticated with Google Cloud"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &>dev/null; then
    echo "❌ Docker not installed"
    exit 1
fi

# Check if we're in the right project directory
if [ ! -f "Dockerfile" ] || [ ! -f "docker-compose.yml" ]; then
    echo "❌ Not in project root directory (missing Dockerfile or docker-compose.yml)"
    exit 1
fi

# Set project
echo "📋 Setting project to $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

# Build and tag Docker images
echo "🏗️ Building Docker images..."

# Backend image
echo "Building backend image..."
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

# Frontend image
echo "Building frontend image..."
docker build -f frontend/Dockerfile -t gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest ./frontend

# Push images to GCR
echo "📤 Pushing images to Google Container Registry..."

echo "Pushing backend image..."
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

echo "Pushing frontend image..."
docker push gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest

# Deploy backend service
echo "🚀 Deploying backend service..."

# Create or update Cloud Run service
gcloud run deploy "$SERVICE_NAME" \
    --image "gcr.io/$PROJECT_ID/$SERVICE_NAME:latest" \
    --region "$REGION" \
    --platform "managed" \
    --allow-unauthenticated \
    --memory "1Gi" \
    --cpu "1" \
    --timeout "300s" \
    --min-instances "1" \
    --max-instances "10" \
    --set-env-vars "DATABASE_URL=$DATABASE_URL" \
    --set-env-vars "REDIS_HOST=$REDIS_HOST" \
    --set-env-vars "REDIS_PORT=$REDIS_PORT" \
    --set-env-vars "REDIS_PASSWORD=$REDIS_PASSWORD" \
    --set-env-vars "NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL" \
    --set-env-vars "SUPABASE_URL=$SUPABASE_URL" \
    --set-env-vars "SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_KEY" \
    --set-env-vars "PHONEPE_MERCHANT_ID=$PHONEPE_MERCHANT_ID" \
    --set-env-vars "PHONEPE_SALT_KEY=$PHONEPE_SALT_KEY" \
    --set-env-vars "PHONEPE_SALT_INDEX=$PHONEPE_SALT_INDEX" \
    --set-env-vars "PHONEPE_ENV=PRODUCTION" \
    --set-cloudsql-instances "$CLOUDSQL_INSTANCE" \
    --set-cloudsql-database="$DATABASE_NAME" \
    --vpc-connector="$VPC_CONNECTOR" \
    --no-allow-unauthenticated \
    --port 8080

# Deploy frontend service
echo "🌐 Deploying frontend service..."

gcloud run deploy "$FRONTEND_SERVICE" \
    --image "gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest" \
    --region "$REGION" \
    --platform "managed" \
    --allow-unauthenticated \
    --memory "512Mi" \
    --cpu "1" \
    --timeout="30s" \
    --min-instances "1" \
    --max-instances "3" \
    --set-env-vars "NEXT_PUBLIC_API_URL=https://api.raptorflow.com" \
    --set-env-vars "NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL" \
    --set-env-vars "NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY" \
    --port 3000

# Configure domain mapping
echo "🌐 Configuring domain mapping..."

# Map custom domain to frontend
gcloud run services update-traffic "$FRONTEND_SERVICE" \
    --region "$REGION" \
    --set-mappings "api.raptorflow.com=80:api.raptorflow.com:443"

# Map API domain to backend
gcloud run services update-traffic "$SERVICE_NAME" \
    --region "$REGION" \
    --set-mappings "api.raptorflow.com=8080:api.raptorflow.com:443"

# Set up SSL certificates
echo "🔒 Setting up SSL certificates..."

# Request SSL certificate for frontend
gcloud run services update-traffic "$FRONTEND_SERVICE" \
    --region "$REGION" \
    --set-mappings "raptorflow.com=3000:raptorflow.com:443" \
    --set-mappings "www.raptorflow.com=3000:raptorflow.com:443"

# Request SSL certificate for API
gcloud run services update-traffic "$SERVICE_NAME" \
    --region "$REGION" \
    --set-mappings "api.raptorflow.com=8080:api.raptorflow.com:443"

# Configure health checks
echo "🏥 Configuring health checks..."

# Add health check to backend
gcloud run services update "$SERVICE_NAME" \
    --region "$REGION" \
    --set-health-check "/health" \
    --set-health-check-probe "GET /health" \
    --set-health-check-interval "30s" \
    --set-health-check-timeout "10s" \
    --set-health-check-healthy-threshold "2" \
    --set-health-check-unhealthy-threshold "3"

# Add health check to frontend
gcloud run services update "$FRONTEND_SERVICE" \
    --region "$REGION" \
    --set-health-check "/" \
    --set-health-check-probe "GET /" \
    --set-health-check-interval "30s" \
    --set-health-check-timeout "10s" \
    --set-health-check-healthy-threshold "2" \
    --set-health-check-unhealthy-threshold "3"

# Set up IAM permissions
echo "🔐 Setting up IAM permissions..."

# Create service account for Cloud Run
gcloud iam service-accounts create "$SERVICE_NAME-sa" \
    --display-name "$SERVICE_NAME Service Account" \
    --description "Service account for $SERVICE_NAME Cloud Run service"

# Grant necessary permissions
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

# Configure logging and monitoring
echo "📊 Configuring logging and monitoring..."

# Enable Cloud Logging
gcloud logging updates sinks create "$PROJECT_ID-raptorflow-sink" \
    --log-filter="resource.type=cloud_run_revision" \
    --description="Cloud Run logs for Raptorflow"

# Enable Cloud Monitoring
gcloud monitoring services create "$PROJECT_ID-raptorflow" \
    --display-name="Raptorflow Monitoring" \
    --monitoring-type="cloud_run"

# Set up alerting
gcloud monitoring alert-policies create \
    --display-name="High Error Rate" \
    --condition="resource.type=cloud_run_revision AND metric.type=run.googleapis.com/request_count AND metric.labels.response_code_code>=500" \
    --duration="300s" \
    --threshold-count="10" \
    --notification-channels="email"

# Set up auto-scaling
echo "⚡ Configuring auto-scaling..."

# Configure auto-scaling for backend
gcloud run services update "$SERVICE_NAME" \
    --region "$REGION" \
    --cpu "1" \
    --memory "1Gi" \
    --min-instances "1" \
    --max-instances "10" \
    --concurrency "80" \
    --scaling-mode="automatic"

# Configure auto-scaling for frontend
gcloud run services update "$FRONTEND_SERVICE" \
    --region "$REGION" \
    --cpu "1" \
    --memory "512Mi" \
    --min-instances "1" \
    --max-instances "3" \
    --concurrency "80" \
    --scaling-mode="automatic"

# Verify deployment
echo "✅ Verifying deployment..."

# Check service status
backend_status=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format="value(status)")
frontend_status=$(gcloud services describe "$FRONTEND_SERVICE" --region "$REGION" --format="value(status)")

echo "Backend service status: $backend_status"
echo "Frontend service status: $frontend_status"

# Test endpoints
echo "🧪 Testing endpoints..."

# Test backend health endpoint
if curl -s "https://api.raptorflow.com/health" | grep -q "ok"; then
    echo "✅ Backend health endpoint responding"
else
    echo "❌ Backend health endpoint not responding"
fi

# Test frontend
if curl -s "https://raptorflow.com" | grep -q "Raptorflow"; then
    echo "✅ Frontend responding"
else
    echo "❌ Frontend not responding"
fi

# Test API connectivity
if curl -s "https://api.raptorflow.com/api/v1/users" -H "Authorization: Bearer test-token" | grep -q "401\|403"; then
    echo "✅ API authentication working (properly rejects unauthorized requests)"
else
    echo "⚠️  API authentication may have issues"
fi

# Set up monitoring dashboards
echo "📈 Setting up monitoring dashboards..."

# Create Cloud Monitoring dashboard
gcloud monitoring dashboards create \
    --display-name="Raptorflow Overview" \
    --chart-metrics="run.googleapis.com/request_count,run.googleapis.com/error_count,run.googleapis.com/memory_usage" \
    --filters="resource.type=cloud_run_revision"

echo "✅ Monitoring dashboard created"

# Generate deployment report
echo ""
echo "📋 Deployment Report"
echo "================================"

echo "✅ Backend Service: $SERVICE_NAME"
echo "✅ Frontend Service: $FRONTEND_SERVICE"
echo "✅ Region: $REGION"
echo "✅ Project: $PROJECT_ID"

echo ""
echo "Service URLs:"
echo "Frontend: https://raptorflow.com"
echo "API: https://api.raptorflow.com"

echo ""
echo "Service Status:"
echo "Backend: $backend_status"
echo "Frontend: $frontend_status"

echo ""
echo "🎉 Production deployment complete!"
echo "================================"

# Post-deployment verification
echo ""
echo "🔍 Post-deployment verification..."

echo "1. Test user registration flow"
echo "2. Test workspace creation"
echo "3. Test payment integration"
echo "4. Test admin dashboard"
echo "5. Verify monitoring alerts"

echo ""
echo "Next steps:"
echo "1. Update DNS records"
echo "2. Configure CDN if needed"
echo "3. Set up monitoring alerts"
echo "4. Test all user flows"
echo "5. Document deployment process"

echo ""
echo "Deployment completed at: $(date)"
echo "================================"
