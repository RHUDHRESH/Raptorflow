#!/bin/bash
"""
Raptorflow Agent Deployment Script
=================================

Automated deployment script for Raptorflow agent system
with health checks, rollback capability, and proper service management.

Usage:
    ./scripts/deploy_agents.sh [environment] [options]

Options:
    --environment <env>    Deployment environment (development|staging|production)
    --skip-health-check     Skip pre-deployment health check
    --force-rollback       Force rollback to previous version
    --dry-run            Show what would be deployed without actually deploying
    --backup              Create backup before deployment
    --workers <num>       Number of worker instances to deploy

Examples:
    ./scripts/deploy_agents.sh --environment production --backup
    ./scripts/deploy_agents.sh --environment staging --dry-run
    ./scripts/deploy_agents.sh --environment production --workers 5
"""

set -euo pipefail

# Configuration
DEFAULT_ENVIRONMENT="development"
DEFAULT_WORKERS=3
HEALTH_CHECK_TIMEOUT=30
ROLLBACK_TIMEOUT=300
DEPLOYMENT_TIMEOUT=600

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Global variables
ENVIRONMENT=""
DRY_RUN=false
SKIP_HEALTH_CHECK=false
FORCE_ROLLBACK=false
CREATE_BACKUP=false
WORKERS_COUNT=""
DEPLOYMENT_ID=""
BACKUP_DIR=""
CURRENT_DIR=""
LOG_FILE=""

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")  echo -e "${GREEN}[INFO]${NC}  $timestamp - $message" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC}  $timestamp - $message" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} $timestamp - $message" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} $timestamp - $message" ;;
        *) echo -e "${BLUE}[INFO]${NC}  $timestamp - $message" ;;
    esac
}

# Error handling
handle_error() {
    local error_code=$1
    local error_message=$2
    local line_number=$3
    
    log "ERROR" "Deployment failed at line $line_number: $error_message"
    cleanup_on_error
    exit $error_code
}

# Cleanup function
cleanup_on_error() {
    log "INFO" "Cleaning up deployment resources..."
    
    # Kill any background processes
    if [[ -n "$DEPLOYMENT_ID" ]]; then
        pkill -f "raptorflow_agent_$DEPLOYMENT_ID" 2>/dev/null || true
    fi
    
    # Remove temporary files
    if [[ -n "$BACKUP_DIR" ]] && [[ -d "$BACKUP_DIR" ]]; then
        rm -rf "$BACKUP_DIR"
    fi
    
    # Reset variables
    ENVIRONMENT=""
    DRY_RUN=false
    SKIP_HEALTH_CHECK=false
    FORCE_ROLLBACK=false
    CREATE_BACKUP=false
    WORKERS_COUNT=""
    DEPLOYMENT_ID=""
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment)
                shift
                ENVIRONMENT="$1"
                shift
                ;;
            --skip-health-check)
                SKIP_HEALTH_CHECK=true
                shift
                ;;
            --force-rollback)
                FORCE_ROLLBACK=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --backup)
                CREATE_BACKUP=true
                shift
                ;;
            --workers)
                shift
                WORKERS_COUNT="$1"
                shift
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Set defaults
    ENVIRONMENT="${ENVIRONMENT:-$DEFAULT_ENVIRONMENT}"
    WORKERS_COUNT="${WORKERS_COUNT:-$DEFAULT_WORKERS}"
}

# Validate environment
validate_environment() {
    case $ENVIRONMENT in
        development|staging|production)
            log "INFO" "Environment validated: $ENVIRONMENT"
            ;;
        *)
            log "ERROR" "Invalid environment: $ENVIRONMENT. Must be one of: development, staging, production"
            exit 1
            ;;
    esac
}

# Check prerequisites
check_prerequisites() {
    log "INFO" "Checking deployment prerequisites..."
    
    # Check if required commands are available
    local required_commands=("docker" "docker-compose" "curl" "jq")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log "ERROR" "Required command not found: $cmd"
            exit 1
        fi
    done
    
    # Check if configuration files exist
    local config_files=("config/raptorflow.yaml" "docker-compose.yml" "Dockerfile")
    for file in "${config_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log "ERROR" "Required configuration file not found: $file"
            exit 1
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log "ERROR" "Docker daemon is not running"
        exit 1
    fi
    
    log "SUCCESS" "Prerequisites check passed"
}

