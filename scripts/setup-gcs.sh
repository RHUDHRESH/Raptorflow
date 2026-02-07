#!/bin/bash

# ============================================================================
# DEPRECATED: GCS Storage Setup Script
# ============================================================================
#
# This script has been deprecated as Raptorflow has migrated from Google Cloud Storage
# to Supabase Storage for all file storage operations.
#
# Please use the Supabase Storage setup instead:
# - See: src/app/api/init-storage/route.ts for automatic bucket creation
# - See: docs/storage-migration.md for migration guide
# - See: backend/services/supabase_storage_client.py for client usage
#
# Migration completed: 2025-01-21
# ============================================================================

echo "⚠️  DEPRECATION WARNING"
echo "===================="
echo "This script has been deprecated."
echo "Raptorflow now uses Supabase Storage instead of Google Cloud Storage."
echo ""
echo "Please refer to the Supabase Storage documentation:"
echo "- src/app/api/init-storage/route.ts - Automatic bucket creation"
echo "- docs/storage-migration.md - Migration guide"
echo "- backend/services/supabase_storage_client.py - Client usage"
echo ""
echo "To set up Supabase Storage:"
echo "1. Ensure SUPABASE_URL and SUPABASE_SERVICE_KEY are configured"
echo "2. Run the init-storage API endpoint to create buckets"
echo "3. Update your code to use the unified-storage.ts client"
echo ""
echo "For migration assistance, see the storage migration documentation."
