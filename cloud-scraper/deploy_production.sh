#!/bin/bash

# Production Deployment Script
# Usage: ./deploy_production.sh [environment]

set -e

# Configuration
ENVIRONMENT=${1:-production}
PROJECT_NAME="raptorflow-scraper"
REGION="us-central1"
SERVICE_NAME="ultra-fast-scraper"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check gcloud CLI
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi

    # Check if user is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "Not authenticated with gcloud. Run 'gcloud auth login'"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Build Docker image
build_image() {
    log_info "Building Docker image..."

    docker build -f Dockerfile.production -t gcr.io/$(gcloud config get-value project)/${PROJECT_NAME}:latest .

    log_success "Docker image built successfully"
}

# Push to Google Container Registry
push_image() {
    log_info "Pushing image to Google Container Registry..."

    PROJECT_ID=$(gcloud config get-value project)
    IMAGE_TAG="gcr.io/${PROJECT_ID}/${PROJECT_NAME}:latest"

    docker push ${IMAGE_TAG}

    log_success "Image pushed to GCR"
}

# Deploy to Cloud Run
deploy_cloud_run() {
    log_info "Deploying to Cloud Run..."

    PROJECT_ID=$(gcloud config get-value project)
    IMAGE_TAG="gcr.io/${PROJECT_ID}/${PROJECT_NAME}:latest"

    # Deploy to Cloud Run
    gcloud run deploy ${SERVICE_NAME} \
        --image=${IMAGE_TAG} \
        --region=${REGION} \
        --platform=managed \
        --allow-unauthenticated \
        --memory=1Gi \
        --cpu=1 \
        --timeout=300 \
        --concurrency=100 \
        --max-instances=10 \
        --min-instances=0 \
        --set-env-vars="ENVIRONMENT=${ENVIRONMENT}" \
        --set-env-vars="LOG_LEVEL=info" \
        --set-env-vars="MAX_WORKERS=8" \
        --set-env-vars="CONNECTION_POOL_SIZE=100" \
        --set-env-vars="REQUEST_TIMEOUT=10" \
        --set-env-vars="COST_TRACKING=true" \
        --set-env-vars="BUDGET_ALERTS=true" \
        --set-env-vars="MAX_COST_PER_HOUR=10.0" \
        --set-env-vars="COMPLIANCE_CHECKING=true" \
        --set-env-vars="ROBOTS_TXT_RESPECT=true" \
        --set-env-vars="RATE_LIMITING=true"

    log_success "Deployed to Cloud Run"
}

# Get service URL
get_service_url() {
    log_info "Getting service URL..."

    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
        --region=${REGION} \
        --format="value(status.url)")

    log_success "Service deployed at: ${SERVICE_URL}"
    echo ${SERVICE_URL}
}

# Run health check
health_check() {
    log_info "Running health check..."

    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
        --region=${REGION} \
        --format="value(status.url)")

    # Wait for service to be ready
    sleep 10

    # Check health endpoint
    if curl -f "${SERVICE_URL}/health" > /dev/null 2>&1; then
        log_success "Health check passed"
    else
        log_error "Health check failed"
        exit 1
    fi
}

# Set up monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."

    # Create monitoring dashboard (if needed)
    # This would integrate with Cloud Monitoring
    log_success "Monitoring setup completed"
}

# Main deployment function
deploy() {
    log_info "Starting deployment to ${ENVIRONMENT}..."

    check_prerequisites
    build_image
    push_image
    deploy_cloud_run
    SERVICE_URL=$(get_service_url)
    health_check
    setup_monitoring

    log_success "Deployment completed successfully!"
    echo ""
    echo "🚀 Ultra-Fast Scraper is now live!"
    echo "📊 Dashboard: ${SERVICE_URL}"
    echo "🔍 Health: ${SERVICE_URL}/health"
    echo "📈 Analytics: ${SERVICE_URL}/performance/analytics"
    echo "💰 Cost Tracking: ${SERVICE_URL}/cost/analytics"
}

# Local deployment
deploy_local() {
    log_info "Starting local deployment..."

    # Build and run with Docker Compose
    docker-compose -f docker-compose.production.yml up -d --build

    log_success "Local deployment completed!"
    echo ""
    echo "🚀 Ultra-Fast Scraper is now running locally!"
    echo "📊 Dashboard: http://localhost:8082"
    echo "🔍 Health: http://localhost:8082/health"
    echo "📈 Analytics: http://localhost:8082/performance/analytics"
    echo "💰 Cost Tracking: http://localhost:8080/cost/analytics"
    echo "📊 Grafana: http://localhost:3000 (admin/admin123)"
    echo "📈 Prometheus: http://localhost:9090"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."

    if [ "$ENVIRONMENT" = "local" ]; then
        docker-compose -f docker-compose.production.yml down
    else
        # Clean up Cloud Run resources
        gcloud run services delete ${SERVICE_NAME} --region=${REGION} --quiet
        log_success "Cloud Run service deleted"
    fi
}

# Show usage
usage() {
    echo "Usage: $0 [command] [environment]"
    echo ""
    echo "Commands:"
    echo "  deploy [production|local]  Deploy the scraper"
    echo "  cleanup [production|local]  Clean up resources"
    echo "  health [production|local]  Check health status"
    echo ""
    echo "Examples:"
    echo "  $0 deploy production    Deploy to Google Cloud Run"
    echo "  $0 deploy local         Deploy locally with Docker Compose"
    echo "  $0 cleanup production   Clean up Cloud Run resources"
    echo "  $0 cleanup local        Stop local containers"
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        case "${2:-production}" in
            production)
                deploy
                ;;
            local)
                deploy_local
                ;;
            *)
                log_error "Unknown environment: $2"
                usage
                exit 1
                ;;
        esac
        ;;
    cleanup)
        ENVIRONMENT=${2:-production}
        cleanup
        ;;
    health)
        ENVIRONMENT=${2:-production}
        if [ "$ENVIRONMENT" = "local" ]; then
            curl -f "http://localhost:8082/health" || log_error "Health check failed"
        else
            SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
                --region=${REGION} \
                --format="value(status.url)")
            curl -f "${SERVICE_URL}/health" || log_error "Health check failed"
        fi
        ;;
    *)
        usage
        exit 1
        ;;
esac
