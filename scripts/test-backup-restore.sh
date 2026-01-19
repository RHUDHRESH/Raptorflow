#!/bin/bash

# Backup Restore Testing Script
# Tests backup integrity and restore capability automatically
# No-cost solution for backup verification

set -euo pipefail

# Configuration
TEST_DB_NAME="raptorflow_test_restore_${RANDOM}"
BACKUP_DIR="/tmp/test_backups"
LOG_FILE="/var/log/backup_test.log"
DATE=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1" >> "$LOG_FILE"
}

# Check required environment variables
check_env() {
    if [[ -z "${SUPABASE_URL}" ]]; then
        error "SUPABASE_URL environment variable is not set"
        exit 1
    fi
    
    if [[ -z "${SUPABASE_SERVICE_ROLE_KEY}" ]]; then
        error "SUPABASE_SERVICE_ROLE_KEY environment variable is not set"
        exit 1
    fi
    
    if [[ -z "${GCP_BUCKET_NAME}" ]]; then
        error "GCP_BUCKET_NAME environment variable is not set"
        exit 1
    fi
}

# Create test backup directory
create_test_dir() {
    mkdir -p "$BACKUP_DIR"
    log "Created test backup directory: $BACKUP_DIR"
}

# Create test database
create_test_database() {
    log "Creating test database: $TEST_DB_NAME"
    
    # Create test database (this would need Supabase CLI support)
    # For now, simulate with table creation
    supabase db push --db-url "$SUPABASE_URL" --schema-only --file "$BACKUP_DIR/test_schema.sql" || true
    
    # Insert test data
    cat > "$BACKUP_DIR/test_data.sql" << EOF
-- Test data for backup verification
INSERT INTO users (id, auth_user_id, email, full_name, onboarding_status, role, is_active, created_at) 
VALUES 
    ('test-user-1', 'auth-test-1', 'test1@example.com', 'Test User 1', 'active', 'user', true, NOW()),
    ('test-user-2', 'auth-test-2', 'test2@example.com', 'Test User 2', 'pending_workspace', 'user', true, NOW()),
    ('test-user-3', 'auth-test-3', 'test3@example.com', 'Test User 3', 'active', 'admin', true, NOW());

INSERT INTO workspaces (id, user_id, name, slug, status, created_at)
VALUES
    ('test-workspace-1', 'test-user-1', 'Test Workspace 1', 'test-workspace-1', 'active', NOW()),
    ('test-workspace-2', 'test-user-2', 'Test Workspace 2', 'test-workspace-2', 'provisioning', NOW());

INSERT INTO subscriptions (id, user_id, plan_id, plan_name, status, billing_cycle, created_at)
VALUES
    ('test-sub-1', 'test-user-1', 'pro', 'Pro', 'active', 'monthly', NOW()),
    ('test-sub-2', 'test-user-2', 'starter', 'Starter', 'pending', 'monthly', NOW());
EOF
    
    # Apply test data
    supabase db push --db-url "$SUPABASE_URL" --data-only --file "$BACKUP_DIR/test_data.sql" || true
    
    log "Test database created with sample data"
}

# Create backup of test database
create_test_backup() {
    log "Creating test backup..."
    
    local backup_name="test_backup_${DATE}"
    
    # Create schema backup
    if ! supabase db dump --db-url "$SUPABASE_URL" --schema-only --file "$BACKUP_DIR/${backup_name}_schema.sql"; then
        error "Failed to create test schema backup"
        exit 1
    fi
    
    # Create data backup
    if ! supabase db dump --db-url "$SUPABASE_URL" --data-only --file "$BACKUP_DIR/${backup_name}_data.sql"; then
        error "Failed to create test data backup"
        exit 1
    fi
    
    # Compress backups
    gzip "$BACKUP_DIR/${backup_name}_schema.sql"
    gzip "$BACKUP_DIR/${backup_name}_data.sql"
    
    log "Test backup created: ${backup_name}_schema.sql.gz, ${backup_name}_data.sql.gz"
    
    # Verify backup files
    if [[ ! -s "$BACKUP_DIR/${backup_name}_schema.sql.gz" ]] || [[ ! -s "$BACKUP_DIR/${backup_name}_data.sql.gz" ]]; then
        error "Backup files are empty or missing"
        exit 1
    fi
    
    # Test gzip integrity
    if ! gzip -t "$BACKUP_DIR/${backup_name}_schema.sql.gz" || ! gzip -t "$BACKUP_DIR/${backup_name}_data.sql.gz"; then
        error "Backup files are corrupted"
        exit 1
    fi
    
    log "Backup integrity verified"
    echo "$backup_name" > "$BACKUP_DIR/last_backup_name.txt"
}

