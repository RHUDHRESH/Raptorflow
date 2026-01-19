#!/bin/bash

# GCS Setup Script for Raptorflow
# This script sets up Google Cloud Storage buckets and permissions

set -e

echo "🚀 Setting up Google Cloud Storage for Raptorflow..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it first:"
    echo "https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project)}
if [ -z "$PROJECT_ID" ]; then
    echo "❌ GCP_PROJECT_ID not set and no default project configured"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Using project: $PROJECT_ID"

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable storage.googleapis.com --project=$PROJECT_ID
gcloud services enable storage-component.googleapis.com --project=$PROJECT_ID

# Bucket configuration
BUCKET_NAME=${GCS_BUCKET_NAME:-"raptorflow-uploads"}
REGION=${GCP_REGION:-"us-central1"}

echo "🪣 Creating bucket: $BUCKET_NAME in $REGION"

# Create bucket
if gsutil ls -b gs://$BUCKET_NAME &> /dev/null; then
    echo "✅ Bucket already exists"
else
    gsutil mb -l $REGION gs://$BUCKET_NAME
    echo "✅ Bucket created successfully"
fi

# Set bucket configuration
echo "⚙️ Configuring bucket settings..."

# Enable versioning
gsutil versioning set on gs://$BUCKET_NAME

# Set lifecycle rules
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 90}
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://$BUCKET_NAME
rm lifecycle.json

# Set uniform bucket-level access
echo "🔐 Setting up access control..."
gsutil iam ch uniformBucketLevelAccess:enabled gs://$BUCKET_NAME

# Create service account if it doesn't exist
SERVICE_ACCOUNT="raptorflow-storage@${PROJECT_ID}.iam.gserviceaccount.com"

if gcloud iam service-accounts describe $SERVICE_ACCOUNT &> /dev/null; then
    echo "✅ Service account already exists"
else
    echo "🔧 Creating service account..."
    gcloud iam service-accounts create raptorflow-storage \
        --display-name="Raptorflow Storage Service" \
        --description="Service account for Raptorfile storage operations"
fi

# Grant permissions to service account
echo "🔑 Granting permissions..."
gsutil iam ch serviceAccount:$SERVICE_ACCOUNT:objectAdmin gs://$BUCKET_NAME
gsutil iam ch serviceAccount:$SERVICE_ACCOUNT:bucketAdmin gs://$BUCKET_NAME

# Generate service account key
echo "🔑 Generating service account key..."
KEY_FILE="raptorflow-storage-key.json"
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SERVICE_ACCOUNT \
    --key-file-type=json

echo "✅ Service account key saved to: $KEY_FILE"
echo "⚠️  Keep this key secure and add it to your environment variables!"

# Test bucket access
echo "🧪 Testing bucket access..."
echo "test-file" | gsutil cp - gs://$BUCKET_NAME/test-upload.txt
gsutil rm gs://$BUCKET_NAME/test-upload.txt

echo ""
echo "🎉 GCS setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Add the service account key to your backend environment:"
echo "   GOOGLE_APPLICATION_CREDENTIALS=/path/to/$KEY_FILE"
echo ""
echo "2. Update your .env file with:"
echo "   GCS_BUCKET_NAME=$BUCKET_NAME"
echo "   GCP_PROJECT_ID=$PROJECT_ID"
echo "   GCP_REGION=$REGION"
echo ""
echo "3. The bucket is configured with:"
echo "   - Versioning: Enabled"
echo "   - Lifecycle: Auto-delete after 365 days"
echo "   - Storage classes: Standard → Nearline (30d) → Coldline (90d)"
echo "   - Access: Uniform bucket-level access"
echo ""
