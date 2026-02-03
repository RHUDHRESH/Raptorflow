-- ============================================
-- CANONICAL RLS POLICIES MIGRATION
-- Consolidated Row Level Security policies for all tables
-- Date: 2026-01-30
-- ============================================

BEGIN;

-- ============================================
-- USERS TABLE RLS
-- ============================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "users_view_own" ON public.users;
DROP POLICY IF EXISTS "users_update_own" ON public.users;

CREATE POLICY "users_view_own" ON public.users
    FOR SELECT USING (auth.uid() = auth_user_id);

CREATE POLICY "users_update_own" ON public.users
    FOR UPDATE USING (auth.uid() = auth_user_id);

-- ============================================
-- WORKSPACES TABLE RLS
-- ============================================
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "workspaces_view_member" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_insert_own" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_admin" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_delete_owner" ON public.workspaces;

CREATE POLICY "workspaces_view_member" ON public.workspaces
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.workspace_members
            WHERE workspace_members.workspace_id = workspaces.id
            AND workspace_members.user_id = (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
        )
    );

CREATE POLICY "workspaces_insert_own" ON public.workspaces
    FOR INSERT WITH CHECK (
        owner_id = (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY "workspaces_update_admin" ON public.workspaces
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workspace_members
            WHERE workspace_members.workspace_id = workspaces.id
            AND workspace_members.user_id = (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "workspaces_delete_owner" ON public.workspaces
    FOR DELETE USING (
        owner_id = (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
    );

-- ============================================
-- WORKSPACE_MEMBERS TABLE RLS
-- ============================================
ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "workspace_members_view_member" ON public.workspace_members;
DROP POLICY IF EXISTS "workspace_members_insert_admin" ON public.workspace_members;
DROP POLICY IF EXISTS "workspace_members_update_admin" ON public.workspace_members;
DROP POLICY IF EXISTS "workspace_members_delete_admin" ON public.workspace_members;

CREATE POLICY "workspace_members_view_member" ON public.workspace_members
    FOR SELECT USING (
        user_id = (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
        OR EXISTS (
            SELECT 1 FROM public.workspace_members wm
            WHERE wm.workspace_id = workspace_members.workspace_id
            AND wm.user_id = (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
        )
    );

CREATE POLICY "workspace_members_insert_admin" ON public.workspace_members
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workspace_members wm
            WHERE wm.workspace_id = workspace_members.workspace_id
            AND wm.user_id = (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
            AND wm.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "workspace_members_update_admin" ON public.workspace_members
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workspace_members wm
            WHERE wm.workspace_id = workspace_members.workspace_id
            AND wm.user_id = (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
            AND wm.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "workspace_members_delete_admin" ON public.workspace_members
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.workspace_members wm
            WHERE wm.workspace_id = workspace_members.workspace_id
            AND wm.user_id = (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
            AND wm.role IN ('owner', 'admin')
        )
    );

-- ============================================
-- SUBSCRIPTION_PLANS TABLE RLS
-- ============================================
ALTER TABLE public.subscription_plans ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "subscription_plans_view_authenticated" ON public.subscription_plans;
DROP POLICY IF EXISTS "subscription_plans_manage_service_role" ON public.subscription_plans;

CREATE POLICY "subscription_plans_view_authenticated" ON public.subscription_plans
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "subscription_plans_manage_service_role" ON public.subscription_plans
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- USER_SUBSCRIPTIONS TABLE RLS
-- ============================================
ALTER TABLE public.user_subscriptions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "user_subscriptions_view_member" ON public.user_subscriptions;
DROP POLICY IF EXISTS "user_subscriptions_insert_admin" ON public.user_subscriptions;
DROP POLICY IF EXISTS "user_subscriptions_update_admin" ON public.user_subscriptions;
DROP POLICY IF EXISTS "user_subscriptions_service_role" ON public.user_subscriptions;

CREATE POLICY "user_subscriptions_view_member" ON public.user_subscriptions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.workspace_members
            WHERE workspace_members.workspace_id = user_subscriptions.workspace_id
            AND workspace_members.user_id = (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
        )
    );

CREATE POLICY "user_subscriptions_insert_admin" ON public.user_subscriptions
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workspace_members
            WHERE workspace_members.workspace_id = user_subscriptions.workspace_id
            AND workspace_members.user_id = (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "user_subscriptions_update_admin" ON public.user_subscriptions
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workspace_members
            WHERE workspace_members.workspace_id = user_subscriptions.workspace_id
            AND workspace_members.user_id = (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "user_subscriptions_service_role" ON public.user_subscriptions
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- SUBSCRIPTION_EVENTS TABLE RLS
-- ============================================
ALTER TABLE public.subscription_events ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "subscription_events_view_member" ON public.subscription_events;
DROP POLICY IF EXISTS "subscription_events_service_role" ON public.subscription_events;

CREATE POLICY "subscription_events_view_member" ON public.subscription_events
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.user_subscriptions us
            JOIN public.workspace_members wm ON wm.workspace_id = us.workspace_id
            WHERE us.id = subscription_events.subscription_id
            AND wm.user_id = (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
        )
    );

CREATE POLICY "subscription_events_service_role" ON public.subscription_events
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- PAYMENT_TRANSACTIONS TABLE RLS
-- ============================================
ALTER TABLE public.payment_transactions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "payment_transactions_view_member" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_service_role" ON public.payment_transactions;

CREATE POLICY "payment_transactions_view_member" ON public.payment_transactions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.user_subscriptions us
            JOIN public.workspace_members wm ON wm.workspace_id = us.workspace_id
            WHERE us.id = payment_transactions.subscription_id
            AND wm.user_id = (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
        )
    );

CREATE POLICY "payment_transactions_service_role" ON public.payment_transactions
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- COMMENTS
-- ============================================
COMMENT ON POLICY "users_view_own" ON public.users IS 'Users can view their own profile';
COMMENT ON POLICY "users_update_own" ON public.users IS 'Users can update their own profile';
COMMENT ON POLICY "workspaces_view_member" ON public.workspaces IS 'Workspace members can view workspace';
COMMENT ON POLICY "workspaces_insert_own" ON public.workspaces IS 'Users can create workspaces they own';
COMMENT ON POLICY "workspaces_update_admin" ON public.workspaces IS 'Admins and owners can update workspace';
COMMENT ON POLICY "workspaces_delete_owner" ON public.workspaces IS 'Only owners can delete workspace';

COMMIT;