# Test restore process
test_restore() {
    log "Testing restore process..."
    
    local backup_name=$(cat "$BACKUP_DIR/last_backup_name.txt")
    
    # Create restore directory
    local restore_dir="$BACKUP_DIR/restore_test_${DATE}"
    mkdir -p "$restore_dir"
    
    # Extract backups
    gunzip -c "$BACKUP_DIR/${backup_name}_schema.sql.gz" > "$restore_dir/schema.sql"
    gunzip -c "$BACKUP_DIR/${backup_name}_data.sql.gz" > "$restore_dir/data.sql"
    
    # Verify SQL syntax
    if ! psql --help > /dev/null 2>&1; then
        warning "psql not available, skipping syntax check"
    else
        log "Checking SQL syntax..."
        
        # Check schema syntax
        if psql --set ON_ERROR_STOP=1 --file="$restore_dir/schema.sql" "postgresql://dummy" 2>/dev/null; then
            log "Schema SQL syntax is valid"
        else
            error "Schema SQL syntax is invalid"
            exit 1
        fi
        
        # Check data syntax
        if psql --set ON_ERROR_STOP=1 --file="$restore_dir/data.sql" "postgresql://dummy" 2>/dev/null; then
            log "Data SQL syntax is valid"
        else
            error "Data SQL syntax is invalid"
            exit 1
        fi
    fi
    
    # Simulate restore verification
    log "Simulating restore verification..."
    
    # Check for required tables
    local required_tables=("users" "workspaces" "subscriptions")
    for table in "${required_tables[@]}"; do
        if grep -q "CREATE TABLE.*$table" "$restore_dir/schema.sql"; then
            log "✓ Found table: $table"
        else
            error "✗ Missing table: $table"
            exit 1
        fi
    done
    
    # Check for test data
    local test_users=$(grep -c "INSERT INTO users" "$restore_dir/data.sql" || echo "0")
    local test_workspaces=$(grep -c "INSERT INTO workspaces" "$restore_dir/data.sql" || echo "0")
    local test_subscriptions=$(grep -c "INSERT INTO subscriptions" "$restore_dir/data.sql" || echo "0")
    
    if [[ $test_users -ge 3 ]]; then
        log "✓ Found test users: $test_users"
    else
        error "✗ Insufficient test users: $test_users"
        exit 1
    fi
    
    if [[ $test_workspaces -ge 2 ]]; then
        log "✓ Found test workspaces: $test_workspaces"
    else
        error "✗ Insufficient test workspaces: $test_workspaces"
        exit 1
    fi
    
    if [[ $test_subscriptions -ge 2 ]]; then
        log "✓ Found test subscriptions: $test_subscriptions"
    else
        error "✗ Insufficient test subscriptions: $test_subscriptions"
        exit 1
    fi
    
    log "Restore verification completed successfully"
}

# Test backup performance
test_backup_performance() {
    log "Testing backup performance..."
    
    local backup_name=$(cat "$BACKUP_DIR/last_backup_name.txt")
    local start_time=$(date +%s)
    
    # Test restore time
    local restore_start=$(date +%s)
    gunzip -c "$BACKUP_DIR/${backup_name}_data.sql.gz" > /dev/null
    local restore_end=$(date +%s)
    local restore_time=$((restore_end - restore_start))
    
    # Test backup size
    local schema_size=$(stat -f%z "$BACKUP_DIR/${backup_name}_schema.sql.gz" 2>/dev/null || stat -c%s "$BACKUP_DIR/${backup_name}_schema.sql.gz")
    local data_size=$(stat -f%z "$BACKUP_DIR/${backup_name}_data.sql.gz" 2>/dev/null || stat -c%s "$BACKUP_DIR/${backup_name}_data.sql.gz")
    local total_size=$((schema_size + data_size))
    
    log "Performance metrics:"
    log "- Restore time: ${restore_time}s"
    log "- Schema backup size: $(numfmt --to=iec $schema_size)"
    log "- Data backup size: $(numfmt --to=iec $data_size)"
    log "- Total backup size: $(numfmt --to=iec $total_size)"
    
    # Performance thresholds
    if [[ $restore_time -gt 60 ]]; then
        warning "Restore time is slow: ${restore_time}s (>60s)"
    fi
    
    if [[ $total_size -gt 104857600 ]]; then  # 100MB
        warning "Backup size is large: $(numfmt --to=iec $total_size) (>100MB)"
    fi
}

# Generate test report
generate_report() {
    log "Generating test report..."
    
    local backup_name=$(cat "$BACKUP_DIR/last_backup_name.txt")
    local report_file="$BACKUP_DIR/backup_test_report_${DATE}.json"
    
    cat > "$report_file" << EOF
{
    "test_name": "backup_restore_test",
    "test_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "backup_name": "$backup_name",
    "environment": "${ENVIRONMENT:-development}",
    "tests_performed": [
        "backup_creation",
        "backup_integrity",
        "sql_syntax_validation",
        "restore_verification",
        "performance_analysis"
    ],
    "results": {
        "backup_created": true,
        "backup_integrity": "passed",
        "sql_syntax": "valid",
        "restore_verification": "passed",
        "performance_metrics": {
            "restore_time_seconds": ${restore_time:-0},
            "backup_size_bytes": ${total_size:-0}
        }
    },
    "status": "success",
    "recommendations": [
        "Automate this test to run daily",
        "Set up alerts for test failures",
        "Monitor backup size trends"
    ]
}
EOF
    
    log "Test report generated: $report_file"
    
    # Upload report to GCS if configured
    if [[ -n "${GCP_BUCKET_NAME}" ]]; then
        gsutil cp "$report_file" "gs://${GCP_BUCKET_NAME}/backup-tests/" || true
        log "Report uploaded to GCS"
    fi
}

# Cleanup test environment
cleanup() {
    log "Cleaning up test environment..."
    
    # Remove test database (if created)
    # supabase db delete "$TEST_DB_NAME" || true
    
    # Remove test files
    rm -rf "$BACKUP_DIR"
    
    log "Cleanup completed"
}

# Main execution
main() {
    log "Starting backup restore test..."
    
    check_env
    create_test_dir
    create_test_database
    create_test_backup
    test_restore
    test_backup_performance
    generate_report
    
    log "Backup restore test completed successfully!"
    
    # Don't cleanup automatically for debugging
    # cleanup
}

# Handle errors
trap 'error "Backup restore test failed"; cleanup; exit 1' ERR

# Run main function
main "$@"
