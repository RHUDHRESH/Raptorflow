-- Row Level Security Policies for workspace_settings
-- Migration: 20251228000002_workspace_settings_rls.sql

-- Enable RLS on workspace_settings table (if not already enabled)
ALTER TABLE workspace_settings ENABLE ROW LEVEL SECURITY;

-- Workspace Settings RLS Policies
-- Only workspace members can read settings
CREATE POLICY "Workspace Settings: Workspace members can read" ON workspace_settings
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = workspace_settings.workspace_id
        )
    );

-- Only owners and admins can update settings
CREATE POLICY "Workspace Settings: Owners and admins can update" ON workspace_settings
    FOR UPDATE USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = workspace_settings.workspace_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- Only owners and admins can insert settings (for initial creation)
CREATE POLICY "Workspace Settings: Owners and admins can insert" ON workspace_settings
    FOR INSERT WITH CHECK (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = workspace_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- Only owners can delete settings
CREATE POLICY "Workspace Settings: Owners can delete" ON workspace_settings
    FOR DELETE USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = workspace_settings.workspace_id
            AND workspace_members.role = 'owner'
        )
    );
