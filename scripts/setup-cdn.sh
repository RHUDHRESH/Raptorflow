#!/bin/bash

# CDN Setup Script for Raptorflow GCS
# Sets up Google Cloud CDN with GCS backend

set -e

echo "🚀 Setting up Google Cloud CDN for Raptorflow..."

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project)}
BUCKET_NAME=${GCS_BUCKET_NAME:-"raptorflow-uploads"}
CDN_NAME="raptorflow-cdn"

if [ -z "$PROJECT_ID" ]; then
    echo "❌ GCP_PROJECT_ID not set"
    exit 1
fi

echo "📋 Project: $PROJECT_ID"
echo "🪣 Bucket: $BUCKET_NAME"

# Enable required APIs
echo "🔧 Enabling CDN APIs..."
gcloud services enable compute.googleapis.com --project=$PROJECT_ID
gcloud services enable loadbalancing.googleapis.com --project=$PROJECT_ID

# Create external IP address
echo "🌐 Creating external IP address..."
gcloud compute addresses create raptorflow-cdn-ip \
    --global \
    --project=$PROJECT_ID

# Get the external IP
EXTERNAL_IP=$(gcloud compute addresses describe raptorflow-cdn-ip \
    --global \
    --format="get(address)" \
    --project=$PROJECT_ID)

echo "📍 External IP reserved: $EXTERNAL_IP"

# Create backend bucket
echo "🪣 Creating backend bucket..."
gcloud compute backend-buckets create $BUCKET_NAME \
    --gcs-bucket-name=$BUCKET_NAME \
    --enable-cdn \
    --cache-mode=CACHE_STORAGE_STATIC \
    --default-ttl=3600 \
    --max-ttl=86400 \
    --project=$PROJECT_ID

# Create URL map
echo "🗺️ Creating URL map..."
gcloud compute url-maps create raptorflow-cdn-map \
    --default-service=$BUCKET_NAME \
    --project=$PROJECT_ID

# Create HTTPS proxy
echo "🔒 Creating HTTPS proxy..."
gcloud compute target-https-proxies create raptorflow-cdn-https \
    --url-map=raptorflow-cdn-map \
    --ssl-certificates=raptorflow-ssl-cert \
    --project=$PROJECT_ID

# Create forwarding rule
echo "➡️ Creating forwarding rule..."
gcloud compute forwarding-rules create raptorflow-cdn-https \
    --address=$EXTERNAL_IP \
    --global \
    --target-https-proxy=raptorflow-cdn-https \
    --ports=443 \
    --project=$PROJECT_ID

# Create SSL certificate (managed)
echo "🔐 Creating SSL certificate..."
gcloud compute ssl-certificates create raptorflow-ssl-cert \
    --domains=raptorflow-cdn.yourdomain.com \
    --project=$PROJECT_ID

echo ""
echo "🎉 CDN setup initiated!"
echo ""
echo "📝 Next steps:"
echo "1. Update your DNS to point raptorflow-cdn.yourdomain.com to: $EXTERNAL_IP"
echo "2. Wait for SSL certificate to be provisioned (can take 24-48 hours)"
echo "3. Update frontend to use CDN URL: https://raptorflow-cdn.yourdomain.com"
echo ""
echo "🌐 CDN will be available at: https://raptorflow-cdn.yourdomain.com"
echo ""
echo "⚠️  Important: Replace 'yourdomain.com' with your actual domain!"
