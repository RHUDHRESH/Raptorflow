-- RaptorFlow Complete Database Schema (v2.0) - Part 9: Storage Setup
-- Supabase Storage buckets and policies

-- =====================================
-- 27. STORAGE BUCKETS
-- =====================================

-- Brand Assets Storage Bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'brand-assets',
    'brand-assets',
    false,
    10485760, -- 10MB
    ARRAY[
        'image/jpeg',
        'image/png',
        'image/svg+xml',
        'image/gif',
        'image/webp',
        'application/pdf',
        'text/plain'
    ]
) ON CONFLICT (id) DO NOTHING;

-- Muse Assets Storage Bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'muse-assets',
    'muse-assets',
    false,
    10485760, -- 10MB
    ARRAY[
        'image/jpeg',
        'image/png',
        'image/svg+xml',
        'image/gif',
        'image/webp',
        'video/mp4',
        'video/webm',
        'audio/mpeg',
        'audio/wav',
        'application/pdf',
        'text/plain',
        'text/markdown'
    ]
) ON CONFLICT (id) DO NOTHING;

-- Campaign Assets Storage Bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'campaign-assets',
    'campaign-assets',
    false,
    10485760, -- 10MB
    ARRAY[
        'image/jpeg',
        'image/png',
        'image/svg+xml',
        'image/gif',
        'image/webp',
        'video/mp4',
        'video/webm',
        'application/pdf',
        'text/plain',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]
) ON CONFLICT (id) DO NOTHING;

-- User Uploads Storage Bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'user-uploads',
    'user-uploads',
    false,
    52428800, -- 50MB
    ARRAY[
        'image/jpeg',
        'image/png',
        'image/svg+xml',
        'image/gif',
        'image/webp',
        'video/mp4',
        'video/webm',
        'audio/mpeg',
        'audio/wav',
        'application/pdf',
        'text/plain',
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    ]
) ON CONFLICT (id) DO NOTHING;

-- =====================================
-- 28. STORAGE RLS POLICIES
-- =====================================

