-- Migration: Remove legacy user_id column from workspaces table
-- Description: Drop the deprecated user_id column and enforce owner_id + workspace_members schema

-- First check if user_id column exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'workspaces'
        AND column_name = 'user_id'
    ) THEN
        -- Create a backup of any data that might be in user_id but not in owner_id
        UPDATE workspaces
        SET owner_id = user_id
        WHERE owner_id IS NULL AND user_id IS NOT NULL;

        -- Drop the deprecated column
        ALTER TABLE workspaces DROP COLUMN user_id;

        RAISE NOTICE 'Dropped user_id column from workspaces table';
    ELSE
        RAISE NOTICE 'user_id column does not exist in workspaces table';
    END IF;
END $$;

-- Add comments to clarify the schema
COMMENT ON COLUMN workspaces.owner_id IS 'Primary owner of the workspace (replaces deprecated user_id)';
COMMENT ON TABLE workspace_members IS 'Workspace membership relationships for multi-user access';

-- Ensure proper indexes exist
CREATE INDEX IF NOT EXISTS idx_workspaces_owner_id ON workspaces(owner_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace_id ON workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_user_id ON workspace_members(user_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_active ON workspace_members(workspace_id, user_id, is_active);

-- Add constraint to ensure owner_id is always set
ALTER TABLE workspaces ADD CONSTRAINT IF NOT EXISTS workspaces_owner_id_not_null
    CHECK (owner_id IS NOT NULL);

-- Log the migration completion
DO $$
BEGIN
    INSERT INTO supabase_migrations.schema_migrations (version, name, executed_at)
    VALUES (
        '20240128000001',
        'remove_legacy_user_id_column',
        NOW()
    ) ON CONFLICT (version) DO NOTHING;

    RAISE NOTICE 'Migration remove_legacy_user_id_column completed successfully';
END $$;
