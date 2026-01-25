-- =================================================================
-- PERFORMANCE FIXES: RLS Auth Function Optimization
-- Migration: 134_fix_rls_performance.sql
-- Priority: MEDIUM - Optimizes RLS policies for better performance
-- =================================================================

-- Fix auth RLS initialization plan issues by wrapping auth functions in SELECT
-- This prevents re-evaluation for each row

-- Drop and recreate optimized policies for subscriptions table
DROP POLICY IF EXISTS "Users can view own subscription" ON public.subscriptions;
DROP POLICY IF EXISTS "Admins can view all subscriptions" ON public.subscriptions;

CREATE POLICY "subscriptions_select_own_optimized" ON public.subscriptions
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        user_id = (select auth.uid())
    );

CREATE POLICY "subscriptions_select_admin_optimized" ON public.subscriptions
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = (select auth.uid()) AND role = 'admin'
        )
    );

-- Drop and recreate optimized policies for payment_transactions table
DROP POLICY IF EXISTS "Users can view own transactions" ON public.payment_transactions;
DROP POLICY IF EXISTS "Admins can view all transactions" ON public.payment_transactions;

CREATE POLICY "payment_transactions_select_own_optimized" ON public.payment_transactions
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        user_id = (select auth.uid())
    );

CREATE POLICY "payment_transactions_select_admin_optimized" ON public.payment_transactions
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = (select auth.uid()) AND role = 'admin'
        )
    );

-- Drop and recreate optimized policies for user_sessions table
DROP POLICY IF EXISTS "Users can manage own sessions" ON public.user_sessions;

CREATE POLICY "user_sessions_manage_own_optimized" ON public.user_sessions
    FOR ALL USING (
        auth.role() = 'authenticated' AND
        user_id = (select auth.uid())
    );

-- Drop and recreate optimized policies for business_context_manifests table
DROP POLICY IF EXISTS "bcm_select_workspace" ON public.business_context_manifests;
DROP POLICY IF EXISTS "bcm_insert_workspace" ON public.business_context_manifests;

CREATE POLICY "bcm_select_workspace_optimized" ON public.business_context_manifests
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        workspace_id = (
            SELECT workspace_id FROM public.profiles
            WHERE id = (select auth.uid())
        )
    );

CREATE POLICY "bcm_insert_workspace_optimized" ON public.business_context_manifests
    FOR INSERT WITH CHECK (
        auth.role() = 'authenticated' AND
        workspace_id = (
            SELECT workspace_id FROM public.profiles
            WHERE id = (select auth.uid())
        )
    );

-- Drop and recreate optimized policies for foundations table
DROP POLICY IF EXISTS "foundations_select_workspace" ON public.foundations;

CREATE POLICY "foundations_select_workspace_optimized" ON public.foundations
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        workspace_id = (
            SELECT workspace_id FROM public.profiles
            WHERE id = (select auth.uid())
        )
    );

-- Drop and recreate optimized policies for icp_profiles table
DROP POLICY IF EXISTS "icp_select_workspace" ON public.icp_profiles;

CREATE POLICY "icp_select_workspace_optimized" ON public.icp_profiles
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        workspace_id = (
            SELECT workspace_id FROM public.profiles
            WHERE id = (select auth.uid())
        )
    );

-- Drop and recreate optimized policies for profiles table
DROP POLICY IF EXISTS "profiles_select_own" ON public.profiles;
DROP POLICY IF EXISTS "profiles_update_own" ON public.profiles;
DROP POLICY IF EXISTS "profiles_insert_system" ON public.profiles;

CREATE POLICY "profiles_select_own_optimized" ON public.profiles
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        id = (select auth.uid())
    );

CREATE POLICY "profiles_update_own_optimized" ON public.profiles
    FOR UPDATE USING (
        auth.role() = 'authenticated' AND
        id = (select auth.uid())
    );

CREATE POLICY "profiles_insert_system_optimized" ON public.profiles
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- Drop and recreate optimized policies for workspaces table
DROP POLICY IF EXISTS "workspaces_select_own" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_own" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_insert_own" ON public.workspaces;
DROP POLICY IF EXISTS "Users can view own workspace" ON public.workspaces;
DROP POLICY IF EXISTS "Users can update own workspace" ON public.workspaces;

CREATE POLICY "workspaces_select_own_optimized" ON public.workspaces
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        id = (SELECT workspace_id FROM public.profiles WHERE id = (select auth.uid()))
    );

CREATE POLICY "workspaces_update_own_optimized" ON public.workspaces
    FOR UPDATE USING (
        auth.role() = 'authenticated' AND
        id = (SELECT workspace_id FROM public.profiles WHERE id = (select auth.uid()))
    );

CREATE POLICY "workspaces_insert_own_optimized" ON public.workspaces
    FOR INSERT WITH CHECK (
        auth.role() = 'authenticated' AND
        owner_id = (select auth.uid())
    );

-- Drop and recreate optimized policies for users table
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
DROP POLICY IF EXISTS "Admins can view all users" ON public.users;
DROP POLICY IF EXISTS "Admins can update users" ON public.users;

CREATE POLICY "users_select_own_optimized" ON public.users
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        id = (select auth.uid())
    );

CREATE POLICY "users_update_own_optimized" ON public.users
    FOR UPDATE USING (
        auth.role() = 'authenticated' AND
        id = (select auth.uid())
    );

CREATE POLICY "users_select_admin_optimized" ON public.users
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = (select auth.uid()) AND role = 'admin'
        )
    );

CREATE POLICY "users_update_admin_optimized" ON public.users
    FOR UPDATE USING (
        auth.role() = 'authenticated' AND
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = (select auth.uid()) AND role = 'admin'
        )
    );

-- Drop and recreate optimized policies for payments table
DROP POLICY IF EXISTS "payments_self_view" ON public.payments;

CREATE POLICY "payments_select_own_optimized" ON public.payments
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        user_id = (select auth.uid())
    );

-- Drop and recreate optimized policies for email_logs table
DROP POLICY IF EXISTS "email_logs_self_view" ON public.email_logs;

CREATE POLICY "email_logs_select_own_optimized" ON public.email_logs
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        user_id = (select auth.uid())
    );
