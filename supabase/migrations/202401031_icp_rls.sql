-- RLS policies for ICP profiles table
-- Migration: 20240103_icp_rls.sql

-- Apply RLS policies to icp_profiles
CREATE POLICY "Users can view own ICP profiles" ON public.icp_profiles
    FOR SELECT USING (user_owns_workspace(workspace_id));

CREATE POLICY "Users can create own ICP profiles" ON public.icp_profiles
    FOR INSERT WITH CHECK (user_owns_workspace(workspace_id));

CREATE POLICY "Users can update own ICP profiles" ON public.icp_profiles
    FOR UPDATE USING (user_owns_workspace(workspace_id));

CREATE POLICY "Users can delete own ICP profiles" ON public.icp_profiles
    FOR DELETE USING (user_owns_workspace(workspace_id));
