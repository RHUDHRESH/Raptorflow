-- RLS Hardening for Foundations
DROP POLICY IF EXISTS "Users can view own foundation" ON public.foundations;
DROP POLICY IF EXISTS "foundations_select_isolation" ON public.foundations;
CREATE POLICY "foundations_select_isolation" ON public.foundations
    FOR SELECT USING (check_membership(workspace_id));

DROP POLICY IF EXISTS "Users can create own foundation" ON public.foundations;
DROP POLICY IF EXISTS "foundations_insert_isolation" ON public.foundations;
CREATE POLICY "foundations_insert_isolation" ON public.foundations
    FOR INSERT WITH CHECK (check_membership(workspace_id));

DROP POLICY IF EXISTS "Users can update own foundation" ON public.foundations;
DROP POLICY IF EXISTS "foundations_update_isolation" ON public.foundations;
CREATE POLICY "foundations_update_isolation" ON public.foundations
    FOR UPDATE USING (check_membership(workspace_id));

-- RLS Hardening for ICP Profiles
DROP POLICY IF EXISTS "Users can view own ICP profiles" ON public.icp_profiles;
DROP POLICY IF EXISTS "icp_select_isolation" ON public.icp_profiles;
CREATE POLICY "icp_select_isolation" ON public.icp_profiles
    FOR SELECT USING (check_membership(workspace_id));

DROP POLICY IF EXISTS "Users can create own ICP profiles" ON public.icp_profiles;
DROP POLICY IF EXISTS "icp_insert_isolation" ON public.icp_profiles;
CREATE POLICY "icp_insert_isolation" ON public.icp_profiles
    FOR INSERT WITH CHECK (check_membership(workspace_id));

-- RLS Hardening for Blackbox Strategies
DROP POLICY IF EXISTS "Users can view blackbox strategies" ON public.blackbox_strategies;
DROP POLICY IF EXISTS "strategies_select_isolation" ON public.blackbox_strategies;
CREATE POLICY "strategies_select_isolation" ON public.blackbox_strategies
    FOR SELECT USING (check_membership(workspace_id));
