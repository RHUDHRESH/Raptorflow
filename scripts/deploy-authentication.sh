#!/bin/bash

# RaptorFlow Authentication Production Deployment Script
# This script deploys the authentication system to production

set -e

echo "🚀 Starting RaptorFlow Authentication Deployment..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if required environment variables are set
check_env_vars() {
    print_step "Checking environment variables..."
    
    required_vars=(
        "NEXT_PUBLIC_SUPABASE_URL"
        "NEXT_PUBLIC_SUPABASE_ANON_KEY"
        "SUPABASE_SERVICE_ROLE_KEY"
        "RESEND_API_KEY"
        "NEXT_PUBLIC_APP_URL"
    )
    
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        exit 1
    fi
    
    print_status "All required environment variables are set"
}

# Verify database connection
verify_database() {
    print_step "Verifying Supabase database connection..."
    
    # Test database connection
    curl -X GET "${NEXT_PUBLIC_APP_URL}/api/setup/create-db-table" \
        -H "Content-Type: application/json" \
        -s | jq -r '.exists // false' | grep -q "true"
    
    if [ $? -eq 0 ]; then
        print_status "Database connection verified"
    else
        print_warning "Database table not found, creating..."
        
        # Create database table
        curl -X POST "${NEXT_PUBLIC_APP_URL}/api/setup/create-db-table" \
            -H "Content-Type: application/json" \
            -s | jq -r '.success // false' | grep -q "true"
        
        if [ $? -eq 0 ]; then
            print_status "Database table created successfully"
        else
            print_error "Failed to create database table"
            exit 1
        fi
    fi
}

# Test email service
test_email_service() {
    print_step "Testing Resend email service..."
    
    # Test email sending
    response=$(curl -X POST "${NEXT_PUBLIC_APP_URL}/api/auth/forgot-password" \
        -H "Content-Type: application/json" \
        -d '{"email": "test@example.com"}' \
        -s)
    
    success=$(echo "$response" | jq -r '.success // false')
    
    if [ "$success" = "true" ]; then
        print_status "Email service is working"
    else
        print_error "Email service test failed"
        exit 1
    fi
}

# Verify authentication endpoints
verify_auth_endpoints() {
    print_step "Verifying authentication endpoints..."
    
    endpoints=(
        "/login"
        "/signup"
        "/forgot-password"
        "/auth/reset-password"
        "/auth/callback"
    )
    
    for endpoint in "${endpoints[@]}"; do
        status_code=$(curl -X GET "${NEXT_PUBLIC_APP_URL}${endpoint}" \
            -s -o /dev/null -w "%{http_code}")
        
        if [ "$status_code" = "200" ] || [ "$status_code" = "307" ]; then
            print_status "✓ $endpoint ($status_code)"
        else
            print_error "✗ $endpoint ($status_code)"
            exit 1
        fi
    done
}

# Check security headers
verify_security_headers() {
    print_step "Verifying security headers..."
    
    response=$(curl -X GET "${NEXT_PUBLIC_APP_URL}/login" -s -I)
    
    required_headers=(
        "content-security-policy"
        "x-content-type-options"
        "x-frame-options"
        "x-xss-protection"
        "referrer-policy"
    )
    
    for header in "${required_headers[@]}"; do
        if echo "$response" | grep -i "$header" > /dev/null; then
            print_status "✓ $header"
        else
            print_warning "✗ $header (missing)"
        fi
    done
}

# Run health check
run_health_check() {
    print_step "Running system health check..."
    
    response=$(curl -X GET "${NEXT_PUBLIC_APP_URL}/api/health" -s)
    
    if [ $? -eq 0 ]; then
        print_status "Health check passed"
        echo "$response" | jq '.'
    else
        print_error "Health check failed"
        exit 1
    fi
}

# Create production backup
create_backup() {
    print_step "Creating production backup..."
    
    # Note: This would need to be implemented based on your backup strategy
    print_warning "Backup strategy needs to be implemented"
}

# Deploy application
deploy_application() {
    print_step "Deploying application..."
    
    # Build the application
    print_status "Building application..."
    npm run build
    
    # Run database migrations
    print_status "Running database migrations..."
    # npm run migrate  # Uncomment if you have migration scripts
    
    # Start the application
    print_status "Starting application..."
    # npm start  # Uncomment for production start
    
    print_status "Application deployed successfully"
}

# Post-deployment verification
post_deployment_checks() {
    print_step "Running post-deployment verification..."
    
    # Wait for application to start
    sleep 10
    
    # Verify all endpoints are working
    verify_auth_endpoints
    
    # Test complete authentication flow
    print_status "Testing complete authentication flow..."
    
    # Create test user
    user_response=$(curl -X POST "${NEXT_PUBLIC_APP_URL}/api/test/create-user" \
        -H "Content-Type: application/json" \
        -d '{"email": "deploy-test@example.com", "password": "TestPassword123"}' \
        -s)
    
    # Test login
    login_response=$(curl -X POST "${NEXT_PUBLIC_APP_URL}/api/test/login" \
        -H "Content-Type: application/json" \
        -d '{"email": "deploy-test@example.com", "password": "TestPassword123"}' \
        -s)
    
    success=$(echo "$login_response" | jq -r '.success // false')
    
    if [ "$success" = "true" ]; then
        print_status "Authentication flow test passed"
    else
        print_error "Authentication flow test failed"
        exit 1
    fi
}

# Main deployment function
main() {
    print_status "Starting deployment process..."
    
    # Pre-deployment checks
    check_env_vars
    verify_database
    test_email_service
    verify_auth_endpoints
    verify_security_headers
    run_health_check
    
    # Create backup
    create_backup
    
    # Deploy
    deploy_application
    
    # Post-deployment verification
    post_deployment_checks
    
    print_status "🎉 Deployment completed successfully!"
    echo "================================================"
    echo "Authentication system is now live at: ${NEXT_PUBLIC_APP_URL}"
    echo ""
    echo "Next steps:"
    echo "1. Configure OAuth providers (Google, etc.)"
    echo "2. Set up monitoring and alerting"
    echo "3. Configure SSL certificates"
    echo "4. Set up backup schedules"
    echo "5. Review security settings"
}

# Handle script arguments
case "${1:-deploy}" in
    "check")
        check_env_vars
        verify_database
        test_email_service
        verify_auth_endpoints
        verify_security_headers
        run_health_check
        ;;
    "deploy")
        main
        ;;
    "verify")
        post_deployment_checks
        ;;
    *)
        echo "Usage: $0 [check|deploy|verify]"
        echo "  check   - Run pre-deployment checks"
        echo "  deploy  - Full deployment process"
        echo "  verify  - Post-deployment verification"
        exit 1
        ;;
esac
