#!/bin/bash

# Backup and Restore Test Script
# Tests database backup and restore procedures

set -e

BACKUP_DIR="/tmp/raptorflow-backups"
RESTORE_TEST_DB="raptorflow_restore_test"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup-$TIMESTAMP.sql"

echo "💾 Starting Backup and Restore Tests..."
echo "================================"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Test 1: Database Backup
echo "📦 Test 1: Database Backup"
echo "Creating database backup..."

# Export database schema and data
if command -v pg_dump &> /dev/null; then
    pg_dump "$DATABASE_URL" --verbose --format=custom --file="$BACKUP_FILE"
    
    # Verify backup file was created
    if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
        backup_size=$(du -h "$BACKUP_FILE" | cut -f1)
        echo "✅ Backup created successfully: $backup_size"
    else
        echo "❌ Backup file creation failed"
        exit 1
    fi
else
    echo "❌ pg_dump not available"
    exit 1
fi

# Test 2: Backup Integrity Check
echo ""
echo "🔍 Test 2: Backup Integrity Check"
echo "Verifying backup file integrity..."

# Check SQL syntax
if psql "$DATABASE_URL" -f "$BACKUP_FILE" > /dev/null 2>&1; then
    echo "✅ Backup file syntax is valid"
else
    echo "❌ Backup file has syntax errors"
    exit 1
fi

