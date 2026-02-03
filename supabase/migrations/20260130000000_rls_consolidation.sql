-- ============================================
-- RLS CONSOLIDATION MIGRATION
-- Consolidates duplicate policies from multiple migrations
-- Date: 2026-01-30
-- ============================================

-- NOTE: This migration uses DROP POLICY IF EXISTS to safely handle duplicates
-- All policies are consolidated into a single, clean set per table

-- ============================================
-- SECTION 1: USERS TABLE
-- ============================================

-- Enable RLS (should already be enabled)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Drop all duplicate users policies
DROP POLICY IF EXISTS "Users can view own data" ON public.users;
DROP POLICY IF EXISTS "Users can update own data" ON public.users;
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
DROP POLICY IF EXISTS "Users can view own identification" ON public.users;
DROP POLICY IF EXISTS "users_allow_authenticated" ON public.users;
DROP POLICY IF EXISTS "users_allow_update_self" ON public.users;
DROP POLICY IF EXISTS "users_service_all" ON public.users;
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;

-- Consolidated users policies
CREATE POLICY "users_view_own" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "users_update_own" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- ============================================
-- SECTION 2: WORKSPACES TABLE
-- ============================================

ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;

-- Drop duplicate workspace policies
DROP POLICY IF EXISTS "Users can view own workspaces" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_allow_authenticated" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_allow_update" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_allow_insert" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_select_simple" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_simple" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_insert_simple" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_select_own_optimized" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_own_optimized" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_insert_own_optimized" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_owner_all" ON public.workspaces;

-- Consolidated workspaces policies
CREATE POLICY "workspaces_view_member" ON public.workspaces
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspace_members
            WHERE workspace_members.workspace_id = public.workspaces.id
            AND workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "workspaces_insert_own" ON public.workspaces
    FOR INSERT WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "workspaces_update_own" ON public.workspaces
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM workspace_members
            WHERE workspace_members.workspace_id = public.workspaces.id
            AND workspace_members.user_id = auth.uid()
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- ============================================
-- SECTION 3: PROFILES TABLE
-- ============================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Drop duplicate profile policies
DROP POLICY IF EXISTS "profiles_service_all" ON public.profiles;
DROP POLICY IF EXISTS "profiles_allow_all" ON public.profiles;
DROP POLICY IF EXISTS "profiles_self_view" ON public.profiles;
DROP POLICY IF EXISTS "profiles_self_update" ON public.profiles;
DROP POLICY IF EXISTS "profiles_self_insert" ON public.profiles;
DROP POLICY IF EXISTS "profiles_service_insert" ON public.profiles;
DROP POLICY IF EXISTS "profiles_select_own_optimized" ON public.profiles;
DROP POLICY IF EXISTS "profiles_update_own_optimized" ON public.profiles;
DROP POLICY IF EXISTS "profiles_insert_system_optimized" ON public.profiles;

-- Consolidated profiles policies
CREATE POLICY "profiles_view_own" ON public.profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "profiles_insert_own" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "profiles_update_own" ON public.profiles
    FOR UPDATE USING (auth.uid() = user_id);

-- ============================================
-- SECTION 4: SUBSCRIPTIONS TABLE
-- ============================================

ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

-- Drop duplicate subscription policies
DROP POLICY IF EXISTS "subscriptions_service_all" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_allow_all" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_allow_authenticated" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_select_simple" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_select_own_optimized" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_select_admin_optimized" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_self_view" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_self_insert" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_self_update" ON public.subscriptions;

-- Consolidated subscriptions policies
CREATE POLICY "subscriptions_view_own" ON public.subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "subscriptions_insert_own" ON public.subscriptions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "subscriptions_update_own" ON public.subscriptions
    FOR UPDATE USING (auth.uid() = user_id);

-- ============================================
-- SECTION 5: PLANS TABLE
-- ============================================

ALTER TABLE public.plans ENABLE ROW LEVEL SECURITY;

