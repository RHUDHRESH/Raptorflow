-- =================================================================
-- COMPREHENSIVE SECURITY FIXES
-- This script addresses all security issues including:
-- 1. Enable RLS on all critical tables
-- 2. Create missing policies for ICP tables
-- 3. Consolidate duplicate policies
-- 4. Add missing foreign key indexes and remove unused indexes
-- 5. Grant appropriate privileges
-- =================================================================

-- =================================================================
-- STEP 1: ENABLE RLS ON ALL CRITICAL TABLES
-- =================================================================

ALTER TABLE public.plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.admin_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_events ENABLE ROW LEVEL SECURITY;

RAISE NOTICE '✅ Enabled RLS on critical tables';

-- =================================================================
-- STEP 2: CREATE PROPERLY SCOPED POLICIES FOR ICP TABLES
-- Users can access ICP data for workspaces they own OR are members of
-- =================================================================

-- ICP Disqualifiers policies
DROP POLICY IF EXISTS "icp_disqualifiers_select_own" ON public.icp_disqualifiers;
CREATE POLICY "icp_disqualifiers_select_scoped" ON public.icp_disqualifiers
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_disqualifiers.workspace_id
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

DROP POLICY IF EXISTS "icp_disqualifiers_insert_own" ON public.icp_disqualifiers;
CREATE POLICY "icp_disqualifiers_insert_scoped" ON public.icp_disqualifiers
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_disqualifiers.workspace_id
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

DROP POLICY IF EXISTS "icp_disqualifiers_update_own" ON public.icp_disqualifiers;
CREATE POLICY "icp_disqualifiers_update_scoped" ON public.icp_disqualifiers
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_disqualifiers.workspace_id
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

DROP POLICY IF EXISTS "icp_disqualifiers_delete_own" ON public.icp_disqualifiers;
CREATE POLICY "icp_disqualifiers_delete_scoped" ON public.icp_disqualifiers
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_disqualifiers.workspace_id
            AND w.owner_id = auth.uid()
        )
    );

CREATE POLICY "icp_disqualifiers_service_role" ON public.icp_disqualifiers
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ICP Firmographics policies
DROP POLICY IF EXISTS "icp_firmographics_select_own" ON public.icp_firmographics;
CREATE POLICY "icp_firmographics_select_scoped" ON public.icp_firmographics
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_firmographics.workspace_id
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

DROP POLICY IF EXISTS "icp_firmographics_insert_own" ON public.icp_firmographics;
CREATE POLICY "icp_firmographics_insert_scoped" ON public.icp_firmographics
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_firmographics.workspace_id
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

DROP POLICY IF EXISTS "icp_firmographics_update_own" ON public.icp_firmographics;
CREATE POLICY "icp_firmographics_update_scoped" ON public.icp_firmographics
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_firmographics.workspace_id
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

DROP POLICY IF EXISTS "icp_firmographics_delete_own" ON public.icp_firmographics;
CREATE POLICY "icp_firmographics_delete_scoped" ON public.icp_firmographics
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_firmographics.workspace_id
            AND w.owner_id = auth.uid()
        )
    );

CREATE POLICY "icp_firmographics_service_role" ON public.icp_firmographics
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ICP Pain Map policies
DROP POLICY IF EXISTS "icp_pain_map_select_own" ON public.icp_pain_map;
CREATE POLICY "icp_pain_map_select_scoped" ON public.icp_pain_map
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_pain_map.workspace_id
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

DROP POLICY IF EXISTS "icp_pain_map_insert_own" ON public.icp_pain_map;
CREATE POLICY "icp_pain_map_insert_scoped" ON public.icp_pain_map
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_pain_map.workspace_id
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

DROP POLICY IF EXISTS "icp_pain_map_update_own" ON public.icp_pain_map;
CREATE POLICY "icp_pain_map_update_scoped" ON public.icp_pain_map
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_pain_map.workspace_id
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

