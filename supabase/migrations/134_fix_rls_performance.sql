-- =================================================================
-- PERFORMANCE FIXES: RLS Auth Function Optimization
-- Migration: 134_fix_rls_performance.sql
-- Priority: MEDIUM - Cleanup legacy policies, scoped policies created elsewhere
-- =================================================================

-- This migration now only drops legacy policies
-- Properly scoped policies are created in:
-- - 20260130_fix_duplicate_subscription_plans.sql (workspaces, subscriptions, payment_transactions)
-- - 20260130_comprehensive_security_fixes.sql (ICP tables, users)

-- Drop legacy subscription policies (scoped policies created elsewhere)
DROP POLICY IF EXISTS "Users can view own subscription" ON public.subscriptions;
DROP POLICY IF EXISTS "Admins can view all subscriptions" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_select_own_optimized" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_select_admin_optimized" ON public.subscriptions;

-- Drop legacy payment_transactions policies (scoped policies created elsewhere)
DROP POLICY IF EXISTS "Users can view own transactions" ON public.payment_transactions;
DROP POLICY IF EXISTS "Admins can view all transactions" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_select_own_optimized" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_select_admin_optimized" ON public.payment_transactions;

-- User sessions - properly scoped policy
DROP POLICY IF EXISTS "Users can manage own sessions" ON public.user_sessions;
DROP POLICY IF EXISTS "user_sessions_manage_own_optimized" ON public.user_sessions;

CREATE POLICY "user_sessions_scoped" ON public.user_sessions
    FOR ALL USING (
        user_id = auth.uid()
    );

CREATE POLICY "user_sessions_service_role" ON public.user_sessions
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Business context manifests - workspace-scoped policy
DROP POLICY IF EXISTS "bcm_select_workspace" ON public.business_context_manifests;
DROP POLICY IF EXISTS "bcm_insert_workspace" ON public.business_context_manifests;
DROP POLICY IF EXISTS "bcm_select_workspace_optimized" ON public.business_context_manifests;
DROP POLICY IF EXISTS "bcm_insert_workspace_optimized" ON public.business_context_manifests;

CREATE POLICY "bcm_select_scoped" ON public.business_context_manifests
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = business_context_manifests.workspace_id
            AND (
                w.owner_id = auth.uid()
                OR EXISTS (
                    SELECT 1 FROM public.workspace_members wm
                    WHERE wm.workspace_id = w.id
                    AND wm.user_id = auth.uid()
                    AND wm.is_active = true
                )
            )
        )
    );

CREATE POLICY "bcm_insert_scoped" ON public.business_context_manifests
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = business_context_manifests.workspace_id
            AND (
                w.owner_id = auth.uid()
                OR EXISTS (
                    SELECT 1 FROM public.workspace_members wm
                    WHERE wm.workspace_id = w.id
                    AND wm.user_id = auth.uid()
                    AND wm.role IN ('owner', 'admin')
                    AND wm.is_active = true
                )
            )
        )
    );

CREATE POLICY "bcm_update_scoped" ON public.business_context_manifests
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = business_context_manifests.workspace_id
            AND (
                w.owner_id = auth.uid()
                OR EXISTS (
                    SELECT 1 FROM public.workspace_members wm
                    WHERE wm.workspace_id = w.id
                    AND wm.user_id = auth.uid()
                    AND wm.role IN ('owner', 'admin')
                    AND wm.is_active = true
                )
            )
        )
    );

CREATE POLICY "bcm_service_role" ON public.business_context_manifests
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Foundations - workspace-scoped policy
DROP POLICY IF EXISTS "foundations_select_workspace" ON public.foundations;
DROP POLICY IF EXISTS "foundations_select_workspace_optimized" ON public.foundations;

CREATE POLICY "foundations_select_scoped" ON public.foundations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = foundations.workspace_id
            AND (
                w.owner_id = auth.uid()
                OR EXISTS (
                    SELECT 1 FROM public.workspace_members wm
                    WHERE wm.workspace_id = w.id
                    AND wm.user_id = auth.uid()
                    AND wm.is_active = true
                )
            )
        )
    );

CREATE POLICY "foundations_insert_scoped" ON public.foundations
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = foundations.workspace_id
            AND (
                w.owner_id = auth.uid()
                OR EXISTS (
                    SELECT 1 FROM public.workspace_members wm
                    WHERE wm.workspace_id = w.id
                    AND wm.user_id = auth.uid()
                    AND wm.role IN ('owner', 'admin')
                    AND wm.is_active = true
                )
            )
        )
    );

CREATE POLICY "foundations_update_scoped" ON public.foundations
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = foundations.workspace_id
            AND (
                w.owner_id = auth.uid()
                OR EXISTS (
                    SELECT 1 FROM public.workspace_members wm
                    WHERE wm.workspace_id = w.id
                    AND wm.user_id = auth.uid()
                    AND wm.role IN ('owner', 'admin')
                    AND wm.is_active = true
                )
            )
        )
    );

