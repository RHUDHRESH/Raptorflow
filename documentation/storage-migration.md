# Storage Migration Status

Raptorflow uses Supabase Storage as the active storage provider.

## Current State

- Upload sessions are created through backend assets APIs.
- Signed upload URLs are issued by Supabase storage.
- Metadata is written to the `assets` table.

## Required Environment Variables

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_STORAGE_BUCKET` (optional, defaults to `uploads`)

## Verification Steps

1. Create workspace.
2. Create `/api/assets/sessions`.
3. Upload file to signed URL.
4. Confirm upload via `/api/assets/{asset_id}/confirm`.
5. List assets via `/api/assets`.