-- Drop duplicate plans policies
DROP POLICY IF EXISTS "plans_service_all" ON public.plans;
DROP POLICY IF EXISTS "plans_allow_all" ON public.plans;
DROP POLICY IF EXISTS "plans_select_authenticated" ON public.plans;
DROP POLICY IF EXISTS "plans_manage_service_role" ON public.plans;
DROP POLICY IF EXISTS "plans_public_read" ON public.plans;

-- Consolidated plans policies
CREATE POLICY "plans_view_authenticated" ON public.plans
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "plans_manage_service_role" ON public.plans
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- SECTION 6: PAYMENT_TRANSACTIONS TABLE
-- ============================================

ALTER TABLE public.payment_transactions ENABLE ROW LEVEL SECURITY;

-- Drop duplicate payment transaction policies
DROP POLICY IF EXISTS "payment_transactions_select_own_optimized" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_select_admin_optimized" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_select_simple" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_allow_authenticated" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_allow_all" ON public.payment_transactions;

-- Consolidated payment transactions policies
CREATE POLICY "payments_view_own" ON public.payment_transactions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM subscriptions
            WHERE subscriptions.id = public.payment_transactions.subscription_id
            AND subscriptions.user_id = auth.uid()
        )
    );

CREATE POLICY "payments_insert_own" ON public.payment_transactions
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM subscriptions
            WHERE subscriptions.id = public.payment_transactions.subscription_id
            AND subscriptions.user_id = auth.uid()
        )
    );

-- ============================================
-- SECTION 7: PAYMENTS TABLE
-- ============================================

ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;

-- Drop duplicate payments policies
DROP POLICY IF EXISTS "payments_select_own_optimized" ON public.payments;
DROP POLICY IF EXISTS "payments_workspace_isolation_select" ON public.payments;
DROP POLICY IF EXISTS "payments_workspace_isolation_insert" ON public.payments;

-- Consolidated payments policies
CREATE POLICY "payments_view_own" ON public.payments
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "payments_insert_own" ON public.payments
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ============================================
-- SECTION 8: EMAIL_LOGS TABLE
-- ============================================

ALTER TABLE public.email_logs ENABLE ROW LEVEL SECURITY;

-- Drop duplicate email_logs policies
DROP POLICY IF EXISTS "email_logs_select_own_optimized" ON public.email_logs;
DROP POLICY IF EXISTS "email_logs_self_view" ON public.email_logs;

-- Consolidated email_logs policies
CREATE POLICY "email_logs_view_own" ON public.email_logs
    FOR SELECT USING (auth.uid() = user_id);

-- ============================================
-- SECTION 9: AUDIT_LOGS TABLE
-- ============================================

ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- Drop duplicate audit_logs policies
DROP POLICY IF EXISTS "audit_logs_select_own" ON public.audit_logs;
DROP POLICY IF EXISTS "audit_logs_select_admin" ON public.audit_logs;
DROP POLICY IF EXISTS "audit_logs_insert_service" ON public.audit_logs;
DROP POLICY IF EXISTS "audit_logs_self_insert" ON public.audit_logs;

-- Consolidated audit_logs policies
CREATE POLICY "audit_logs_view_own" ON public.audit_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "audit_logs_insert_service" ON public.audit_logs
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "audit_logs_view_admin" ON public.audit_logs
    FOR SELECT USING (auth.role() = 'service_role' OR auth.role() = 'authenticated');

-- ============================================
-- SECTION 10: ADMIN_ACTIONS TABLE
-- ============================================

ALTER TABLE public.admin_actions ENABLE ROW LEVEL SECURITY;

-- Drop duplicate admin_actions policies
DROP POLICY IF EXISTS "admin_actions_select_admin" ON public.admin_actions;
DROP POLICY IF EXISTS "admin_actions_insert_service" ON public.admin_actions;

-- Consolidated admin_actions policies
CREATE POLICY "admin_actions_view_admin" ON public.admin_actions
    FOR SELECT USING (auth.role() = 'service_role');

CREATE POLICY "admin_actions_insert_service" ON public.admin_actions
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- ============================================
-- SECTION 11: SECURITY_EVENTS TABLE
-- ============================================

