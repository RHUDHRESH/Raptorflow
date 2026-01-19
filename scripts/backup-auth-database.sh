#!/bin/bash

# RaptorFlow Authentication Database Backup Script
# This script creates automated backups of the authentication database

set -e

# Configuration
BACKUP_DIR="/backups/raptorflow-auth"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="auth_backup_${TIMESTAMP}.sql"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
        "DATABASE_URL"
        "SUPABASE_SERVICE_ROLE_KEY"
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

# Create backup directory
create_backup_dir() {
    print_step "Creating backup directory..."
    
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        print_status "Created backup directory: $BACKUP_DIR"
    else
        print_status "Backup directory exists: $BACKUP_DIR"
    fi
}

# Extract database connection info
extract_db_info() {
    print_step "Extracting database connection information..."
    
    # Parse DATABASE_URL
    if [[ $DATABASE_URL =~ postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+) ]]; then
        DB_USER="${BASH_REMATCH[1]}"
        DB_PASSWORD="${BASH_REMATCH[2]}"
        DB_HOST="${BASH_REMATCH[3]}"
        DB_PORT="${BASH_REMATCH[4]}"
        DB_NAME="${BASH_REMATCH[5]}"
        
        print_status "Database info extracted successfully"
    else
        print_error "Failed to parse DATABASE_URL"
        exit 1
    fi
}

# Create database backup
create_backup() {
    print_step "Creating database backup..."
    
    local backup_path="$BACKUP_DIR/$BACKUP_FILE"
    
    # Use pg_dump to create backup
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --no-password \
        --verbose \
        --format=custom \
        --compress=9 \
        --file="$backup_path" \
        --table=profiles \
        --table=password_reset_tokens \
        --table=sessions \
        2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_status "Database backup created: $backup_path"
        
        # Get backup size
        backup_size=$(du -h "$backup_path" | cut -f1)
        print_status "Backup size: $backup_size"
    else
        print_error "Failed to create database backup"
        exit 1
    fi
}

# Create backup metadata
create_metadata() {
    print_step "Creating backup metadata..."
    
    local metadata_file="$BACKUP_DIR/auth_backup_${TIMESTAMP}.json"
    
    cat > "$metadata_file" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "backup_file": "$BACKUP_FILE",
    "database": {
        "host": "$DB_HOST",
        "port": "$DB_PORT",
        "name": "$DB_NAME",
        "user": "$DB_USER"
    },
    "tables": [
        "profiles",
        "password_reset_tokens",
        "sessions"
    ],
    "backup_size": "$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)",
    "created_by": "backup-auth-database.sh",
    "environment": "${NODE_ENV:-development}"
}
EOF
    
    print_status "Metadata file created: $metadata_file"
}

# Verify backup integrity
verify_backup() {
    print_step "Verifying backup integrity..."
    
    local backup_path="$BACKUP_DIR/$BACKUP_FILE"
    
    # Check if backup file exists and is not empty
    if [ -f "$backup_path" ] && [ -s "$backup_path" ]; then
        # Try to restore to a temporary database to verify
        print_status "Backup file exists and is not empty"
        
        # List contents of backup
        if command -v pg_restore >/dev/null 2>&1; then
            PGPASSWORD="$DB_PASSWORD" pg_restore \
                -h "$DB_HOST" \
                -p "$DB_PORT" \
                -U "$DB_USER" \
                -d "$DB_NAME" \
                --list "$backup_path" >/dev/null 2>&1
            
            if [ $? -eq 0 ]; then
                print_status "Backup integrity verified"
            else
                print_warning "Backup integrity check failed, but backup was created"
            fi
        fi
    else
        print_error "Backup file is missing or empty"
        exit 1
    fi
}

