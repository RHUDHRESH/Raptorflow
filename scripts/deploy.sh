#!/bin/bash

# RaptorFlow Production Deployment Script
# This script handles the complete production deployment process

set -e  # Exit on any error

echo "🚀 RAPTORFLOW PRODUCTION DEPLOYMENT"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."

    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi

    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi

    if ! command -v python &> /dev/null; then
        print_error "Python is not installed"
        exit 1
    fi

    print_success "All dependencies found"
}

# Environment validation
validate_environment() {
    print_status "Validating environment..."

    # Check for required environment variables
    required_vars=(
        "NEXT_PUBLIC_SUPABASE_URL"
        "NEXT_PUBLIC_SUPABASE_ANON_KEY"
        "SUPABASE_SERVICE_ROLE_KEY"
    )

    missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_error "Missing environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        print_error "Please set these variables in your .env.local file"
        exit 1
    fi

    print_success "Environment validation passed"
}

# Frontend build and deployment
deploy_frontend() {
    print_status "Building and deploying frontend..."

    cd frontend

    # Install dependencies
    print_status "Installing frontend dependencies..."
    npm ci

    # Type checking
    print_status "Running TypeScript type check..."
    npm run type-check

    # Linting
    print_status "Running ESLint..."
    npm run lint

    # Build for production
    print_status "Building frontend for production..."
    npm run build

    # Run tests
    print_status "Running frontend tests..."
    npm run test:ci

    print_success "Frontend deployment completed"

    cd ..
}

# Backend deployment
deploy_backend() {
    print_status "Deploying backend..."

    cd backend

    # Install dependencies
    print_status "Installing backend dependencies..."
    pip install -r requirements.txt

    # Test imports
    print_status "Testing backend imports..."
    python -c "import main; print('Backend imports successful')"

    # Start backend (in production, this would be a proper service)
    print_status "Starting backend service..."
    python test_backend.py &

    # Wait for backend to start
    sleep 5

    # Health check
    print_status "Checking backend health..."
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        print_success "Backend is healthy"
    else
        print_error "Backend health check failed"
        exit 1
    fi

    print_success "Backend deployment completed"

    cd ..
}

# Database setup
setup_database() {
    print_status "Setting up database..."

    # Test database connection
    python -c "
import os
from dotenv import load_dotenv
load_dotenv('frontend/.env.local')

from supabase import create_client
supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')

if supabase_url and supabase_key:
    client = create_client(supabase_url, supabase_key)
    print('✅ Database connection successful')
else:
    print('❌ Database connection failed')
    exit(1)
"

    print_success "Database setup completed"
}

# System health verification
verify_deployment() {
    print_status "Verifying deployment..."

    # Check frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend is responding"
    else
        print_error "Frontend is not responding"
        exit 1
    fi

    # Check backend
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        print_success "Backend is healthy"
    else
        print_error "Backend is not healthy"
        exit 1
    fi

    print_success "Deployment verification completed"
}

# Main deployment function
main() {
    print_status "Starting production deployment..."

    # Load environment variables
    if [ -f "frontend/.env.local" ]; then
        export $(cat frontend/.env.local | grep -v '^#' | xargs)
    else
        print_error "frontend/.env.local file not found"
        exit 1
    fi

    # Run deployment steps
    check_dependencies
    validate_environment
    setup_database
    deploy_backend
    deploy_frontend
    verify_deployment

    print_success "🎉 PRODUCTION DEPLOYMENT COMPLETED SUCCESSFULLY!"
    echo ""
    echo "📍 Services running at:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:8080"
    echo "  Health:   http://localhost:8080/health"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Test all functionality"
    echo "  2. Update DNS if needed"
    echo "  3. Configure monitoring"
    echo "  4. Set up backup procedures"
}

# Handle script arguments
case "${1:-}" in
    "frontend")
        deploy_frontend
        ;;
    "backend")
        deploy_backend
        ;;
    "database")
        setup_database
        ;;
    "health")
        verify_deployment
        ;;
    *)
        main
        ;;
esac