ALTER TABLE public.security_events ENABLE ROW LEVEL SECURITY;

-- Drop duplicate security_events policies
DROP POLICY IF EXISTS "security_events_select_own" ON public.security_events;
DROP POLICY IF EXISTS "security_events_select_admin" ON public.security_events;
DROP POLICY IF EXISTS "security_events_insert_service" ON public.security_events;

-- Consolidated security_events policies
CREATE POLICY "security_events_view_own" ON public.security_events
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "security_events_view_admin" ON public.security_events
    FOR SELECT USING (auth.role() = 'service_role');

CREATE POLICY "security_events_insert_service" ON public.security_events
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- ============================================
-- SECTION 12: USER_SESSIONS TABLE
-- ============================================

ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

-- Drop duplicate user_sessions policies
DROP POLICY IF EXISTS "user_sessions_manage_own_optimized" ON public.user_sessions;

-- Consolidated user_sessions policies
CREATE POLICY "user_sessions_manage_own" ON public.user_sessions
    FOR ALL USING (auth.uid() = user_id);

-- ============================================
-- SECTION 13: BUSINESS_CONTEXT_MANIFESTS (BCM) TABLE
-- ============================================

ALTER TABLE public.business_context_manifests ENABLE ROW LEVEL SECURITY;

-- Drop duplicate BCM policies
DROP POLICY IF EXISTS "bcm_select_workspace_optimized" ON public.business_context_manifests;
DROP POLICY IF EXISTS "bcm_insert_workspace_optimized" ON public.business_context_manifests;
DROP POLICY IF EXISTS "bcm_manifests_workspace_isolation_select" ON public.bcm_manifests;

-- Consolidated BCM policies
CREATE POLICY "bcm_view_workspace" ON public.business_context_manifests
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.business_context_manifests.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

CREATE POLICY "bcm_insert_workspace" ON public.business_context_manifests
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.business_context_manifests.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

-- ============================================
-- SECTION 14: ICP_PROFILES TABLE
-- ============================================

ALTER TABLE public.icp_profiles ENABLE ROW LEVEL SECURITY;

-- Drop duplicate icp_profiles policies
DROP POLICY IF EXISTS "icp_select_workspace_optimized" ON public.icp_profiles;

-- Consolidated icp_profiles policies
CREATE POLICY "icp_view_workspace" ON public.icp_profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.icp_profiles.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

CREATE POLICY "icp_insert_workspace" ON public.icp_profiles
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.icp_profiles.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

-- ============================================
-- SECTION 15: FOUNDATIONS TABLE
-- ============================================

ALTER TABLE public.foundations ENABLE ROW LEVEL SECURITY;

-- Drop duplicate foundations policies
DROP POLICY IF EXISTS "foundations_select_workspace_optimized" ON public.foundations;

-- Consolidated foundations policies
CREATE POLICY "foundations_view_workspace" ON public.foundations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.foundations.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

CREATE POLICY "foundations_insert_workspace" ON public.foundations
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.foundations.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

-- ============================================
-- SECTION 16: SUBSCRIPTION_PLANS TABLE
-- ============================================

ALTER TABLE public.subscription_plans ENABLE ROW LEVEL SECURITY;

-- Drop duplicate subscription_plans policies
DROP POLICY IF EXISTS "subscription_plans_allow_authenticated" ON public.subscription_plans;
DROP POLICY IF EXISTS "Public can read active subscription plans" ON public.subscription_plans;
DROP POLICY IF EXISTS "Public can read subscription plans" ON public.subscription_plans;

-- Consolidated subscription_plans policies
CREATE POLICY "subscription_plans_view_active" ON public.subscription_plans
    FOR SELECT USING (is_active = true OR auth.role() = 'service_role');

-- ============================================
-- SECTION 17: USER_SUBSCRIPTIONS TABLE
-- ============================================

ALTER TABLE public.user_subscriptions ENABLE ROW LEVEL SECURITY;

-- Drop duplicate user_subscriptions policies
DROP POLICY IF EXISTS "Users can execute create_user_subscription" ON public.user_subscriptions;

