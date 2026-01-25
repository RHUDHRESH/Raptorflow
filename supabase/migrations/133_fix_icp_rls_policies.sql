-- =================================================================
-- SECURITY FIXES: ICP Tables Missing RLS Policies
-- Migration: 133_fix_icp_rls_policies.sql
-- Priority: MEDIUM - Adds missing RLS policies for ICP tables
-- =================================================================

-- Create RLS policies for icp_disqualifiers table
CREATE POLICY "icp_disqualifiers_select_workspace" ON public.icp_disqualifiers
    FOR SELECT USING (
        auth.role() IN ('authenticated', 'service_role') AND
        workspace_id = (
            SELECT workspace_id FROM public.profiles
            WHERE id = (select auth.uid())
        )
    );

CREATE POLICY "icp_disqualifiers_insert_workspace" ON public.icp_disqualifiers
    FOR INSERT WITH CHECK (
        auth.role() = 'authenticated' AND
        workspace_id = (
            SELECT workspace_id FROM public.profiles
            WHERE id = (select auth.uid())
        )
    );

CREATE POLICY "icp_disqualifiers_update_workspace" ON public.icp_disqualifiers
    FOR UPDATE USING (
        auth.role() = 'authenticated' AND
        workspace_id = (
            SELECT workspace_id FROM public.profiles
            WHERE id = (select auth.uid())
        )
    );

CREATE POLICY "icp_disqualifiers_delete_workspace" ON public.icp_disqualifiers
    FOR DELETE USING (
        auth.role() = 'authenticated' AND
        workspace_id = (
            SELECT workspace_id FROM public.profiles
            WHERE id = (select auth.uid())
        )
    );

-- Create RLS policies for icp_firmographics table
CREATE POLICY "icp_firmographics_select_workspace" ON public.icp_firmographics
    FOR SELECT USING (
        auth.role() IN ('authenticated', 'service_role') AND
        profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id = (
                SELECT workspace_id FROM public.profiles
                WHERE id = (select auth.uid())
            )
        )
    );

CREATE POLICY "icp_firmographics_insert_workspace" ON public.icp_firmographics
    FOR INSERT WITH CHECK (
        auth.role() = 'authenticated' AND
        profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id = (
                SELECT workspace_id FROM public.profiles
                WHERE id = (select auth.uid())
            )
        )
    );

CREATE POLICY "icp_firmographics_update_workspace" ON public.icp_firmographics
    FOR UPDATE USING (
        auth.role() = 'authenticated' AND
        profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id = (
                SELECT workspace_id FROM public.profiles
                WHERE id = (select auth.uid())
            )
        )
    );

CREATE POLICY "icp_firmographics_delete_workspace" ON public.icp_firmographics
    FOR DELETE USING (
        auth.role() = 'authenticated' AND
        profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id = (
                SELECT workspace_id FROM public.profiles
                WHERE id = (select auth.uid())
            )
        )
    );

-- Create RLS policies for icp_pain_map table
CREATE POLICY "icp_pain_map_select_workspace" ON public.icp_pain_map
    FOR SELECT USING (
        auth.role() IN ('authenticated', 'service_role') AND
        profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id = (
                SELECT workspace_id FROM public.profiles
                WHERE id = (select auth.uid())
            )
        )
    );

CREATE POLICY "icp_pain_map_insert_workspace" ON public.icp_pain_map
    FOR INSERT WITH CHECK (
        auth.role() = 'authenticated' AND
        profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id = (
                SELECT workspace_id FROM public.profiles
                WHERE id = (select auth.uid())
            )
        )
    );

CREATE POLICY "icp_pain_map_update_workspace" ON public.icp_pain_map
    FOR UPDATE USING (
        auth.role() = 'authenticated' AND
        profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id = (
                SELECT workspace_id FROM public.profiles
                WHERE id = (select auth.uid())
            )
        )
    );

CREATE POLICY "icp_pain_map_delete_workspace" ON public.icp_pain_map
    FOR DELETE USING (
        auth.role() = 'authenticated' AND
        profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id = (
                SELECT workspace_id FROM public.profiles
                WHERE id = (select auth.uid())
            )
        )
    );

-- Create RLS policies for icp_psycholinguistics table
CREATE POLICY "icp_psycholinguistics_select_workspace" ON public.icp_psycholinguistics
    FOR SELECT USING (
        auth.role() IN ('authenticated', 'service_role') AND
        profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id = (
                SELECT workspace_id FROM public.profiles
                WHERE id = (select auth.uid())
            )
        )
    );

CREATE POLICY "icp_psycholinguistics_insert_workspace" ON public.icp_psycholinguistics
    FOR INSERT WITH CHECK (
        auth.role() = 'authenticated' AND
        profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id = (
                SELECT workspace_id FROM public.profiles
                WHERE id = (select auth.uid())
            )
        )
    );

CREATE POLICY "icp_psycholinguistics_update_workspace" ON public.icp_psycholinguistics
    FOR UPDATE USING (
        auth.role() = 'authenticated' AND
        profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id = (
                SELECT workspace_id FROM public.profiles
                WHERE id = (select auth.uid())
            )
        )
    );

CREATE POLICY "icp_psycholinguistics_delete_workspace" ON public.icp_psycholinguistics
    FOR DELETE USING (
        auth.role() = 'authenticated' AND
        profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id = (
                SELECT workspace_id FROM public.profiles
                WHERE id = (select auth.uid())
            )
        )
    );

-- Grant necessary permissions
GRANT ALL ON public.icp_disqualifiers TO authenticated;
GRANT ALL ON public.icp_disqualifiers TO service_role;
GRANT ALL ON public.icp_firmographics TO authenticated;
GRANT ALL ON public.icp_firmographics TO service_role;
GRANT ALL ON public.icp_pain_map TO authenticated;
GRANT ALL ON public.icp_pain_map TO service_role;
GRANT ALL ON public.icp_psycholinguistics TO authenticated;
GRANT ALL ON public.icp_psycholinguistics TO service_role;
