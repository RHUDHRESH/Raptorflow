-- RLS policies for campaigns table
-- Migration: 20240106_campaigns_rls.sql
-- Description: Row Level Security policies for campaigns table

-- Users can view campaigns in their workspace
CREATE POLICY "Users can view campaigns" ON public.campaigns
    FOR SELECT USING (
        user_owns_workspace(workspace_id)
    );

-- Users can create campaigns in their workspace
CREATE POLICY "Users can create campaigns" ON public.campaigns
    FOR INSERT WITH CHECK (
        user_owns_workspace(workspace_id)
    );

-- Users can update campaigns in their workspace
CREATE POLICY "Users can update campaigns" ON public.campaigns
    FOR UPDATE USING (
        user_owns_workspace(workspace_id)
    );

-- Users can delete campaigns in their workspace
CREATE POLICY "Users can delete campaigns" ON public.campaigns
    FOR DELETE USING (
        user_owns_workspace(workspace_id)
    );
