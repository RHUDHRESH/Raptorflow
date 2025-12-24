-- Migration: Setup Supabase Storage for Brand Assets
-- Isolated by workspace_id

-- 1. Create the 'brand-assets' bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('brand-assets', 'brand-assets', false)
ON CONFLICT (id) DO NOTHING;

-- 2. RLS Policies for the bucket
-- Allow members to upload/read/delete within their workspace folder
-- Path pattern: {workspace_id}/...

CREATE POLICY "Workspace Isolation for Uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'brand-assets' AND
    (storage.foldername(name))[1] = (
        SELECT workspace_id::text
        FROM workspace_members
        WHERE user_id = auth.uid()
        AND workspace_id::text = (storage.foldername(name))[1]
        LIMIT 1
    )
);

CREATE POLICY "Workspace Isolation for Selection"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'brand-assets' AND
    (storage.foldername(name))[1] = (
        SELECT workspace_id::text
        FROM workspace_members
        WHERE user_id = auth.uid()
        AND workspace_id::text = (storage.foldername(name))[1]
        LIMIT 1
    )
);

CREATE POLICY "Workspace Isolation for Deletion"
ON storage.objects FOR DELETE
TO authenticated
USING (
    bucket_id = 'brand-assets' AND
    (storage.foldername(name))[1] = (
        SELECT workspace_id::text
        FROM workspace_members
        WHERE user_id = auth.uid()
        AND workspace_id::text = (storage.foldername(name))[1]
        LIMIT 1
    )
);
