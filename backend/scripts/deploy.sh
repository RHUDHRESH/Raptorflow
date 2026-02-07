#!/bin/bash

# RaptorFlow API Deployment Script
# Usage: ./deploy.sh [environment] [version]
# Environments: staging, production

set -e

# Default values
ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}
NAMESPACE="raptorflow"
REGISTRY="ghcr.io/raptorflow/raptorflow-api"

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

# Check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
}

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
}

# Validate environment
validate_environment() {
    if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
        log_error "Invalid environment. Must be 'staging' or 'production'"
        exit 1
    fi
}

# Build Docker image
build_image() {
    log_info "Building Docker image for $ENVIRONMENT environment..."

    if [[ "$ENVIRONMENT" == "production" ]]; then
        docker build -f Dockerfile.production -t $REGISTRY:$VERSION .
    else
        docker build -f Dockerfile -t $REGISTRY:$ENVIRONMENT-$VERSION .
    fi

    log_info "Docker image built successfully"
}

# Push Docker image
push_image() {
    log_info "Pushing Docker image to registry..."

    if [[ "$ENVIRONMENT" == "production" ]]; then
        docker push $REGISTRY:$VERSION
    else
        docker push $REGISTRY:$ENVIRONMENT-$VERSION
    fi

    log_info "Docker image pushed successfully"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log_info "Deploying to $ENVIRONMENT environment..."

    # Set namespace context
    kubectl config use-context $ENVIRONMENT

    # Apply deployment
    if [[ "$ENVIRONMENT" == "production" ]]; then
        kubectl apply -f k8s/production-deployment.yaml -n $NAMESPACE
    else
        kubectl apply -f k8s/staging-deployment.yaml -n $NAMESPACE
    fi

    # Wait for deployment to be ready
    log_info "Waiting for deployment to be ready..."
    kubectl rollout status deployment/raptorflow-api-$ENVIRONMENT -n $NAMESPACE --timeout=300s

    log_info "Deployment completed successfully"
}

# Run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."

    # Get service URL
    if [[ "$ENVIRONMENT" == "production" ]]; then
        SERVICE_URL="https://api.raptorflow.com"
    else
        SERVICE_URL="https://staging-api.raptorflow.com"
    fi

    # Test health endpoint
    if curl -f -s "$SERVICE_URL/health" > /dev/null; then
        log_info "Health check passed"
    else
        log_error "Health check failed"
        exit 1
    fi

    # Test metrics endpoint
    if curl -f -s "$SERVICE_URL/metrics" > /dev/null; then
        log_info "Metrics endpoint check passed"
    else
        log_warn "Metrics endpoint check failed (may be expected)"
    fi

    log_info "Smoke tests completed successfully"
}

# Rollback deployment
rollback() {
    log_warn "Rolling back deployment..."

    kubectl rollout undo deployment/raptorflow-api-$ENVIRONMENT -n $NAMESPACE

    log_info "Rollback completed"
}

# Main deployment function
deploy() {
    log_info "Starting deployment to $ENVIRONMENT environment..."

    check_kubectl
    check_docker
    validate_environment

    # Build and push image
    build_image
    push_image

    # Deploy to Kubernetes
    deploy_kubernetes

    # Run smoke tests
    run_smoke_tests

    log_info "Deployment to $ENVIRONMENT completed successfully!"
}

# Show usage
show_usage() {
    echo "Usage: $0 [environment] [version] [options]"
    echo ""
    echo "Environments:"
    echo "  staging     Deploy to staging environment"
    echo "  production  Deploy to production environment"
    echo ""
    echo "Versions:"
    echo "  latest      Use latest tag (default)"
    echo "  v1.0.0      Use specific version tag"
    echo ""
    echo "Options:"
    echo "  --rollback  Rollback the current deployment"
    echo "  --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 staging latest"
    echo "  $0 production v1.2.3"
    echo "  $0 production --rollback"
}

# Parse command line arguments
case "$3" in
    --rollback)
        rollback
        exit 0
        ;;
    --help)
        show_usage
        exit 0
        ;;
    "")
        # No option, continue with deployment
        ;;
    *)
        log_error "Unknown option: $3"
        show_usage
        exit 1
        ;;
esac

# Run deployment
deploy