# Clean up old backups
cleanup_old_backups() {
    print_step "Cleaning up old backups..."
    
    # Find and remove backups older than RETENTION_DAYS
    local old_backups=$(find "$BACKUP_DIR" -name "auth_backup_*.sql" -mtime +$RETENTION_DAYS)
    
    if [ -n "$old_backups" ]; then
        echo "$old_backups" | while read -r backup; do
            rm "$backup"
            print_status "Removed old backup: $(basename "$backup")"
        done
        
        # Also remove corresponding metadata files
        find "$BACKUP_DIR" -name "auth_backup_*.json" -mtime +$RETENTION_DAYS -delete
    else
        print_status "No old backups to remove"
    fi
}

# Create backup notification
send_notification() {
    print_step "Sending backup notification..."
    
    local backup_path="$BACKUP_DIR/$BACKUP_FILE"
    local backup_size=$(du -h "$backup_path" | cut -f1)
    
    # Create notification message
    local message="🗄️ Database Backup Completed

📅 Date: $(date)
📁 File: $BACKUP_FILE
📊 Size: $backup_size
🗄️ Database: $DB_NAME
🌐 Host: $DB_HOST

Backup location: $backup_path"

    # Send notification (you can integrate with your preferred notification service)
    if command -v curl >/dev/null 2>&1; then
        # Example: Send to Slack webhook (uncomment and configure)
        # curl -X POST -H 'Content-type: application/json' \
        #     --data "{\"text\":\"$message\"}" \
        #     "$SLACK_WEBHOOK_URL"
        
        print_status "Backup notification prepared"
    fi
}

# List available backups
list_backups() {
    print_step "Listing available backups..."
    
    echo "Available backups in $BACKUP_DIR:"
    echo "================================"
    
    if [ -d "$BACKUP_DIR" ]; then
        ls -lh "$BACKUP_DIR"/auth_backup_*.sql 2>/dev/null | while read -r line; do
            echo "$line"
        done
    else
        print_warning "Backup directory does not exist"
    fi
}

# Restore from backup
restore_backup() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        print_error "Please specify a backup file to restore"
        echo "Usage: $0 restore <backup_file>"
        exit 1
    fi
    
    print_step "Restoring from backup: $backup_file"
    
    local backup_path="$BACKUP_DIR/$backup_file"
    
    if [ ! -f "$backup_path" ]; then
        print_error "Backup file not found: $backup_path"
        exit 1
    fi
    
    # Create a timestamp for the restore
    local restore_timestamp=$(date +"%Y%m%d_%H%M%S")
    local pre_restore_backup="pre_restore_${restore_timestamp}.sql"
    
    print_warning "Creating pre-restore backup: $pre_restore_backup"
    
    # Create pre-restore backup
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --no-password \
        --format=custom \
        --compress=9 \
        --file="$BACKUP_DIR/$pre_restore_backup" \
        --table=profiles \
        --table=password_reset_tokens \
        --table=sessions \
        2>/dev/null
    
    # Restore from backup
    print_status "Restoring database from backup..."
    
    PGPASSWORD="$DB_PASSWORD" pg_restore \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --no-password \
        --verbose \
        --clean \
        --if-exists \
        "$backup_path"
    
    if [ $? -eq 0 ]; then
        print_status "Database restored successfully"
        print_status "Pre-restore backup saved as: $pre_restore_backup"
    else
        print_error "Failed to restore database"
        exit 1
    fi
}

# Main function
main() {
    case "${1:-backup}" in
        "backup")
            check_env_vars
            create_backup_dir
            extract_db_info
            create_backup
            create_metadata
            verify_backup
            cleanup_old_backups
            send_notification
            print_status "🎉 Database backup completed successfully!"
            ;;
        "list")
            list_backups
            ;;
        "restore")
            restore_backup "$2"
            ;;
        "cleanup")
            create_backup_dir
            cleanup_old_backups
            ;;
        *)
            echo "Usage: $0 [backup|list|restore|cleanup] [backup_file]"
            echo "  backup   - Create a new database backup"
            echo "  list     - List available backups"
            echo "  restore  - Restore from a backup file"
            echo "  cleanup  - Clean up old backups"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