-- Enable RLS on storage objects
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Brand Assets Storage Policies
CREATE POLICY "Brand Assets: Workspace members can view their workspace assets" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'brand-assets' AND
        (storage.foldername(name))[1] IN (
            SELECT workspace_id::text FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Brand Assets: Workspace members can upload to their workspace" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'brand-assets' AND
        (storage.foldername(name))[1] IN (
            SELECT workspace_id::text FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Brand Assets: Workspace members can update their workspace assets" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'brand-assets' AND
        (storage.foldername(name))[1] IN (
            SELECT workspace_id::text FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Brand Assets: Owners and admins can delete their workspace assets" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'brand-assets' AND
        (storage.foldername(name))[1] IN (
            SELECT workspace_id::text FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- Muse Assets Storage Policies
CREATE POLICY "Muse Assets: Workspace members can view their workspace assets" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'muse-assets' AND
        (storage.foldername(name))[1] IN (
            SELECT workspace_id::text FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Muse Assets: Workspace members can upload to their workspace" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'muse-assets' AND
        (storage.foldername(name))[1] IN (
            SELECT workspace_id::text FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Muse Assets: Workspace members can update their workspace assets" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'muse-assets' AND
        (storage.foldername(name))[1] IN (
            SELECT workspace_id::text FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Muse Assets: Owners and admins can delete their workspace assets" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'muse-assets' AND
        (storage.foldername(name))[1] IN (
            SELECT workspace_id::text FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- Campaign Assets Storage Policies
CREATE POLICY "Campaign Assets: Workspace members can view their workspace assets" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'campaign-assets' AND
        (storage.foldername(name))[1] IN (
            SELECT workspace_id::text FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Campaign Assets: Workspace members can upload to their workspace" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'campaign-assets' AND
        (storage.foldername(name))[1] IN (
            SELECT workspace_id::text FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Campaign Assets: Workspace members can update their workspace assets" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'campaign-assets' AND
        (storage.foldername(name))[1] IN (
            SELECT workspace_id::text FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Campaign Assets: Owners and admins can delete their workspace assets" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'campaign-assets' AND
        (storage.foldername(name))[1] IN (
            SELECT workspace_id::text FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- User Uploads Storage Policies
CREATE POLICY "User Uploads: Users can view their own uploads" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'user-uploads' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );

CREATE POLICY "User Uploads: Users can upload their own files" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'user-uploads' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );

CREATE POLICY "User Uploads: Users can update their own files" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'user-uploads' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );

CREATE POLICY "User Uploads: Users can delete their own files" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'user-uploads' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );

-- =====================================
-- 29. STORAGE HELPER FUNCTIONS
-- =====================================

-- Function to generate storage path for brand assets
CREATE OR REPLACE FUNCTION brand_asset_path(workspace_uuid UUID, file_name TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN workspace_uuid::text || '/' || file_name;
END;
$$ language 'plpgsql';

-- Function to generate storage path for muse assets
CREATE OR REPLACE FUNCTION muse_asset_path(workspace_uuid UUID, asset_uuid UUID, file_name TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN workspace_uuid::text || '/' || asset_uuid::text || '/' || file_name;
END;
$$ language 'plpgsql';

-- Function to generate storage path for campaign assets
CREATE OR REPLACE FUNCTION campaign_asset_path(workspace_uuid UUID, campaign_uuid UUID, file_name TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN workspace_uuid::text || '/' || campaign_uuid::text || '/' || file_name;
END;
$$ language 'plpgsql';

-- Function to generate storage path for user uploads
CREATE OR REPLACE FUNCTION user_upload_path(user_uuid UUID, file_name TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN user_uuid::text || '/' || file_name;
END;
$$ language 'plpgsql';

-- Function to check if user can access storage object
CREATE OR REPLACE FUNCTION can_access_storage_object(object_name TEXT, bucket_name TEXT, operation TEXT DEFAULT 'read')
RETURNS BOOLEAN AS $$
DECLARE
    workspace_id UUID;
    user_role TEXT;
    is_member BOOLEAN;
BEGIN
    -- Extract workspace ID from path
    IF bucket_name IN ('brand-assets', 'muse-assets', 'campaign-assets') THEN
        workspace_id := (storage.foldername(object_name))[1]::UUID;

        -- Check if user is workspace member
        SELECT EXISTS(
            SELECT 1 FROM workspace_members
            WHERE workspace_id = workspace_id
            AND user_id = auth.uid()
        ) INTO is_member;

        IF NOT is_member THEN
            RETURN FALSE;
        END IF;

        -- For delete operations, check if user is owner or admin
        IF operation = 'delete' THEN
            SELECT role INTO user_role
            FROM workspace_members
            WHERE workspace_id = workspace_id
            AND user_id = auth.uid()
            LIMIT 1;

            RETURN user_role IN ('owner', 'admin');
        END IF;

        RETURN TRUE;
    ELSIF bucket_name = 'user-uploads' THEN
        -- For user uploads, check if user owns the folder
        RETURN (storage.foldername(object_name))[1] = auth.uid()::text;
    END IF;

    RETURN FALSE;
END;
$$ language 'plpgsql';

-- =====================================
-- 30. STORAGE CLEANUP FUNCTIONS
-- =====================================

-- Function to clean up orphaned storage objects
CREATE OR REPLACE FUNCTION cleanup_orphaned_storage_objects()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete brand assets for deleted workspaces
    DELETE FROM storage.objects
    WHERE bucket_id = 'brand-assets'
    AND (storage.foldername(name))[1] NOT IN (
        SELECT id::text FROM workspaces
    );

    -- Delete muse assets for deleted workspaces
    DELETE FROM storage.objects
    WHERE bucket_id = 'muse-assets'
    AND (storage.foldername(name))[1] NOT IN (
        SELECT id::text FROM workspaces
    );

    -- Delete campaign assets for deleted workspaces
    DELETE FROM storage.objects
    WHERE bucket_id = 'campaign-assets'
    AND (storage.foldername(name))[1] NOT IN (
        SELECT id::text FROM workspaces
    );

    -- Delete user uploads for deleted users
    DELETE FROM storage.objects
    WHERE bucket_id = 'user-uploads'
    AND (storage.foldername(name))[1] NOT IN (
        SELECT id::text FROM auth.users
    );

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ language 'plpgsql';

-- Function to get storage usage statistics
CREATE OR REPLACE FUNCTION get_storage_usage_stats(workspace_uuid UUID DEFAULT NULL)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    brand_size BIGINT;
    muse_size BIGINT;
    campaign_size BIGINT;
    user_size BIGINT;
BEGIN
    IF workspace_uuid IS NOT NULL THEN
        -- Get usage for specific workspace
        SELECT COALESCE(SUM(size), 0) INTO brand_size
        FROM storage.objects
        WHERE bucket_id = 'brand-assets'
        AND (storage.foldername(name))[1] = workspace_uuid::text;

        SELECT COALESCE(SUM(size), 0) INTO muse_size
        FROM storage.objects
        WHERE bucket_id = 'muse-assets'
        AND (storage.foldername(name))[1] = workspace_uuid::text;

        SELECT COALESCE(SUM(size), 0) INTO campaign_size
        FROM storage.objects
        WHERE bucket_id = 'campaign-assets'
        AND (storage.foldername(name))[1] = workspace_uuid::text;

        result := jsonb_build_object(
            'workspace_id', workspace_uuid,
            'brand_assets_bytes', brand_size,
            'muse_assets_bytes', muse_size,
            'campaign_assets_bytes', campaign_size,
            'total_bytes', brand_size + muse_size + campaign_size,
            'calculated_at', now()
        );
    ELSE
        -- Get global usage statistics
        SELECT COALESCE(SUM(size), 0) INTO brand_size
        FROM storage.objects
        WHERE bucket_id = 'brand-assets';

        SELECT COALESCE(SUM(size), 0) INTO muse_size
        FROM storage.objects
        WHERE bucket_id = 'muse-assets';

        SELECT COALESCE(SUM(size), 0) INTO campaign_size
        FROM storage.objects
        WHERE bucket_id = 'campaign-assets';

        SELECT COALESCE(SUM(size), 0) INTO user_size
        FROM storage.objects
        WHERE bucket_id = 'user-uploads';

        result := jsonb_build_object(
            'brand_assets_bytes', brand_size,
            'muse_assets_bytes', muse_size,
            'campaign_assets_bytes', campaign_size,
            'user_uploads_bytes', user_size,
            'total_bytes', brand_size + muse_size + campaign_size + user_size,
            'calculated_at', now()
        );
    END IF;

    RETURN result;
END;
$$ language 'plpgsql';
