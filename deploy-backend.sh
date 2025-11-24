#!/bin/bash
# Deploy RaptorFlow Backend to Google Cloud Run

set -e

echo "🚀 RaptorFlow Backend Deployment to Cloud Run"
echo "=============================================="

# Configuration
PROJECT_ID="raptorflow-477017"
SERVICE_NAME="raptorflow-backend"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found. Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Get project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo "📝 Authenticating with Google Cloud..."
gcloud auth login
gcloud config set project "$PROJECT_ID"

echo "⚙️  Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Configure environment variables
echo "🔐 Setting up environment variables..."
echo "Create backend/.env.prod with your production secrets:"
echo ""
echo "ENVIRONMENT=production"
echo "DEBUG=False"
echo "LOG_LEVEL=WARNING"
echo "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"
echo "SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co"
echo "SUPABASE_SERVICE_KEY=your_service_key_here"
echo "SECRET_KEY=your-strong-random-string-here"
echo ""
read -p "Press Enter once you've created backend/.env.prod: "

if [ ! -f "backend/.env.prod" ]; then
    echo "❌ backend/.env.prod not found!"
    exit 1
fi

echo "🐳 Building Docker image..."
docker build -f Dockerfile.cloudrun -t "${IMAGE_NAME}:latest" .

echo "🔼 Pushing image to Google Container Registry..."
docker push "${IMAGE_NAME}:latest"

echo "☁️  Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE_NAME}:latest" \
    --platform managed \
    --region "${REGION}" \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 3600 \
    --max-instances 10 \
    --env-vars-file backend/.env.prod

echo ""
echo "✅ Backend deployed successfully!"
echo ""
echo "📊 Service URL:"
gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format="value(status.url)"
echo ""
echo "📋 View logs:"
echo "gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}\" --limit 50"