-- Consolidated user_subscriptions policies
CREATE POLICY "user_subscriptions_view_own" ON public.user_subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "user_subscriptions_insert_own" ON public.user_subscriptions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "user_subscriptions_update_own" ON public.user_subscriptions
    FOR UPDATE USING (auth.uid() = user_id);

-- ============================================
-- SECTION 18: USER_ONBOARDING TABLE
-- ============================================

ALTER TABLE public.user_onboarding ENABLE ROW LEVEL SECURITY;

-- Drop duplicate user_onboarding policies
DROP POLICY IF EXISTS "user_onboarding_owner_select" ON public.user_onboarding;
DROP POLICY IF EXISTS "user_onboarding_owner_insert" ON public.user_onboarding;
DROP POLICY IF EXISTS "user_onboarding_owner_update" ON public.user_onboarding;
DROP POLICY IF EXISTS "user_onboarding_owner_delete" ON public.user_onboarding;

-- Consolidated user_onboarding policies
CREATE POLICY "user_onboarding_view_own" ON public.user_onboarding
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "user_onboarding_insert_own" ON public.user_onboarding
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "user_onboarding_update_own" ON public.user_onboarding
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "user_onboarding_delete_own" ON public.user_onboarding
    FOR DELETE USING (auth.uid() = user_id);

-- ============================================
-- SECTION 19: ICP_DISQUALIFIERS TABLE
-- ============================================

ALTER TABLE public.icp_disqualifiers ENABLE ROW LEVEL SECURITY;

-- Drop duplicate icp_disqualifiers policies
DROP POLICY IF EXISTS "icp_disqualifiers_select_workspace" ON public.icp_disqualifiers;
DROP POLICY IF EXISTS "icp_disqualifiers_insert_workspace" ON public.icp_disqualifiers;
DROP POLICY IF EXISTS "icp_disqualifiers_update_workspace" ON public.icp_disqualifiers;
DROP POLICY IF EXISTS "icp_disqualifiers_delete_workspace" ON public.icp_disqualifiers;

-- Consolidated icp_disqualifiers policies
CREATE POLICY "icp_disqualifiers_view_workspace" ON public.icp_disqualifiers
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.icp_disqualifiers.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

CREATE POLICY "icp_disqualifiers_insert_workspace" ON public.icp_disqualifiers
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.icp_disqualifiers.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

-- ============================================
-- SECTION 20: ICP_FIRMOGRAPHICS TABLE
-- ============================================

ALTER TABLE public.icp_firmographics ENABLE ROW LEVEL SECURITY;

-- Drop duplicate icp_firmographics policies
DROP POLICY IF EXISTS "icp_firmographics_select_workspace" ON public.icp_firmographics;
DROP POLICY IF EXISTS "icp_firmographics_insert_workspace" ON public.icp_firmographics;
DROP POLICY IF EXISTS "icp_firmographics_update_workspace" ON public.icp_firmographics;
DROP POLICY IF EXISTS "icp_firmographics_delete_workspace" ON public.icp_firmographics;

-- Consolidated icp_firmographics policies
CREATE POLICY "icp_firmographics_view_workspace" ON public.icp_firmographics
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.icp_firmographics.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

CREATE POLICY "icp_firmographics_insert_workspace" ON public.icp_firmographics
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.icp_firmographics.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

-- ============================================
-- SECTION 21: ICP_PAIN_MAP TABLE
-- ============================================

ALTER TABLE public.icp_pain_map ENABLE ROW LEVEL SECURITY;

-- Drop duplicate icp_pain_map policies
DROP POLICY IF EXISTS "icp_pain_map_select_workspace" ON public.icp_pain_map;
DROP POLICY IF EXISTS "icp_pain_map_insert_workspace" ON public.icp_pain_map;
DROP POLICY IF EXISTS "icp_pain_map_update_workspace" ON public.icp_pain_map;
DROP POLICY IF EXISTS "icp_pain_map_delete_workspace" ON public.icp_pain_map;