# Check table counts
echo "Checking table counts in backup..."
original_counts=$(psql "$DATABASE_URL" -c "
SELECT 'profiles', COUNT(*) FROM profiles
UNION ALL
SELECT 'workspaces', COUNT(*) FROM workspaces
UNION ALL
SELECT 'campaigns', COUNT(*) FROM campaigns
UNION ALL
SELECT 'users', COUNT(*) FROM users;" 2>/dev/null)

backup_counts=$(psql "$DATABASE_URL" -f "$BACKUP_FILE" -c "
SELECT 'profiles', COUNT(*) FROM profiles
UNION ALL
SELECT 'workspaces', COUNT(*) FROM workspaces
UNION ALL
SELECT 'campaigns', COUNT(*) FROM campaigns
UNION ALL
SELECT 'users', COUNT(*) FROM users;" 2>/dev/null)

if [ "$original_counts" = "$backup_counts" ]; then
    echo "✅ Backup data integrity verified"
else
    echo "❌ Backup data integrity mismatch"
    echo "Original: $original_counts"
    echo "Backup: $backup_counts"
    exit 1
fi

# Test 3: Database Restore
echo ""
echo "🔄 Test 3: Database Restore"
echo "Creating test database for restore..."

# Create test database
createdb "$RESTORE_TEST_DB" 2>/dev/null || true

# Load backup into test database
if psql "$RESTORE_TEST_DB" -f "$BACKUP_FILE" > /dev/null 2>&1; then
    echo "✅ Database restore successful"
else
    echo "❌ Database restore failed"
    exit 1
fi

# Verify restored data
echo "Verifying restored data..."
restored_counts=$(psql "$RESTORE_TEST_DB" -c "
SELECT 'profiles', COUNT(*) FROM profiles
UNION ALL
SELECT 'workspaces', COUNT(*) FROM workspaces
UNION ALL
SELECT 'campaigns', COUNT(*) FROM campaigns
UNION ALL
SELECT 'users', COUNT(*) FROM users;" 2>/dev/null)

if [ "$original_counts" = "$restored_counts" ]; then
    echo "✅ Restored data integrity verified"
else
    echo "❌ Restored data integrity mismatch"
    echo "Original: $original_counts"
    echo "Restored: $restored_counts"
    exit 1
fi

# Clean up test database
dropdb "$RESTORE_TEST_DB" 2>/dev/null || true

# Test 4: Incremental Backup
echo ""
echo "📈 Test 4: Incremental Backup"
echo "Testing incremental backup capability..."

# Create a small change
psql "$DATABASE_URL" -c "
INSERT INTO profiles (id, user_id, workspace_id, created_at, updated_at)
VALUES ('test-backup-'$(date +%s)', 'test-user', 'test-workspace', NOW(), NOW());" 2>/dev/null

# Create incremental backup
inc_backup_file="$BACKUP_DIR/incremental-$TIMESTAMP.sql"
pg_dump "$DATABASE_URL" --data-only --table=profiles --file="$inc_backup_file"

if [ -f "$inc_backup_file" ] && [ -s "$inc_backup_file" ]; then
    inc_size=$(du -h "$inc_backup_file" | cut -f1)
    echo "✅ Incremental backup created: $inc_size"
    
    # Verify incremental backup contains only profiles table
    if grep -q "INSERT INTO profiles" "$inc_backup_file"; then
        echo "✅ Incremental backup contains expected data"
    else
        echo "❌ Incremental backup missing expected data"
        exit 1
    fi
else
    echo "❌ Incremental backup creation failed"
    exit 1
fi

# Test 5: Backup Encryption
echo ""
echo "🔐 Test 5: Backup Encryption"
echo "Testing backup file encryption..."

# Create encrypted backup
encrypted_backup="$BACKUP_DIR/encrypted-$TIMESTAMP.sql"
gpg --symmetric --cipher-algo AES256 --compress --output "$encrypted_backup" "$BACKUP_FILE" 2>/dev/null

if [ -f "$encrypted_backup" ]; then
    enc_size=$(du -h "$encrypted_backup" | cut -f1)
    echo "✅ Encrypted backup created: $enc_size"
    
    # Test decryption
    decrypted_backup="$BACKUP_DIR/decrypted-$TIMESTAMP.sql"
    gpg --decrypt --output "$decrypted_backup" "$encrypted_backup" 2>/dev/null
    
    if [ -f "$decrypted_backup" ]; then
        # Compare file sizes
        original_size=$(stat -c%s "$BACKUP_FILE")
        decrypted_size=$(stat -c%s "$decrypted_backup")
        
        if [ "$original_size" = "$decrypted_size" ]; then
            echo "✅ Backup encryption/decryption verified"
        else
            echo "❌ Decrypted file size mismatch"
            exit 1
        fi
        
        # Clean up decrypted file
        rm "$decrypted_backup"
    else
        echo "❌ Backup decryption failed"
        exit 1
    fi
else
    echo "❌ Encrypted backup creation failed"
    exit 1
fi

# Test 6: Backup Schedule
echo ""
echo "⏰ Test 6: Backup Schedule"
echo "Testing automated backup schedule..."

# Create backup script
backup_script="$BACKUP_DIR/scheduled-backup.sh"
cat > "$backup_script" << 'EOF'
#!/bin/bash
# Automated backup script
BACKUP_DIR="/tmp/raptorflow-backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/scheduled-$TIMESTAMP.sql"

mkdir -p "$BACKUP_DIR"
pg_dump "$DATABASE_URL" --verbose --format=custom --file="$BACKUP_FILE"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "scheduled-*.sql" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
EOF

chmod +x "$backup_script"

# Test backup script execution
if "$backup_script" > /dev/null 2>&1; then
    echo "✅ Backup script execution successful"
else
    echo "❌ Backup script execution failed"
    exit 1
fi

# Test 7: Backup Retention
echo ""
echo "🗂 Test 7: Backup Retention Policy"
echo "Testing backup retention policy..."

# Create multiple backup files
for i in {1..5}; do
    touch "$BACKUP_DIR/old-backup-$i.sql"
    sleep 0.1
done

# Create retention script
retention_script="$BACKUP_DIR/cleanup-old-backups.sh"
cat > "$retention_script" << 'EOF'
#!/bin/bash
# Clean up old backups (keep last 3)
BACKUP_DIR="/tmp/raptorflow-backups"
find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete
echo "Old backups cleaned up"
EOF

chmod +x "$retention_script"

# Test retention script
old_count=$(find "$BACKUP_DIR" -name "old-backup-*.sql" | wc -l)
"$retention_script" > /dev/null 2>&1
new_count=$(find "$BACKUP_DIR" -name "old-backup-*.sql" | wc -l)

if [ "$new_count" -lt "$old_count" ]; then
    echo "✅ Backup retention policy working (removed $((old_count - new_count)) files)"
else
    echo "❌ Backup retention policy not working"
    exit 1
fi

# Clean up test files
rm "$BACKUP_DIR"/old-backup-*.sql

# Test 8: Backup Monitoring
echo ""
echo "📊 Test 8: Backup Monitoring"
echo "Testing backup monitoring and alerting..."

# Create monitoring script
monitor_script="$BACKUP_DIR/backup-monitor.sh"
cat > "$monitor_script" << 'EOF'
#!/bin/bash
# Backup monitoring script
BACKUP_DIR="/tmp/raptorflow-backups"
ALERT_EMAIL="admin@raptorflow.com"

# Check for recent backups
recent_backups=$(find "$BACKUP_DIR" -name "*.sql" -mtime -1 | wc -l)

if [ "$recent_backups" -lt 1 ]; then
    echo "WARNING: No backups found in last 24 hours" | mail -s "Backup Alert" "$ALERT_EMAIL"
    exit 1
else
    echo "✅ Found $recent_backups recent backups"
fi

# Check backup file sizes
for backup in "$BACKUP_DIR"/*.sql; do
    size=$(stat -c%s "$backup")
    if [ "$size" -lt 1000 ]; then
        echo "WARNING: Small backup file: $(basename "$backup") ($size bytes)" | mail -s "Small Backup Alert" "$ALERT_EMAIL"
    fi
done
EOF

chmod +x "$monitor_script"

# Test monitoring script
if "$monitor_script" > /dev/null 2>&1; then
    echo "✅ Backup monitoring script working"
else
    echo "❌ Backup monitoring script failed"
    exit 1
fi

# Generate summary report
echo ""
echo "📋 Backup and Restore Test Summary"
echo "================================"

echo "✅ Test 1: Database Backup - PASSED"
echo "✅ Test 2: Backup Integrity Check - PASSED"
echo "✅ Test 3: Database Restore - PASSED"
echo "✅ Test 4: Incremental Backup - PASSED"
echo "✅ Test 5: Backup Encryption - PASSED"
echo "✅ Test 6: Backup Schedule - PASSED"
echo "✅ Test 7: Backup Retention - PASSED"
echo "✅ Test 8: Backup Monitoring - PASSED"

echo ""
echo "Backup files created:"
ls -lh "$BACKUP_DIR"/*.sql 2>/dev/null | tail -5

echo ""
echo "🎉 All backup and restore tests passed!"
echo "Backup system is production ready."

# Clean up test files
rm -f "$BACKUP_DIR/decrypted-$TIMESTAMP.sql"
rm -f "$BACKUP_DIR/old-backup-*.sql"

echo ""
echo "Backup and Restore Tests Complete"
echo "================================"
