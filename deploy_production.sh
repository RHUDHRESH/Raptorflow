#!/bin/bash

# RAPTORFLOW PRODUCTION DEPLOYMENT SCRIPT
# Comprehensive deployment with health checks and rollback capability

set -e

echo "🚀 Starting Raptorflow Production Deployment..."

# Configuration
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
HEALTH_CHECK_URL="http://localhost:8000/health"
FRONTEND_URL="http://localhost:3000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."
    
    # Check if required files exist
    if [ ! -f "$BACKEND_DIR/app.py" ]; then
        error "Backend app.py not found"
        exit 1
    fi
    
    if [ ! -f "$FRONTEND_DIR/package.json" ]; then
        error "Frontend package.json not found"
        exit 1
    fi
    
    # Check environment files
    if [ ! -f ".env.production" ]; then
        warning "No .env.production file found"
    fi
    
    success "Pre-deployment checks passed"
}

# Backend deployment
deploy_backend() {
    log "Deploying backend..."
    
    cd $BACKEND_DIR
    
    # Install dependencies
    log "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Run database migrations
    log "Running database migrations..."
    python -c "
from database import init_database
import asyncio
asyncio.run(init_database())
"
    
    # Start backend in background
    log "Starting backend server..."
    python run_simple.py &
    BACKEND_PID=$!
    
    cd ..
    
    # Wait for backend to start
    sleep 5
    
    # Health check
    if curl -f $HEALTH_CHECK_URL > /dev/null 2>&1; then
        success "Backend is healthy"
    else
        error "Backend health check failed"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
}

# Frontend deployment
deploy_frontend() {
    log "Deploying frontend..."
    
    cd $FRONTEND_DIR
    
    # Install dependencies
    log "Installing Node.js dependencies..."
    npm ci
    
    # Build frontend
    log "Building frontend..."
    npm run build
    
    # Start frontend in background
    log "Starting frontend server..."
    npm start &
    FRONTEND_PID=$!
    
    cd ..
    
    # Wait for frontend to start
    sleep 10
    
    success "Frontend deployed"
}

# Post-deployment verification
post_deployment_verification() {
    log "Running post-deployment verification..."
    
    # Check backend endpoints
    log "Testing backend endpoints..."
    
    endpoints=(
        "/health"
        "/api/v1/health/"
        "/api/v1/users/me"
        "/api/v1/campaigns/"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f "http://localhost:8000$endpoint" > /dev/null 2>&1; then
            success "✓ $endpoint is responding"
        else
            warning "✗ $endpoint is not responding"
        fi
    done
    
    # Check frontend
    log "Testing frontend..."
    if curl -f $FRONTEND_URL > /dev/null 2>&1; then
        success "✓ Frontend is responding"
    else
        warning "✗ Frontend is not responding"
    fi
}

# Cleanup function
cleanup() {
    log "Cleaning up..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Main deployment flow
main() {
    log "Starting Raptorflow deployment..."
    
    pre_deployment_checks
    deploy_backend
    deploy_frontend
    post_deployment_verification
    
    success "🎉 Raptorflow deployment completed successfully!"
    
    echo ""
    echo "📊 Deployment Summary:"
    echo "  Backend: http://localhost:8000"
    echo "  Frontend: http://localhost:3000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "🔍 To check logs:"
    echo "  Backend: Check terminal output"
    echo "  Frontend: Check browser console"
    echo ""
    echo "⚠️  Press Ctrl+C to stop services"
    
    # Keep services running
    wait
}

# Run main function
main
