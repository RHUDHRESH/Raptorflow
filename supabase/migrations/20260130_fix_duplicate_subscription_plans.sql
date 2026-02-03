-- =================================================================
-- FIX DUPLICATE SUBSCRIPTION PLANS AND REINSTATE SCOPED RLS
-- Issue: Plans displayed twice, infinite recursion in users policy
-- Fix: Replace overly permissive policies with properly scoped RLS
-- This migration should be run AFTER 20260130_drop_old_table_adopt_archive_schema.sql
-- =================================================================

-- =================================================================
-- STEP 1: DROP PERMISSIVE SIMPLE POLICIES
-- =================================================================

-- Drop overly permissive workspace policies
DROP POLICY IF EXISTS "workspaces_select_consolidated" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_consolidated" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_select_simple" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_simple" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_insert_simple" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_unified" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_insert_unified" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_unified" ON public.workspaces;

-- Drop overly permissive subscription policies
DROP POLICY IF EXISTS "subscriptions_select_consolidated" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_select_simple" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_unified" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_insert_unified" ON public.subscriptions;

-- Drop overly permissive payment_transactions policies
DROP POLICY IF EXISTS "payment_transactions_select_consolidated" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_select_simple" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_unified" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_insert_unified" ON public.payment_transactions;

-- =================================================================
-- STEP 2: CREATE PROPERLY SCOPED WORKSPACE POLICIES
-- Users can access workspaces they own OR are members of
-- =================================================================

-- SELECT: User owns workspace OR is a member via workspace_members
CREATE POLICY "workspaces_select_scoped" ON public.workspaces
    FOR SELECT USING (
        owner_id = auth.uid()
        OR EXISTS (
            SELECT 1 FROM public.workspace_members wm
            WHERE wm.workspace_id = workspaces.id
            AND wm.user_id = auth.uid()
            AND wm.is_active = true
        )
    );

-- UPDATE: User owns workspace OR is admin/owner member
CREATE POLICY "workspaces_update_scoped" ON public.workspaces
    FOR UPDATE USING (
        owner_id = auth.uid()
        OR EXISTS (
            SELECT 1 FROM public.workspace_members wm
            WHERE wm.workspace_id = workspaces.id
            AND wm.user_id = auth.uid()
            AND wm.role IN ('owner', 'admin')
            AND wm.is_active = true
        )
    );

-- INSERT: User can create workspaces where they are the owner
CREATE POLICY "workspaces_insert_scoped" ON public.workspaces
    FOR INSERT WITH CHECK (
        owner_id = auth.uid()
    );

-- DELETE: Only owner can delete workspace
CREATE POLICY "workspaces_delete_scoped" ON public.workspaces
    FOR DELETE USING (
        owner_id = auth.uid()
    );

-- Service role bypass for backend operations
CREATE POLICY "workspaces_service_role" ON public.workspaces
    FOR ALL USING (
        auth.jwt() ->> 'role' = 'service_role'
    );

-- =================================================================
-- STEP 3: CREATE PROPERLY SCOPED SUBSCRIPTION POLICIES
-- Users can access subscriptions for workspaces they own or are members of
-- =================================================================

-- SELECT: User owns the workspace OR is a member
CREATE POLICY "subscriptions_select_scoped" ON public.subscriptions
    FOR SELECT USING (
        -- Direct user_profile_id match (if column exists)
        (user_profile_id IS NOT NULL AND user_profile_id = auth.uid())
        -- OR workspace-based access
        OR EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = subscriptions.workspace_id
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

-- UPDATE: User owns the workspace OR is admin member
CREATE POLICY "subscriptions_update_scoped" ON public.subscriptions
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = subscriptions.workspace_id
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

-- INSERT: User owns the workspace
CREATE POLICY "subscriptions_insert_scoped" ON public.subscriptions
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = subscriptions.workspace_id
            AND w.owner_id = auth.uid()
        )
    );

-- Service role bypass for webhooks and backend processes
CREATE POLICY "subscriptions_service_role" ON public.subscriptions
    FOR ALL USING (
        auth.jwt() ->> 'role' = 'service_role'
    );

-- =================================================================
-- STEP 4: CREATE PROPERLY SCOPED PAYMENT_TRANSACTIONS POLICIES
-- Users can access their own transactions
-- =================================================================

-- SELECT: User owns the transaction (via user_id or customer_id)
CREATE POLICY "payment_transactions_select_scoped" ON public.payment_transactions
    FOR SELECT USING (
        user_id = auth.uid()
        OR customer_id = auth.uid()::text
    );

-- INSERT: User can create their own transactions
CREATE POLICY "payment_transactions_insert_scoped" ON public.payment_transactions
    FOR INSERT WITH CHECK (
        user_id = auth.uid()
        OR customer_id = auth.uid()::text
    );

-- UPDATE: User can update their own transactions
CREATE POLICY "payment_transactions_update_scoped" ON public.payment_transactions
    FOR UPDATE USING (
        user_id = auth.uid()
        OR customer_id = auth.uid()::text
    );

-- Service role bypass for webhooks and backend processes
CREATE POLICY "payment_transactions_service_role" ON public.payment_transactions
    FOR ALL USING (
        auth.jwt() ->> 'role' = 'service_role'
    );

-- =================================================================
-- STEP 5: FIX DUPLICATE SUBSCRIPTION PLANS
-- =================================================================

-- Remove any duplicate subscription plans (keep only one of each slug)
DELETE FROM public.subscription_plans p1
WHERE p1.ctid > (
    SELECT MIN(p2.ctid)
    FROM public.subscription_plans p2
    WHERE p1.slug = p2.slug
);

-- Ensure subscription_plans table has proper constraints
ALTER TABLE public.subscription_plans DROP CONSTRAINT IF EXISTS subscription_plans_pkey CASCADE;
ALTER TABLE public.subscription_plans ADD PRIMARY KEY (id);

-- Ensure unique constraints exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'subscription_plans_name_key'
    ) THEN
        ALTER TABLE public.subscription_plans
        ADD CONSTRAINT subscription_plans_name_key UNIQUE (name);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'subscription_plans_slug_key'
    ) THEN
        ALTER TABLE public.subscription_plans
        ADD CONSTRAINT subscription_plans_slug_key UNIQUE (slug);
    END IF;
END $$;

-- =================================================================
-- LOG COMPLETION
-- =================================================================
DO $$
DECLARE
    plan_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO plan_count FROM public.subscription_plans;
    RAISE NOTICE '✅ Fixed duplicate subscription plans. Total plans: %', plan_count;
    RAISE NOTICE '✅ Reinstated properly scoped RLS policies for workspaces, subscriptions, payment_transactions';
    RAISE NOTICE '   - workspaces: owner OR workspace_members access';
    RAISE NOTICE '   - subscriptions: workspace owner/member access';
    RAISE NOTICE '   - payment_transactions: user_id/customer_id access';
    RAISE NOTICE '   - Service role bypass preserved for all tables';
END $$;
