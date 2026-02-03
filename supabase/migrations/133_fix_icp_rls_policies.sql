-- =================================================================
-- SECURITY FIXES: ICP Tables RLS Policy Cleanup
-- Migration: 133_fix_icp_rls_policies.sql
-- Priority: MEDIUM - Drops legacy policies, scoped policies created elsewhere
-- =================================================================

-- Note: Properly scoped ICP policies are created in:
-- - 20260130_comprehensive_security_fixes.sql

-- Drop legacy icp_disqualifiers policies
DROP POLICY IF EXISTS "icp_disqualifiers_select_workspace" ON public.icp_disqualifiers;
DROP POLICY IF EXISTS "icp_disqualifiers_insert_workspace" ON public.icp_disqualifiers;
DROP POLICY IF EXISTS "icp_disqualifiers_update_workspace" ON public.icp_disqualifiers;
DROP POLICY IF EXISTS "icp_disqualifiers_delete_workspace" ON public.icp_disqualifiers;

-- Drop legacy icp_firmographics policies
DROP POLICY IF EXISTS "icp_firmographics_select_workspace" ON public.icp_firmographics;
DROP POLICY IF EXISTS "icp_firmographics_insert_workspace" ON public.icp_firmographics;
DROP POLICY IF EXISTS "icp_firmographics_update_workspace" ON public.icp_firmographics;
DROP POLICY IF EXISTS "icp_firmographics_delete_workspace" ON public.icp_firmographics;

-- Drop legacy icp_pain_map policies
DROP POLICY IF EXISTS "icp_pain_map_select_workspace" ON public.icp_pain_map;
DROP POLICY IF EXISTS "icp_pain_map_insert_workspace" ON public.icp_pain_map;
DROP POLICY IF EXISTS "icp_pain_map_update_workspace" ON public.icp_pain_map;
DROP POLICY IF EXISTS "icp_pain_map_delete_workspace" ON public.icp_pain_map;

-- Drop legacy icp_psycholinguistics policies
DROP POLICY IF EXISTS "icp_psycholinguistics_select_workspace" ON public.icp_psycholinguistics;
DROP POLICY IF EXISTS "icp_psycholinguistics_insert_workspace" ON public.icp_psycholinguistics;
DROP POLICY IF EXISTS "icp_psycholinguistics_update_workspace" ON public.icp_psycholinguistics;
DROP POLICY IF EXISTS "icp_psycholinguistics_delete_workspace" ON public.icp_psycholinguistics;

-- Grant necessary permissions (keep these)
GRANT SELECT, INSERT, UPDATE, DELETE ON public.icp_disqualifiers TO authenticated;
GRANT ALL ON public.icp_disqualifiers TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.icp_firmographics TO authenticated;
GRANT ALL ON public.icp_firmographics TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.icp_pain_map TO authenticated;
GRANT ALL ON public.icp_pain_map TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.icp_psycholinguistics TO authenticated;
GRANT ALL ON public.icp_psycholinguistics TO service_role;
