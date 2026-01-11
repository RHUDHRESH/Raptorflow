-- RLS policies for workspaces table
-- Migration: 20240101_workspaces_rls.sql

-- Users can view own workspaces
CREATE POLICY "Users can view own workspaces" ON public.workspaces
    FOR SELECT USING (user_id = auth.uid());

-- Users can create workspaces
CREATE POLICY "Users can create workspaces" ON public.workspaces
    FOR INSERT WITH CHECK (user_id = auth.uid());

-- Users can update own workspaces
CREATE POLICY "Users can update own workspaces" ON public.workspaces
    FOR UPDATE USING (user_id = auth.uid());

-- Users can delete own workspaces
CREATE POLICY "Users can delete own workspaces" ON public.workspaces
    FOR DELETE USING (user_id = auth.uid());