DROP POLICY IF EXISTS "icp_pain_map_delete_own" ON public.icp_pain_map;
CREATE POLICY "icp_pain_map_delete_scoped" ON public.icp_pain_map
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_pain_map.workspace_id
            AND w.owner_id = auth.uid()
        )
    );

CREATE POLICY "icp_pain_map_service_role" ON public.icp_pain_map
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ICP Psycholinguistics policies
DROP POLICY IF EXISTS "icp_psycholinguistics_select_own" ON public.icp_psycholinguistics;
CREATE POLICY "icp_psycholinguistics_select_scoped" ON public.icp_psycholinguistics
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_psycholinguistics.workspace_id
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

DROP POLICY IF EXISTS "icp_psycholinguistics_insert_own" ON public.icp_psycholinguistics;
CREATE POLICY "icp_psycholinguistics_insert_scoped" ON public.icp_psycholinguistics
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_psycholinguistics.workspace_id
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

DROP POLICY IF EXISTS "icp_psycholinguistics_update_own" ON public.icp_psycholinguistics;
CREATE POLICY "icp_psycholinguistics_update_scoped" ON public.icp_psycholinguistics
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_psycholinguistics.workspace_id
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

DROP POLICY IF EXISTS "icp_psycholinguistics_delete_own" ON public.icp_psycholinguistics;
CREATE POLICY "icp_psycholinguistics_delete_scoped" ON public.icp_psycholinguistics
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.workspaces w
            WHERE w.id = icp_psycholinguistics.workspace_id
            AND w.owner_id = auth.uid()
        )
    );

CREATE POLICY "icp_psycholinguistics_service_role" ON public.icp_psycholinguistics
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

RAISE NOTICE '✅ Created missing policies for ICP tables';

-- =================================================================
-- STEP 3: CLEAN UP DUPLICATE/LEGACY POLICIES
-- Note: Scoped policies are created in 20260130_fix_duplicate_subscription_plans.sql
-- This step only drops legacy policies to avoid conflicts
-- =================================================================

-- Drop legacy payment_transactions policies (scoped policies created elsewhere)
DROP POLICY IF EXISTS "payment_transactions_select_consolidated" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_select_own_optimized" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_select_admin_optimized" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_select_simple" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_allow_authenticated" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_allow_all" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_unified" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_insert_own_optimized" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_insert_own" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_insert_unified" ON public.payment_transactions;

-- Drop legacy subscriptions policies (scoped policies created elsewhere)
DROP POLICY IF EXISTS "subscriptions_select_consolidated" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_select_simple" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_unified" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_insert_own" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_insert_unified" ON public.subscriptions;

-- Drop legacy users policies - create properly scoped user policy
DROP POLICY IF EXISTS "users_select_consolidated" ON public.users;
DROP POLICY IF EXISTS "users_select_own" ON public.users;
DROP POLICY IF EXISTS "users_unified" ON public.users;

-- Users can only see their own record (scoped by auth_user_id or id)
CREATE POLICY "users_select_scoped" ON public.users
    FOR SELECT USING (
        auth_user_id = auth.uid()
        OR id = auth.uid()
    );

CREATE POLICY "users_update_scoped" ON public.users
    FOR UPDATE USING (
        auth_user_id = auth.uid()
        OR id = auth.uid()
    );

CREATE POLICY "users_service_role" ON public.users
    FOR ALL USING (
        auth.jwt() ->> 'role' = 'service_role'
    );

-- Drop legacy workspaces policies (scoped policies created elsewhere)
DROP POLICY IF EXISTS "workspaces_select_consolidated" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_select_simple" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_simple" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_insert_simple" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_unified" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_insert_own" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_insert_unified" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_own" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_unified" ON public.workspaces;

RAISE NOTICE '✅ Consolidated duplicate policies';

-- =================================================================
-- STEP 4: ADD MISSING FOREIGN KEY INDEXES AND REMOVE UNUSED INDEXES
-- =================================================================

-- Create indexes on payment_transactions foreign keys
CREATE INDEX IF NOT EXISTS idx_payment_transactions_user_id_fkey
    ON public.payment_transactions(user_id);

