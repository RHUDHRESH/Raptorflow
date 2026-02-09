#!/bin/bash

# RaptorFlow GCP Deployment Script
set -e

echo "🚀 Deploying RaptorFlow to Google Cloud Platform..."

# Set variables
PROJECT_ID=${PROJECT_ID:-"raptorflow-prod"}
REGION=${REGION:-"us-central1"}
BACKEND_IMAGE="gcr.io/${PROJECT_ID}/raptorflow-backend"

echo "📦 Building and pushing backend image..."
cd backend
docker build -t ${BACKEND_IMAGE}:latest .
docker push ${BACKEND_IMAGE}:latest

echo "🔧 Applying Terraform infrastructure..."
cd ../terraform
terraform init
terraform apply -auto-approve

echo "🚀 Deploying backend to Cloud Run..."
gcloud run deploy raptorflow-backend \
  --image ${BACKEND_IMAGE}:latest \
  --region ${REGION} \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars \
  SUPABASE_URL=${SUPABASE_URL} \
  SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY} \
  GCP_PROJECT_ID=${PROJECT_ID} \
  GCP_REGION=${REGION} \
  REDIS_HOST=$(gcloud redis instances list --format='value(name)' --filter='name:raptorflow-redis')

echo "🔧 Setting up Cloud Build triggers..."
gcloud builds triggers create raptorflow-backend \
  --repo-name ${GITHUB_REPO} \
  --repo-owner ${GITHUB_OWNER} \
  --branch-name main \
  --build-config cloudbuild.yaml \
  --description "Auto-build and deploy RaptorFlow backend"

echo "📊 Creating BigQuery dataset for analytics..."
bq mk --dataset ${PROJECT_ID}:ai_usage
bq mk --table ${PROJECT_ID}:ai_usage.usage_logs \
  --schema user_id:STRING,model:STRING,prompt_length:INTEGER,response_length:INTEGER,timestamp:TIMESTAMP

echo "✅ Deployment complete!"
echo ""
echo "🌐 Frontend URL: https://raptorflow.in"
echo "🔧 Backend URL: $(gcloud run services describe raptorflow-backend --region ${REGION} --format='value(status.url)')"
echo "💾 Storage buckets: gsutil ls"
echo "🔴 Redis instance: $(gcloud redis instances list --format='value(name)')"
echo "🧠 Vertex AI: https://console.cloud.google.com/vertex-ai"
echo "📊 BigQuery: https://console.cloud.google.com/bigquery"
