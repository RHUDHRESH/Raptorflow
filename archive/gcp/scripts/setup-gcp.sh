#!/bin/bash

# GCP Setup Script for RaptorFlow
set -e

echo "🔧 Setting up Google Cloud Platform for RaptorFlow..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it first:"
    echo "curl https://sdk.cloud.google.com | bash"
    exit 1
fi

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Please install it first:"
    echo "https://developer.hashicorp.com/terraform/downloads"
    exit 1
fi

# Set project
PROJECT_ID=${PROJECT_ID:-"raptorflow-prod"}
echo "📋 Using project: ${PROJECT_ID}"

# Create or select project
gcloud projects list | grep -q "${PROJECT_ID}" || {
    echo "🆕 Creating new project: ${PROJECT_ID}"
    gcloud projects create ${PROJECT_ID} \
        --name="RaptorFlow" \
        --set-as-default
}

# Set up billing
echo "💳 Setting up billing..."
BILLING_ACCOUNT=$(gcloud billing accounts list --format='value(name)' | head -1)
if [ -z "$BILLING_ACCOUNT" ]; then
    echo "❌ No billing account found. Please set up billing in Google Cloud Console."
    exit 1
fi

gcloud billing projects link ${BILLING_ACCOUNT} --project ${PROJECT_ID}

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable \
    compute.googleapis.com \
    storage.googleapis.com \
    sql-component.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    redis.googleapis.com \
    aiplatform.googleapis.com \
    iam.googleapis.com \
    resourcemanager.googleapis.com \
    --project=${PROJECT_ID}

# Create service accounts
echo "👤 Creating service accounts..."
gcloud iam service-accounts create raptorflow-backend \
    --display-name="RaptorFlow Backend Service Account" \
    --project=${PROJECT_ID}

# Grant permissions
echo "🔐 Granting permissions..."
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:raptorflow-backend@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:raptorflow-backend@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:raptorflow-backend@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Create Artifact Registry repository
echo "📦 Creating Artifact Registry repository..."
gcloud artifacts repositories create raptorflow-backend \
    --repository-format=docker \
    --location=${REGION:-us-central1} \
    --project=${PROJECT_ID}

# Create BigQuery dataset
echo "📊 Creating BigQuery dataset..."
bq mk --dataset ${PROJECT_ID}:ai_usage

# Create Redis instance
echo "🔴 Creating Redis instance..."
gcloud redis instances create raptorflow-redis \
    --size=4 \
    --tier=STANDARD_HA \
    --region=${REGION:-us-central1} \
    --authorized-network=default \
    --display-name="RaptorFlow Redis Cache" \
    --project=${PROJECT_ID}

# Create Cloud Build trigger
echo "🔨 Setting up Cloud Build..."
gcloud builds triggers create raptorflow-backend \
    --repo-name=${GITHUB_REPO:-"raptorflow"} \
    --repo-owner=${GITHUB_OWNER:-"your-username"} \
    --branch-name=main \
    --build-config=cloudbuild.yaml \
    --description="Auto-build and deploy RaptorFlow backend"

echo "✅ GCP setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Run 'terraform init && terraform apply' in the terraform directory"
echo "2. Deploy backend with 'npm run deploy'"
echo "3. Configure Supabase with the generated credentials"
echo ""
echo "🔗 Useful links:"
echo "Google Cloud Console: https://console.cloud.google.com"
echo "Artifact Registry: https://console.cloud.google.com/artifacts"
echo "Cloud Build: https://console.cloud.google.com/cloud-build"
echo "Cloud Run: https://console.cloud.google.com/run"
echo "Vertex AI: https://console.cloud.google.com/vertex-ai"
