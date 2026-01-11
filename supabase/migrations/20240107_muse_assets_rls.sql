-- RLS policies for muse_assets table
-- Migration: 20240107_muse_assets_rls.sql
-- Description: Row Level Security policies for muse_assets table

-- Users can view muse assets in their workspace
CREATE POLICY "Users can view muse assets" ON public.muse_assets
    FOR SELECT USING (
        user_owns_workspace(workspace_id)
    );

-- Users can create muse assets in their workspace
CREATE POLICY "Users can create muse assets" ON public.muse_assets
    FOR INSERT WITH CHECK (
        user_owns_workspace(workspace_id)
    );

-- Users can update muse assets in their workspace
CREATE POLICY "Users can update muse assets" ON public.muse_assets
    FOR UPDATE USING (
        user_owns_workspace(workspace_id)
    );

-- Users can delete muse assets in their workspace
CREATE POLICY "Users can delete muse assets" ON public.muse_assets
    FOR DELETE USING (
        user_owns_workspace(workspace_id)
    );
