#!/bin/bash

# Raptorflow Cloud Run Scraper Deployment Script
# This script builds and deploys the enhanced scraper to Google Cloud Run

set -e

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-raptorflow-481505}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="raptorflow-scraper"
BUCKET_NAME="raptorflow-scraped-data"
TOPIC_NAME="scraping-results"

echo "🚀 Deploying Raptorflow Cloud Scraper to Google Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo "❌ Please run 'gcloud auth login' first."
    exit 1
fi

# Set the project
echo "📋 Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable logging.googleapis.com

# Create Cloud Storage bucket if it doesn't exist
echo "📦 Creating Cloud Storage bucket..."
if ! gsutil ls gs://$BUCKET_NAME &> /dev/null; then
    gsutil mb gs://$BUCKET_NAME
    echo "✅ Created bucket: gs://$BUCKET_NAME"
else
    echo "✅ Bucket already exists: gs://$BUCKET_NAME"
fi

# Create Pub/Sub topic if it doesn't exist
echo "📨 Creating Pub/Sub topic..."
if ! gcloud pubsub topics describe $TOPIC_NAME &> /dev/null; then
    gcloud pubsub topics create $TOPIC_NAME
    echo "✅ Created topic: $TOPIC_NAME"
else
    echo "✅ Topic already exists: $TOPIC_NAME"
fi

# Build and deploy the service
echo "🔨 Building and deploying Cloud Run service..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --min-instances 0 \
    --max-instances 10 \
    --cpu 1 \
    --memory 1Gi \
    --timeout 60s \
    --concurrency 10 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-env-vars="BUCKET_NAME=$BUCKET_NAME" \
    --set-env-vars="TOPIC_NAME=$TOPIC_NAME" \
    --set-env-vars="MAX_CONTENT_LENGTH=10000000"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format="value(status.url)")

echo "✅ Deployment complete!"
echo "🌐 Service URL: $SERVICE_URL"
echo "🧪 Test the service:"
echo "curl -X POST \"$SERVICE_URL/scrape\" -H \"Content-Type: application/json\" -d '{\"url\":\"https://example.com\",\"user_id\":\"test-user\"}'"

# Test the health endpoint
echo "🏥 Testing health endpoint..."
if curl -s "$SERVICE_URL/health" | grep -q "healthy"; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    exit 1
fi

echo "🎉 Raptorflow Cloud Scraper is ready!"
echo "📊 View logs: gcloud logs read \"resource.type=cloud_run_revision\" --limit 50 --format=\"table(textPayload)\""
echo "🔍 View service: gcloud run services describe $SERVICE_NAME --region $REGION"
