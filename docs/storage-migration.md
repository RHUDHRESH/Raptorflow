# Storage Migration: GCS to Supabase

## Overview

Raptorflow has successfully migrated from Google Cloud Storage (GCS) to Supabase Storage for all file storage operations. This document outlines the migration process and provides guidance for developers.

## Migration Timeline

**Completed:** January 21, 2025

## What Changed

### Backend Changes

1. **New Supabase Storage Client**
   - `backend/services/supabase_storage_client.py` - Python client for Supabase Storage REST API
   - `backend/infrastructure/supabase_storage.py` - High-level storage service

2. **Updated Services**
   - `backend/services/storage.py` - EnhancedStorageService now uses Supabase
   - `backend/services/document_service.py` - DocumentService uses SupabaseStorageManager
   - `backend/services/titan/orchestrator.py` - Titan intelligence storage uses Supabase

3. **Configuration Updates**
   - `backend/services/environment_manager.py` - Removed GCS env vars, added Supabase config
   - `backend/core/environment_validation.py` - Updated validation for Supabase variables

### Frontend Changes

1. **Unified Storage Abstraction**
   - `src/lib/unified-storage.ts` - Now configured to use Supabase by default
   - `src/lib/storage-paths.ts` - Standardized path generation for Supabase

2. **API Updates**
   - `src/app/api/init-storage/route.ts` - Creates Supabase buckets with proper policies
   - `src/app/api/onboarding/provision-storage/route.ts` - Uses Supabase for workspace storage

### Infrastructure Changes

1. **Bucket Structure**
   - `workspace-uploads` - User file uploads
   - `workspace-exports` - Generated exports
   - `workspace-backups` - System backups
   - `workspace-assets` - Static assets
   - `workspace-logs` - Log files
   - `intelligence-vault` - AI intelligence data
   - `user-avatars` - User profile images
   - `user-documents` - User documents
   - `user-data` - User data exports

2. **Path Convention**
   - Format: `workspace/<slug>/<category>/<YYYY-MM-DD>/<uuid>-<filename>`
   - Example: `workspace/my-workspace/uploads/2025-01-21/abc123-document.pdf`

## Environment Variables

### Removed (GCS)
```bash
GOOGLE_PROJECT_ID
GOOGLE_APPLICATION_CREDENTIALS
GCS_MAIN_BUCKET
GCS_EVIDENCE_BUCKET
GCS_INGEST_BUCKET
GCS_GOLD_BUCKET
```

### Added (Supabase)
```bash
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
```

## Code Migration Guide

### Backend Python

**Before (GCS):**
```python
from google.cloud.storage import Client
storage_client = Client()
bucket = storage_client.bucket('my-bucket')
blob = bucket.blob('path/to/file')
blob.upload_from_string(content)
```

**After (Supabase):**
```python
from backend.services.supabase_storage_client import get_supabase_storage_client
client = get_supabase_storage_client()
client.upload_file('my-bucket', 'path/to/file', content)
```

### Frontend TypeScript

**Before (GCS):**
```typescript
import { gcpStorage } from './gcp-storage'
const result = await gcpStorage.uploadFile({ file, userId })
```

**After (Supabase):**
```typescript
import { unifiedStorage } from './unified-storage'
const result = await unifiedStorage.uploadFile(file, { userId })
```

## Bucket Access Policies

### Public Buckets
- `workspace-assets` - Static assets (images, CSS, JS)
- `user-avatars` - User profile images

### Private Buckets
- `workspace-uploads` - User uploads (signed URLs required)
- `workspace-exports` - Generated exports
- `workspace-backups` - System backups
- `workspace-logs` - Log files
- `intelligence-vault` - AI intelligence data
- `user-documents` - User documents
- `user-data` - User data exports

## Migration Checklist

- [x] Backend services updated to use Supabase
- [x] Frontend unified storage configured for Supabase
- [x] Environment variables updated
- [x] Bucket creation API implemented
- [x] Path utilities standardized
- [x] GCS script deprecated
- [x] Documentation updated

## Testing

### Backend Tests
```bash
# Test Supabase storage client
python -m backend.services.supabase_storage_client

# Test enhanced storage service
python -m backend.services.storage
```

### Frontend Tests
```bash
# Test unified storage
npm run test:storage
```

## Rollback Plan

If rollback is needed:
1. Restore GCS environment variables
2. Revert backend services to GCS imports
3. Update unified-storage.ts to use 'gcs' provider
4. Restore GCS setup script

## Support

For migration issues:
1. Check Supabase dashboard for bucket status
2. Verify environment variables are set correctly
3. Review logs for storage operation errors
4. Consult the development team for assistance

## Performance Considerations

- Supabase Storage provides better integration with the existing database
- Signed URLs are generated on-demand for private files
- Automatic CDN integration through Supabase
- Improved security with Row Level Security policies

## Cost Impact

- Supabase Storage pricing is based on usage
- No minimum storage commitments
- Better cost predictability compared to GCS
- Included in Supabase Pro plan limits
