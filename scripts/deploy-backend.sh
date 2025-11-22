#!/bin/bash

# RaptorFlow Backend - Google Cloud Run Deployment Script
# Deploys the Python FastAPI backend to Google Cloud Run

set -e  # Exit on error

# Colors for output
GREEN='\033[0.32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 RaptorFlow Backend Deployment to Google Cloud Run${NC}"
echo "=================================================="

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}
REGION=${GOOGLE_CLOUD_REGION:-"us-central1"}
SERVICE_NAME="raptorflow-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠️  GOOGLE_CLOUD_PROJECT not set. Please set it:${NC}"
    echo "export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

echo -e "${GREEN}✓ Project ID: ${PROJECT_ID}${NC}"
echo -e "${GREEN}✓ Region: ${REGION}${NC}"
echo -e "${GREEN}✓ Service Name: ${SERVICE_NAME}${NC}"
echo ""

# Authenticate
echo -e "${YELLOW}🔐 Authenticating with Google Cloud...${NC}"
gcloud auth configure-docker

# Build the container image
echo -e "${YELLOW}📦 Building Docker image...${NC}"
docker build -f Dockerfile.backend -t ${IMAGE_NAME}:latest .

# Tag with timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${TIMESTAMP}

# Push to Google Container Registry
echo -e "${YELLOW}⬆️  Pushing image to GCR...${NC}"
docker push ${IMAGE_NAME}:latest
docker push ${IMAGE_NAME}:${TIMESTAMP}

echo -e "${GREEN}✓ Image pushed successfully${NC}"
echo ""

# Deploy to Cloud Run
echo -e "${YELLOW}🌐 Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --set-env-vars "ENVIRONMENT=production,DEBUG=False,LOG_LEVEL=INFO" \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
    --set-env-vars "VERTEX_AI_LOCATION=${REGION}" \
    --set-secrets "SUPABASE_URL=SUPABASE_URL:latest" \
    --set-secrets "SUPABASE_SERVICE_KEY=SUPABASE_SERVICE_KEY:latest" \
    --set-secrets "SUPABASE_JWT_SECRET=SUPABASE_JWT_SECRET:latest" \
    --set-secrets "REDIS_URL=REDIS_URL:latest" \
    --project ${PROJECT_ID}

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)' \
    --project ${PROJECT_ID})

echo ""
echo -e "${GREEN}=================================================="
echo -e "✅ Deployment successful!"
echo -e "=================================================="
echo -e "📍 Service URL: ${SERVICE_URL}"
echo -e "📚 API Docs: ${SERVICE_URL}/docs"
echo -e "❤️  Health Check: ${SERVICE_URL}/health"
echo -e "=================================================${NC}"
echo ""
echo -e "${YELLOW}💡 Next steps:${NC}"
echo "1. Update frontend VITE_BACKEND_API_URL to: ${SERVICE_URL}/api/v1"
echo "2. Ensure all secrets are set in Google Secret Manager"
echo "3. Test the deployment: curl ${SERVICE_URL}/health"
echo ""



