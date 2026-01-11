#!/bin/bash

# RaptorFlow Backend Production Deployment Script
# Deploys the backend to Google Cloud Run

set -e

# Configuration
PROJECT_ID="${PROJECT_ID:-your-gcp-project-id}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-raptorflow-backend}"
IMAGE_NAME="${IMAGE_NAME:-raptorflow-backend}"
TAG="${TAG:-latest}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check required tools
check_requirements() {
    log_info "Checking requirements..."

    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed"
        exit 1
    fi

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    log_info "Requirements check passed"
}

# Set up GCP project
setup_project() {
    log_info "Setting up GCP project..."

    gcloud config set project "$PROJECT_ID"
    gcloud services enable \
        run.googleapis.com \
        cloudbuild.googleapis.com \
        artifactregistry.googleapis.com \
        secretmanager.googleapis.com \
        sql-component.googleapis.com

    log_info "GCP project setup complete"
}

# Build and push Docker image
build_and_push() {
    log_info "Building and pushing Docker image..."

    # Configure Docker to use gcloud as a credential helper
    gcloud auth configure-docker "$REGION-docker.pkg.dev"

    # Build the image
    docker build -f Dockerfile.production -t "$IMAGE_NAME:$TAG" .

    # Tag the image for Artifact Registry
    IMAGE_PATH="$REGION-docker.pkg.dev/$PROJECT_ID/raptorflow/$IMAGE_NAME:$TAG"
    docker tag "$IMAGE_NAME:$TAG" "$IMAGE_PATH"

    # Push the image
    docker push "$IMAGE_PATH"

    log_info "Docker image pushed: $IMAGE_PATH"
}

# Deploy to Cloud Run
deploy_cloud_run() {
    log_info "Deploying to Cloud Run..."

    IMAGE_PATH="$REGION-docker.pkg.dev/$PROJECT_ID/raptorflow/$IMAGE_NAME:$TAG"

    # Deploy to Cloud Run
    gcloud run deploy "$SERVICE_NAME" \
        --image="$IMAGE_PATH" \
        --region="$REGION" \
        --platform=managed \
        --allow-unauthenticated \
        --memory=1Gi \
        --cpu=1 \
        --timeout=300 \
        --concurrency=1000 \
        --max-instances=100 \
        --min-instances=0 \
        --set-env-vars="ENVIRONMENT=production" \
        --set-secrets="SUPABASE_URL=supabase-url:latest" \
        --set-secrets="SUPABASE_SERVICE_ROLE_KEY=supabase-service-key:latest" \
        --set-secrets="UPSTASH_REDIS_URL=redis-url:latest" \
        --set-secrets="UPSTASH_REDIS_TOKEN=redis-token:latest" \
        --set-secrets="JWT_SECRET_KEY=jwt-secret:latest" \
        --set-env-vars="ENABLE_RATE_LIMITING=true" \
        --set-env-vars="RATE_LIMIT_REQUESTS=100" \
        --set-env-vars="LOG_LEVEL=INFO" \
        --set-env-vars="ENABLE_METRICS=true" \
        --set-env-vars="ENABLE_HEALTH_CHECKS=true"

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="value(status.url)")

    log_info "Deployment complete!"
    log_info "Service URL: $SERVICE_URL"
}

# Update CORS origins
update_cors() {
    log_info "Updating CORS origins..."

    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="value(status.url)")

    # Update ALLOWED_ORIGINS environment variable
    gcloud run services update "$SERVICE_NAME" \
        --region="$REGION" \
        --set-env-vars="ALLOWED_ORIGINS=$SERVICE_URL,https://yourdomain.com"

    log_info "CORS origins updated"
}

# Health check
health_check() {
    log_info "Performing health check..."

    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="value(status.url)")

    # Wait for deployment to be ready
    sleep 30

    # Check health endpoint
    if curl -f "$SERVICE_URL/health" > /dev/null 2>&1; then
        log_info "Health check passed"
    else
        log_error "Health check failed"
        exit 1
    fi
}

# Main deployment function
main() {
    log_info "Starting RaptorFlow Backend deployment..."

    check_requirements
    setup_project
    build_and_push
    deploy_cloud_run
    update_cors
    health_check

    log_info "Deployment completed successfully! 🚀"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "build")
        build_and_push
        ;;
    "health")
        health_check
        ;;
    "setup")
        check_requirements
        setup_project
        ;;
    *)
        echo "Usage: $0 {deploy|build|health|setup}"
        echo "  deploy  - Full deployment (default)"
        echo "  build   - Build and push Docker image only"
        echo "  health  - Perform health check"
        echo "  setup   - Set up GCP project and services"
        exit 1
        ;;
esac