CREATE POLICY "foundations_service_role" ON public.foundations
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ICP profiles - workspace-scoped policy
DROP POLICY IF EXISTS "icp_select_workspace" ON public.icp_profiles;
DROP POLICY IF EXISTS "icp_select_workspace_optimized" ON public.icp_profiles;

CREATE POLICY "icp_profiles_select_scoped" ON public.icp_profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_profiles.workspace_id
            AND (
                w.owner_id = auth.uid()
                OR EXISTS (
                    SELECT 1 FROM public.workspace_members wm
                    WHERE wm.workspace_id = w.id
                    AND wm.user_id = auth.uid()
                    AND wm.is_active = true
                )
            )
        )
    );

CREATE POLICY "icp_profiles_insert_scoped" ON public.icp_profiles
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_profiles.workspace_id
            AND (
                w.owner_id = auth.uid()
                OR EXISTS (
                    SELECT 1 FROM public.workspace_members wm
                    WHERE wm.workspace_id = w.id
                    AND wm.user_id = auth.uid()
                    AND wm.role IN ('owner', 'admin')
                    AND wm.is_active = true
                )
            )
        )
    );

CREATE POLICY "icp_profiles_update_scoped" ON public.icp_profiles
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_profiles.workspace_id
            AND (
                w.owner_id = auth.uid()
                OR EXISTS (
                    SELECT 1 FROM public.workspace_members wm
                    WHERE wm.workspace_id = w.id
                    AND wm.user_id = auth.uid()
                    AND wm.role IN ('owner', 'admin')
                    AND wm.is_active = true
                )
            )
        )
    );

CREATE POLICY "icp_profiles_delete_scoped" ON public.icp_profiles
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_profiles.workspace_id
            AND w.owner_id = auth.uid()
        )
    );

CREATE POLICY "icp_profiles_service_role" ON public.icp_profiles
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Profiles - user-scoped policy
DROP POLICY IF EXISTS "profiles_select_own" ON public.profiles;
DROP POLICY IF EXISTS "profiles_update_own" ON public.profiles;
DROP POLICY IF EXISTS "profiles_insert_system" ON public.profiles;
DROP POLICY IF EXISTS "profiles_select_own_optimized" ON public.profiles;
DROP POLICY IF EXISTS "profiles_update_own_optimized" ON public.profiles;
DROP POLICY IF EXISTS "profiles_insert_system_optimized" ON public.profiles;

CREATE POLICY "profiles_select_scoped" ON public.profiles
    FOR SELECT USING (id = auth.uid());

CREATE POLICY "profiles_update_scoped" ON public.profiles
    FOR UPDATE USING (id = auth.uid());

CREATE POLICY "profiles_service_role" ON public.profiles
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Drop legacy workspace policies (scoped policies created elsewhere)
DROP POLICY IF EXISTS "workspaces_select_own" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_own" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_insert_own" ON public.workspaces;
DROP POLICY IF EXISTS "Users can view own workspace" ON public.workspaces;
DROP POLICY IF EXISTS "Users can update own workspace" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_select_own_optimized" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_own_optimized" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_insert_own_optimized" ON public.workspaces;

-- Drop legacy users policies (scoped policies created elsewhere)
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
DROP POLICY IF EXISTS "Admins can view all users" ON public.users;
DROP POLICY IF EXISTS "Admins can update users" ON public.users;
DROP POLICY IF EXISTS "users_select_own_optimized" ON public.users;
DROP POLICY IF EXISTS "users_update_own_optimized" ON public.users;
DROP POLICY IF EXISTS "users_select_admin_optimized" ON public.users;
DROP POLICY IF EXISTS "users_update_admin_optimized" ON public.users;

-- Payments - user-scoped policy
DROP POLICY IF EXISTS "payments_self_view" ON public.payments;
DROP POLICY IF EXISTS "payments_select_own_optimized" ON public.payments;

CREATE POLICY "payments_select_scoped" ON public.payments
    FOR SELECT USING (user_profile_id = auth.uid());

CREATE POLICY "payments_insert_scoped" ON public.payments
    FOR INSERT WITH CHECK (user_profile_id = auth.uid());

CREATE POLICY "payments_service_role" ON public.payments
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Email logs - user-scoped policy
DROP POLICY IF EXISTS "email_logs_self_view" ON public.email_logs;
DROP POLICY IF EXISTS "email_logs_select_own_optimized" ON public.email_logs;

CREATE POLICY "email_logs_select_scoped" ON public.email_logs
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "email_logs_service_role" ON public.email_logs
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');