-- Consolidated icp_pain_map policies
CREATE POLICY "icp_pain_map_view_workspace" ON public.icp_pain_map
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.icp_pain_map.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

CREATE POLICY "icp_pain_map_insert_workspace" ON public.icp_pain_map
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.icp_pain_map.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

-- ============================================
-- SECTION 22: ICP_PSYCHOLINGUISTICS TABLE
-- ============================================

ALTER TABLE public.icp_psycholinguistics ENABLE ROW LEVEL SECURITY;

-- Drop duplicate icp_psycholinguistics policies
DROP POLICY IF EXISTS "icp_psycholinguistics_select_workspace" ON public.icp_psycholinguistics;
DROP POLICY IF EXISTS "icp_psycholinguistics_insert_workspace" ON public.icp_psycholinguistics;
DROP POLICY IF EXISTS "icp_psycholinguistics_update_workspace" ON public.icp_psycholinguistics;
DROP POLICY IF EXISTS "icp_psycholinguistics_delete_workspace" ON public.icp_psycholinguistics;

-- Consolidated icp_psycholinguistics policies
CREATE POLICY "icp_psycholinguistics_view_workspace" ON public.icp_psycholinguistics
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.icp_psycholinguistics.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

CREATE POLICY "icp_psycholinguistics_insert_workspace" ON public.icp_psycholinguistics
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.icp_psycholinguistics.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

-- ============================================
-- SECTION 23: BCM_EVENTS TABLE
-- ============================================

ALTER TABLE public.bcm_events ENABLE ROW LEVEL SECURITY;

-- Drop duplicate bcm_events policies
DROP POLICY IF EXISTS "bcm_events_delete_isolation" ON public.bcm_events;

-- Consolidated bcm_events policies
CREATE POLICY "bcm_events_view_workspace" ON public.bcm_events
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.bcm_events.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

CREATE POLICY "bcm_events_insert_workspace" ON public.bcm_events
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM workspaces
            WHERE workspaces.id = public.bcm_events.workspace_id
            AND EXISTS (
                SELECT 1 FROM workspace_members
                WHERE workspace_members.workspace_id = workspaces.id
                AND workspace_members.user_id = auth.uid()
            )
        )
    );

-- ============================================
-- SECTION 24: PAYMENT_AUDIT_LOG TABLE
-- ============================================

ALTER TABLE public.payment_audit_log ENABLE ROW LEVEL SECURITY;

-- Drop duplicate payment_audit_log policies
DROP POLICY IF EXISTS "Admins can view all audit logs" ON public.payment_audit_log;

-- Consolidated payment_audit_log policies
CREATE POLICY "payment_audit_log_view_admin" ON public.payment_audit_log
    FOR SELECT USING (auth.role() = 'service_role');

-- ============================================
-- SECTION 25: PAYMENT_SECURITY_EVENTS TABLE
-- ============================================

ALTER TABLE public.payment_security_events ENABLE ROW LEVEL SECURITY;

-- Drop duplicate payment_security_events policies
DROP POLICY IF EXISTS "Admins can view all security events" ON public.payment_security_events;

-- Consolidated payment_security_events policies
CREATE POLICY "payment_security_events_view_admin" ON public.payment_security_events
    FOR SELECT USING (auth.role() = 'service_role');

-- ============================================
-- VERIFICATION: List all policies after consolidation
-- ============================================

-- This is informational only - queries current policies
-- SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public' ORDER BY tablename, policyname;

-- NOTE: Duplicate content removed. Properly scoped policies including owner_id check
-- and service_role bypass are created in:
-- - 20260130_fix_duplicate_subscription_plans.sql (workspaces, subscriptions, payment_transactions)
-- - 20260130_comprehensive_security_fixes.sql (ICP tables, users)
-- - 134_fix_rls_performance.sql (profiles, foundations, bcm, etc.)

-- ============================================
-- VERIFICATION: List all policies after consolidation
-- ============================================

-- This is informational only - queries current policies
-- SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public' ORDER BY tablename, policyname;