# Health check function
health_check() {
    if [[ "$SKIP_HEALTH_CHECK" == "true" ]]; then
        log "INFO" "Skipping health check as requested"
        return 0
    fi
    
    log "INFO" "Performing pre-deployment health check..."
    
    # Check if services are already running
    local running_services=$(docker ps --format "table {{.Names}}" --filter "name=raptorflow" | grep -c "raptorflow")
    
    if [[ $running_services -gt 0 ]]; then
        log "WARN" "Raptorflow services are already running"
        if [[ "$FORCE_ROLLBACK" != "true" ]]; then
            log "ERROR" "Cannot deploy while services are running. Use --force-rollback to stop them first."
            exit 1
        fi
    fi
    
    # Check database connectivity
    local db_check=$(timeout $HEALTH_CHECK_TIMEOUT bash -c "
        if [[ '$ENVIRONMENT' == 'production' ]]; then
            curl -f --connect-timeout 10 --max-time 10 '$DATABASE_URL' || echo 'DB_UNREACHABLE'
        else
            echo 'DB_OK'
        fi
    " 2>/dev/null)
    
    if [[ "$db_check" != "DB_OK" ]]; then
        log "ERROR" "Database health check failed"
        exit 1
    fi
    
    # Check Redis connectivity
    local redis_check=$(timeout $HEALTH_CHECK_TIMEOUT bash -c "
        curl -f --connect-timeout 10 --max-time 10 '$REDIS_URL' || echo 'REDIS_UNREACHABLE'
    " 2>/dev/null)
    
    if [[ "$redis_check" != "REDIS_OK" ]]; then
        log "ERROR" "Redis health check failed"
        exit 1
    fi
    
    log "SUCCESS" "Health check passed"
    return 0
}

# Create backup
create_backup() {
    if [[ "$CREATE_BACKUP" != "true" ]]; then
        return 0
    fi
    
    log "INFO" "Creating backup before deployment..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup configuration files
    cp config/raptorflow.yaml "$BACKUP_DIR/" 2>/dev/null || {
        log "ERROR" "Failed to backup configuration files"
        exit 1
    }
    
    # Backup database (if PostgreSQL)
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log "INFO" "Creating database backup..."
        pg_dump "$DATABASE_URL" > "$BACKUP_DIR/database_backup.sql" 2>/dev/null || {
            log "ERROR" "Failed to backup database"
            exit 1
        }
    fi
    
    # Backup current running containers
    docker ps --format "table {{.Names}}\t{{.Image}}" > "$BACKUP_DIR/containers.txt" 2>/dev/null
    
    log "SUCCESS" "Backup created in $BACKUP_DIR"
}

# Rollback function
rollback() {
    if [[ ! -f "backups/rollback_info.txt" ]]; then
        log "ERROR" "No rollback information found"
        exit 1
    fi
    
    log "WARN" "Rolling back to previous deployment..."
    
    # Read rollback info
    local prev_backup_dir=$(cat "backups/rollback_info.txt" | head -1)
    local prev_image=$(cat "backups/rollback_info.txt" | head -2 | tail -1)
    
    # Stop current services
    docker-compose down 2>/dev/null || true
    
    # Restore previous version
    if [[ -f "$prev_backup_dir/docker-compose.yml" ]]; then
        docker-compose -f "$prev_backup_dir/docker-compose.yml" up -d
        log "SUCCESS" "Rollback completed to $prev_backup_dir"
    else
        log "ERROR" "Failed to rollback: backup files not found"
        exit 1
    fi
}

# Deploy function
deploy() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log "INFO" "DRY RUN: Would deploy with $WORKERS_COUNT workers to $ENVIRONMENT environment"
        return 0
    fi
    
    log "INFO" "Starting deployment to $ENVIRONMENT environment..."
    
    # Generate deployment ID
    DEPLOYMENT_ID="deploy_$(date +%Y%m%d_%H%M%S)"
    
    # Update environment-specific configuration
    update_environment_config
    
    # Build and deploy Docker containers
    local compose_file="docker-compose.$ENVIRONMENT.yml"
    
    if [[ ! -f "$compose_file" ]]; then
        log "WARN" "Environment-specific compose file not found: $compose_file, using default"
        compose_file="docker-compose.yml"
    fi
    
    # Deploy with specified number of workers
    WORKERS_COUNT=${WORKERS_COUNT:-3}
    
    log "INFO" "Deploying $WORKERS_COUNT worker instances..."
    
    # Scale services
    docker-compose -f "$compose_file" up -d --scale raptorflow_agent=$WORKERS_COUNT
    
    # Wait for services to be healthy
    log "INFO" "Waiting for services to be healthy..."
    local health_wait_time=0
    local max_health_wait=120
    
    while [[ $health_wait_time -lt $max_health_wait ]]; do
        local healthy=true
        
        # Check each service
        local services=("raptorflow_agent" "raptorflow_loadbalancer" "raptorflow_redis" "raptorflow_db")
        for service in "${services[@]}"; do
            if ! docker ps --format "table {{.Status}}" --filter "name=$service" | grep -q "Up"; then
                healthy=false
                break
            fi
        done
        
        if [[ "$healthy" == "true" ]]; then
            log "SUCCESS" "All services are healthy"
            break
        fi
        
        sleep 5
        health_wait_time=$((health_wait_time + 5))
    done
    
    # Save rollback information
    echo "$BACKUP_DIR" > "backups/rollback_info.txt"
    echo "$(docker images --format "table {{.Repository}}\t{{.Tag}}" | grep raptorflow | head -1)" >> "backups/rollback_info.txt"
    
    # Run post-deployment health check
    post_deployment_health_check
    
    log "SUCCESS" "Deployment completed successfully (ID: $DEPLOYMENT_ID)"
}

# Update environment-specific configuration
update_environment_config() {
    case $ENVIRONMENT in
        production)
            # Production-specific settings
            log "INFO" "Applying production configuration..."
            # Set production environment variables
            export RAPTORFLOW_ENV=production
            export LOG_LEVEL=INFO
            ;;
        staging)
            # Staging-specific settings
            log "INFO" "Applying staging configuration..."
            export RAPTORFLOW_ENV=staging
            export LOG_LEVEL=DEBUG
            ;;
        development)
            # Development-specific settings
            log "INFO" "Applying development configuration..."
            export RAPTORFLOW_ENV=development
            export LOG_LEVEL=DEBUG
            ;;
        *)
            log "ERROR" "Unknown environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
}

