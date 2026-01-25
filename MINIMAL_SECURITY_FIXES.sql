-- =================================================================
-- MINIMAL SECURITY FIXES - NO CONCURRENTLY, NO COMPLEX SYNTAX
-- Run each section separately if needed
-- =================================================================

-- STEP 1: Enable RLS on critical tables
ALTER TABLE public.plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.admin_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_events ENABLE ROW LEVEL SECURITY;

-- STEP 2: Create basic policies for critical tables
CREATE POLICY "plans_select_authenticated" ON public.plans
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "plans_manage_service_role" ON public.plans
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "audit_logs_select_own" ON public.audit_logs
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        actor_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY "audit_logs_select_admin" ON public.audit_logs
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_user_id = auth.uid()
            AND role IN ('admin', 'super_admin', 'support', 'billing_admin')
        )
    );

CREATE POLICY "admin_actions_select_admin" ON public.admin_actions
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_user_id = auth.uid()
            AND role IN ('admin', 'super_admin', 'support', 'billing_admin')
        )
    );

CREATE POLICY "security_events_select_own" ON public.security_events
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

-- STEP 3: Fix extension security
CREATE SCHEMA IF NOT EXISTS extensions;
DROP EXTENSION IF EXISTS vector;
CREATE EXTENSION vector SCHEMA extensions;

-- STEP 4: Add ICP policies (basic ones)
CREATE POLICY "icp_disqualifiers_select_workspace" ON public.icp_disqualifiers
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        icp_profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id IN (
                SELECT id FROM public.workspaces
                WHERE owner_id = auth.uid()
            )
        )
    );

CREATE POLICY "icp_firmographics_select_workspace" ON public.icp_firmographics
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        icp_profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id IN (
                SELECT id FROM public.workspaces
                WHERE owner_id = auth.uid()
            )
        )
    );

CREATE POLICY "icp_pain_map_select_workspace" ON public.icp_pain_map
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        icp_profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id IN (
                SELECT id FROM public.workspaces
                WHERE owner_id = auth.uid()
            )
        )
    );

CREATE POLICY "icp_psycholinguistics_select_workspace" ON public.icp_psycholinguistics
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        icp_profile_id IN (
            SELECT id FROM public.icp_profiles
            WHERE workspace_id IN (
                SELECT id FROM public.workspaces
                WHERE owner_id = auth.uid()
            )
        )
    );

-- STEP 5: Grant permissions
GRANT ALL ON public.plans TO authenticated;
GRANT ALL ON public.plans TO service_role;
GRANT SELECT ON public.audit_logs TO authenticated;
GRANT ALL ON public.audit_logs TO service_role;
GRANT SELECT ON public.admin_actions TO authenticated;
GRANT ALL ON public.admin_actions TO service_role;
GRANT SELECT ON public.security_events TO authenticated;
GRANT ALL ON public.security_events TO service_role;
GRANT USAGE ON SCHEMA extensions TO authenticated;
GRANT USAGE ON SCHEMA extensions TO service_role;
GRANT USAGE ON SCHEMA extensions TO anon;
GRANT ALL ON public.icp_disqualifiers TO authenticated;
GRANT ALL ON public.icp_disqualifiers TO service_role;
GRANT ALL ON public.icp_firmographics TO authenticated;
GRANT ALL ON public.icp_firmographics TO service_role;
GRANT ALL ON public.icp_pain_map TO authenticated;
GRANT ALL ON public.icp_pain_map TO service_role;
GRANT ALL ON public.icp_psycholinguistics TO authenticated;
GRANT ALL ON public.icp_psycholinguistics TO service_role;

-- STEP 6: Update search path
ALTER DATABASE postgres SET search_path = "$user", public, extensions;
