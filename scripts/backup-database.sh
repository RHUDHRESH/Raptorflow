#!/bin/bash

# Supabase Database Backup Script
# This script creates automated backups of the Supabase database

set -euo pipefail

# Configuration
BACKUP_DIR="/backups/supabase"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="raptorflow_backup_${DATE}"
RETENTION_DAYS=30
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Send notification to Slack
notify_slack() {
    local message="$1"
    local color="${2:-good}"
    
    if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\", \"color\":\"$color\"}" \
            "$SLACK_WEBHOOK_URL" || true
    fi
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

# Create backup directory
create_backup_dir() {
    mkdir -p "$BACKUP_DIR"
    log "Created backup directory: $BACKUP_DIR"
}

# Perform database backup
backup_database() {
    log "Starting database backup..."
    
    # Use Supabase CLI to create backup
    if ! supabase db dump --db-url "$SUPABASE_URL" --data-only --file "$BACKUP_DIR/${BACKUP_NAME}.sql"; then
        error "Failed to create database backup"
        notify_slack "❌ Database backup failed for Raptorflow" "danger"
        exit 1
    fi
    
    # Compress the backup
    gzip "$BACKUP_DIR/${BACKUP_NAME}.sql"
    
    log "Database backup created: ${BACKUP_NAME}.sql.gz"
}

# Create schema backup
backup_schema() {
    log "Starting schema backup..."
    
    if ! supabase db dump --db-url "$SUPABASE_URL" --schema-only --file "$BACKUP_DIR/${BACKUP_NAME}_schema.sql"; then
        error "Failed to create schema backup"
        notify_slack "❌ Schema backup failed for Raptorflow" "danger"
        exit 1
    fi
    
    # Compress the backup
    gzip "$BACKUP_DIR/${BACKUP_NAME}_schema.sql"
    
    log "Schema backup created: ${BACKUP_NAME}_schema.sql.gz"
}

# Upload to Google Cloud Storage
upload_to_gcs() {
    log "Uploading backups to Google Cloud Storage..."
    
    # Upload data backup
    if ! gsutil cp "$BACKUP_DIR/${BACKUP_NAME}.sql.gz" "gs://${GCP_BUCKET_NAME}/backups/database/"; then
        error "Failed to upload data backup to GCS"
        notify_slack "❌ Failed to upload data backup to GCS" "danger"
        exit 1
    fi
    
    # Upload schema backup
    if ! gsutil cp "$BACKUP_DIR/${BACKUP_NAME}_schema.sql.gz" "gs://${GCP_BUCKET_NAME}/backups/schema/"; then
        error "Failed to upload schema backup to GCS"
        notify_slack "❌ Failed to upload schema backup to GCS" "danger"
        exit 1
    fi
    
    log "Backups uploaded to GCS successfully"
}

# Clean up old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    # Clean local backups
    find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete
    
    # Clean GCS backups
    gsutil ls "gs://${GCP_BUCKET_NAME}/backups/database/" | \
        while read -r line; do
            file_date=$(echo "$line" | grep -o '[0-9]\{8\}_[0-9]\{6\}' || true)
            if [[ -n "$file_date" ]]; then
                file_timestamp=$(date -d "${file_date:0:8} ${file_date:9:2}:${file_date:11:2}:${file_date:13:2}" +%s 2>/dev/null || true)
                if [[ -n "$file_timestamp" ]]; then
                    cutoff_timestamp=$(date -d "$RETENTION_DAYS days ago" +%s)
                    if (( file_timestamp < cutoff_timestamp )); then
                        gsutil rm "$line" || true
                    fi
                fi
            fi
        done
    
    log "Old backups cleaned up"
}

# Verify backup integrity
verify_backup() {
    log "Verifying backup integrity..."
    
    # Check if files exist and are not empty
    if [[ ! -s "$BACKUP_DIR/${BACKUP_NAME}.sql.gz" ]]; then
        error "Data backup file is empty or missing"
        exit 1
    fi
    
    if [[ ! -s "$BACKUP_DIR/${BACKUP_NAME}_schema.sql.gz" ]]; then
        error "Schema backup file is empty or missing"
        exit 1
    fi
    
    # Test gzip integrity
    if ! gzip -t "$BACKUP_DIR/${BACKUP_NAME}.sql.gz"; then
        error "Data backup file is corrupted"
        exit 1
    fi
    
    if ! gzip -t "$BACKUP_DIR/${BACKUP_NAME}_schema.sql.gz"; then
        error "Schema backup file is corrupted"
        exit 1
    fi
    
    log "Backup integrity verified"
}

# Create backup manifest
create_manifest() {
    local manifest_file="$BACKUP_DIR/${BACKUP_NAME}_manifest.json"
    
    cat > "$manifest_file" << EOF
{
    "backup_name": "$BACKUP_NAME",
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "type": "full",
    "files": [
        {
            "name": "${BACKUP_NAME}.sql.gz",
            "type": "data",
            "size": $(stat -f%z "$BACKUP_DIR/${BACKUP_NAME}.sql.gz" 2>/dev/null || stat -c%s "$BACKUP_DIR/${BACKUP_NAME}.sql.gz"),
            "checksum": "$(sha256sum "$BACKUP_DIR/${BACKUP_NAME}.sql.gz" | cut -d' ' -f1)"
        },
        {
            "name": "${BACKUP_NAME}_schema.sql.gz",
            "type": "schema",
            "size": $(stat -f%z "$BACKUP_DIR/${BACKUP_NAME}_schema.sql.gz" 2>/dev/null || stat -c%s "$BACKUP_DIR/${BACKUP_NAME}_schema.sql.gz"),
            "checksum": "$(sha256sum "$BACKUP_DIR/${BACKUP_NAME}_schema.sql.gz" | cut -d' ' -f1)"
        }
    ],
    "retention_days": $RETENTION_DAYS,
    "environment": "${ENVIRONMENT:-development}"
}
EOF
    
    # Upload manifest
    gsutil cp "$manifest_file" "gs://${GCP_BUCKET_NAME}/backups/manifests/"
    
    log "Backup manifest created and uploaded"
}

# Main execution
main() {
    log "Starting database backup process..."
    
    check_env
    create_backup_dir
    backup_database
    backup_schema
    verify_backup
    upload_to_gcs
    create_manifest
    cleanup_old_backups
    
    # Clean up local files
    rm -f "$BACKUP_DIR/${BACKUP_NAME}.sql.gz"
    rm -f "$BACKUP_DIR/${BACKUP_NAME}_schema.sql.gz"
    rm -f "$BACKUP_DIR/${BACKUP_NAME}_manifest.json"
    
    log "Database backup completed successfully!"
    notify_slack "✅ Database backup completed for Raptorflow (${BACKUP_NAME})" "good"
}

# Handle errors
trap 'error "Backup script failed"; notify_slack "❌ Database backup script failed for Raptorflow" "danger"; exit 1' ERR

# Run main function
main "$@"