CREATE INDEX IF NOT EXISTS idx_payment_transactions_subscription_id_fkey
    ON public.payment_transactions(subscription_id);

CREATE INDEX IF NOT EXISTS idx_payment_transactions_plan_id_fkey
    ON public.payment_transactions(plan_id);

-- Create indexes on subscriptions foreign keys
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id_fkey
    ON public.subscriptions(user_id);

CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_id_fkey
    ON public.subscriptions(plan_id);

-- Remove unused indexes (as reported by Supabase advisor)
DROP INDEX IF EXISTS idx_payment_transactions_user_id ON public.payment_transactions;
DROP INDEX IF EXISTS idx_payment_transactions_transaction_id ON public.payment_transactions;
DROP INDEX IF EXISTS idx_payment_transactions_status ON public.payment_transactions;
DROP INDEX IF EXISTS idx_payment_transactions_created_at ON public.payment_transactions;
DROP INDEX IF EXISTS idx_subscriptions_status ON public.subscriptions;
DROP INDEX IF EXISTS idx_subscriptions_current_period_end ON public.subscriptions;
DROP INDEX IF EXISTS idx_user_sessions_user_id ON public.user_sessions;

RAISE NOTICE '✅ Added missing foreign key indexes and removed unused indexes';

-- =================================================================
-- STEP 5: GRANT APPROPRIATE PRIVILEGES
-- =================================================================

-- Grant authenticated users necessary select rights
GRANT SELECT ON public.plans TO authenticated;
GRANT SELECT ON public.audit_logs TO authenticated;
GRANT SELECT ON public.admin_actions TO authenticated;
GRANT SELECT ON public.security_events TO authenticated;
GRANT SELECT ON public.icp_disqualifiers TO authenticated;
GRANT SELECT ON public.icp_firmographics TO authenticated;
GRANT SELECT ON public.icp_pain_map TO authenticated;
GRANT SELECT ON public.icp_psycholinguistics TO authenticated;
GRANT SELECT ON public.payment_transactions TO authenticated;
GRANT SELECT ON public.subscriptions TO authenticated;
GRANT SELECT ON public.users TO authenticated;
GRANT SELECT ON public.workspaces TO authenticated;

-- Grant service role full access
GRANT ALL ON public.plans TO service_role;
GRANT ALL ON public.audit_logs TO service_role;
GRANT ALL ON public.admin_actions TO service_role;
GRANT ALL ON public.security_events TO service_role;
GRANT ALL ON public.icp_disqualifiers TO service_role;
GRANT ALL ON public.icp_firmographics TO service_role;
GRANT ALL ON public.icp_pain_map TO service_role;
GRANT ALL ON public.icp_psycholinguistics TO service_role;
GRANT ALL ON public.payment_transactions TO service_role;
GRANT ALL ON public.subscriptions TO service_role;
GRANT ALL ON public.users TO service_role;
GRANT ALL ON public.workspaces TO service_role;

-- Grant insert/update/delete rights where appropriate
GRANT INSERT, UPDATE, DELETE ON public.icp_disqualifiers TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.icp_firmographics TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.icp_pain_map TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.icp_psycholinguistics TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.workspaces TO authenticated;

RAISE NOTICE '✅ Granted appropriate privileges';

-- =================================================================
-- MIGRATION COMPLETE
-- =================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════';
    RAISE NOTICE '✅ COMPREHENSIVE SECURITY FIXES COMPLETED';
    RAISE NOTICE '═════════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE 'Summary:';
    RAISE NOTICE '  1. Enabled RLS on all critical tables';
    RAISE NOTICE '  2. Created missing policies for ICP tables';
    RAISE NOTICE '  3. Consolidated duplicate policies';
    RAISE NOTICE '  4. Added missing foreign key indexes and removed unused indexes';
    RAISE NOTICE '  5. Granted appropriate privileges';
    RAISE NOTICE '';
END $$;