# Post-deployment health check
post_deployment_health_check() {
    log "INFO" "Running post-deployment health check..."
    
    local services_healthy=true
    local services=("raptorflow_agent" "raptorflow_loadbalancer" "raptorflow_redis" "raptorflow_db")
    
    for service in "${services[@]}"; do
        if ! docker ps --format "table {{.Status}}" --filter "name=$service" | grep -q "Up"; then
            services_healthy=false
            log "ERROR" "Service $service is not healthy"
        fi
    done
    
    if [[ "$services_healthy" == "true" ]]; then
        log "SUCCESS" "Post-deployment health check passed"
    else
        log "ERROR" "Post-deployment health check failed - some services are unhealthy"
        exit 1
    fi
}

# Show deployment status
show_status() {
    log "INFO" "Current deployment status:"
    
    if [[ -n "$DEPLOYMENT_ID" ]]; then
        echo "Deployment ID: $DEPLOYMENT_ID"
    fi
    
    echo "Environment: $ENVIRONMENT"
    echo "Workers: $WORKERS_COUNT"
    
    # Show running services
    echo "Running services:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=raptorflow"
    
    # Show recent logs
    if [[ -n "$DEPLOYMENT_ID" ]]; then
        echo "Recent logs:"
        docker logs --tail 50 --since 10m raptorflow_agent 2>/dev/null || true
    fi
}

# Cleanup function
cleanup() {
    log "INFO" "Cleaning up deployment resources..."
    
    # Remove temporary files
    if [[ -n "$BACKUP_DIR" ]] && [[ -d "$BACKUP_DIR" ]]; then
        rm -rf "$BACKUP_DIR"
    fi
    
    log "INFO" "Cleanup completed"
}

# Main script logic
main() {
    # Set up script directory
    CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$CURRENT_DIR"
    
    # Create log file
    LOG_FILE="logs/deploy_$(date +%Y%m%d_%H%M%S).log"
    mkdir -p logs
    
    # Redirect all output to log file
    exec 1> >(tee -a "$LOG_FILE")
    
    log "INFO" "=== Raptorflow Agent Deployment Script ==="
    log "INFO" "Starting deployment process..."
    
    # Parse arguments
    parse_arguments "$@"
    
    # Validate environment
    validate_environment
    
    # Check prerequisites
    check_prerequisites
    
    # Handle force rollback
    if [[ "$FORCE_ROLLBACK" == "true" ]]; then
        rollback
        exit 0
    fi
    
    # Create backup if requested
    create_backup
    
    # Perform deployment
    deploy
    
    log "INFO" "Deployment process completed"
}

# Signal handlers
trap 'cleanup_on_error' ERR
trap 'cleanup' EXIT

# Run main function
main "$@"
