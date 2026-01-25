-- =================================================================
-- COMPLETE SECURITY FIXES - APPLY ALL AT ONCE
-- Run this in Supabase Dashboard > SQL Editor
-- =================================================================

-- STEP 1: CRITICAL SECURITY FIXES
-- Enable RLS on critical tables
ALTER TABLE public.plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.admin_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_events ENABLE ROW LEVEL SECURITY;

-- STEP 2: CREATE RLS POLICIES FOR CRITICAL TABLES
-- Drop existing policies first to avoid conflicts
DROP POLICY IF EXISTS "plans_select_authenticated" ON public.plans;
DROP POLICY IF EXISTS "plans_manage_service_role" ON public.plans;
DROP POLICY IF EXISTS "audit_logs_select_own" ON public.audit_logs;
DROP POLICY IF EXISTS "audit_logs_select_admin" ON public.audit_logs;
DROP POLICY IF EXISTS "audit_logs_insert_service" ON public.audit_logs;
DROP POLICY IF EXISTS "admin_actions_select_admin" ON public.admin_actions;
DROP POLICY IF EXISTS "admin_actions_insert_service" ON public.admin_actions;
DROP POLICY IF EXISTS "security_events_select_own" ON public.security_events;
DROP POLICY IF EXISTS "security_events_select_admin" ON public.security_events;
DROP POLICY IF EXISTS "security_events_insert_service" ON public.security_events;

-- Plans table policies
CREATE POLICY "plans_select_authenticated" ON public.plans
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "plans_manage_service_role" ON public.plans
    FOR ALL USING (auth.role() = 'service_role');

-- Audit logs policies - using actor_id instead of user_id
CREATE POLICY "audit_logs_select_own" ON public.audit_logs
    FOR SELECT USING (
        auth.role() = 'authenticated' AND 
        actor_id = (select auth.uid())
    );

CREATE POLICY "audit_logs_select_admin" ON public.audit_logs
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = (select auth.uid()) AND role = 'admin'
        )
    );

CREATE POLICY "audit_logs_insert_service" ON public.audit_logs
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- Admin actions policies
CREATE POLICY "admin_actions_select_admin" ON public.admin_actions
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = (select auth.uid()) AND role = 'admin'
        )
    );

CREATE POLICY "admin_actions_insert_service" ON public.admin_actions
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- Security events policies - using user_id (assuming it exists)
CREATE POLICY "security_events_select_own" ON public.security_events
    FOR SELECT USING (
        auth.role() = 'authenticated' AND 
        user_id = (select auth.uid())
    );

CREATE POLICY "security_events_select_admin" ON public.security_events
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = (select auth.uid()) AND role = 'admin'
        )
    );

CREATE POLICY "security_events_insert_service" ON public.security_events
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- STEP 3: FIX FUNCTION SECURITY
-- Drop and recreate functions with fixed search_path
DROP FUNCTION IF EXISTS public.update_updated_at_column CASCADE;

CREATE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

DROP FUNCTION IF EXISTS public.get_user_by_auth_uid CASCADE;

CREATE FUNCTION public.get_user_by_auth_uid(user_auth_uid text)
RETURNS TABLE (
    id uuid,
    email text,
    role text,
    is_active boolean,
    created_at timestamptz,
    updated_at timestamptz
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id,
        u.email,
        u.role,
        u.is_active,
        u.created_at,
        u.updated_at
    FROM public.users u
    WHERE u.auth_uid = user_auth_uid
    AND u.is_active = true;
END;
$$;

DROP FUNCTION IF EXISTS public.handle_new_user CASCADE;

CREATE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    workspace_id uuid;
BEGIN
    -- Create a default workspace for the new user
    INSERT INTO public.workspaces (name, slug, owner_id, status)
    VALUES (
        'Default Workspace',
        'default-' || substr(md5(NEW.id::text), 1, 8),
        NEW.id,
        'active'
    ) RETURNING id INTO workspace_id;
    
    -- Update user with workspace reference
    UPDATE public.users 
    SET workspace_id = workspace_id 
    WHERE id = NEW.id;
    
    RETURN NEW;
END;
$$;

DROP FUNCTION IF EXISTS public.update_updated_at CASCADE;

CREATE FUNCTION public.update_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

-- STEP 4: FIX EXTENSION SECURITY
-- Create extensions schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS extensions;

-- Move vector extension from public to extensions schema
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension 
        WHERE extname = 'vector' 
        AND extnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
    ) THEN
        DROP EXTENSION IF EXISTS vector CASCADE;
        CREATE EXTENSION IF NOT EXISTS vector SCHEMA extensions;
        RAISE NOTICE 'Vector extension moved from public to extensions schema';
    ELSE
        CREATE EXTENSION IF NOT EXISTS vector SCHEMA extensions;
        RAISE NOTICE 'Vector extension created in extensions schema';
    END IF;
END $$;

-- STEP 5: ADD MISSING RLS POLICIES FOR ICP TABLES
-- Drop existing policies first
DROP POLICY IF EXISTS "icp_disqualifiers_select_workspace" ON public.icp_disqualifiers;
DROP POLICY IF EXISTS "icp_disqualifiers_insert_workspace" ON public.icp_disqualifiers;
DROP POLICY IF EXISTS "icp_disqualifiers_update_workspace" ON public.icp_disqualifiers;
DROP POLICY IF EXISTS "icp_disqualifiers_delete_workspace" ON public.icp_disqualifiers;
DROP POLICY IF EXISTS "icp_firmographics_select_workspace" ON public.icp_firmographics;
DROP POLICY IF EXISTS "icp_firmographics_insert_workspace" ON public.icp_firmographics;
DROP POLICY IF EXISTS "icp_firmographics_update_workspace" ON public.icp_firmographics;
DROP POLICY IF EXISTS "icp_firmographics_delete_workspace" ON public.icp_firmographics;
DROP POLICY IF EXISTS "icp_pain_map_select_workspace" ON public.icp_pain_map;
DROP POLICY IF EXISTS "icp_pain_map_insert_workspace" ON public.icp_pain_map;
DROP POLICY IF EXISTS "icp_pain_map_update_workspace" ON public.icp_pain_map;
DROP POLICY IF EXISTS "icp_pain_map_delete_workspace" ON public.icp_pain_map;
DROP POLICY IF EXISTS "icp_psycholinguistics_select_workspace" ON public.icp_psycholinguistics;
DROP POLICY IF EXISTS "icp_psycholinguistics_insert_workspace" ON public.icp_psycholinguistics;
DROP POLICY IF EXISTS "icp_psycholinguistics_update_workspace" ON public.icp_psycholinguistics;
DROP POLICY IF EXISTS "icp_psycholinguistics_delete_workspace" ON public.icp_psycholinguistics;

-- icp_disqualifiers policies
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

-- icp_firmographics policies
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

-- icp_pain_map policies
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

-- icp_psycholinguistics policies
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

-- STEP 6: OPTIMIZE RLS POLICIES FOR PERFORMANCE
-- Drop old policies and create optimized ones
DROP POLICY IF EXISTS "Users can view own subscription" ON public.subscriptions;
DROP POLICY IF EXISTS "Admins can view all subscriptions" ON public.subscriptions;

CREATE POLICY "subscriptions_select_optimized" ON public.subscriptions
    FOR SELECT USING (
        auth.role() = 'authenticated' AND (
            user_id = (select auth.uid()) OR
            EXISTS (
                SELECT 1 FROM public.profiles 
                WHERE id = (select auth.uid()) AND role = 'admin'
            )
        )
    );

DROP POLICY IF EXISTS "Users can view own transactions" ON public.payment_transactions;
DROP POLICY IF EXISTS "Admins can view all transactions" ON public.payment_transactions;

CREATE POLICY "payment_transactions_select_optimized" ON public.payment_transactions
    FOR SELECT USING (
        auth.role() = 'authenticated' AND (
            user_id = (select auth.uid()) OR
            EXISTS (
                SELECT 1 FROM public.profiles 
                WHERE id = (select auth.uid()) AND role = 'admin'
            )
        )
    );

-- STEP 7: ADD MISSING INDEXES
-- Foreign key indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS 
idx_payment_transactions_plan_id_fkey 
ON public.payment_transactions(plan_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS 
idx_payment_transactions_subscription_id_fkey 
ON public.payment_transactions(subscription_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS 
idx_users_banned_by_fkey 
ON public.users(banned_by);

-- Performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS 
idx_user_sessions_user_active_expires 
ON public.user_sessions(user_id, is_active, expires_at)
WHERE is_active = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS 
idx_payment_transactions_user_status_created 
ON public.payment_transactions(user_id, status, created_at);

CREATE INDEX CONCURRENTLY IF NOT EXISTS 
idx_subscriptions_user_status_period 
ON public.subscriptions(user_id, status, current_period_end)
WHERE status IN ('active', 'trialing');

-- STEP 8: REMOVE UNUSED INDEXES
DROP INDEX CONCURRENTLY IF EXISTS idx_payments_user_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_email_logs_user_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_users_email;
DROP INDEX CONCURRENTLY IF EXISTS idx_users_onboarding_status;
DROP INDEX CONCURRENTLY IF EXISTS idx_users_role;
DROP INDEX CONCURRENTLY IF EXISTS idx_users_is_active;
DROP INDEX CONCURRENTLY IF EXISTS idx_users_created_at;
DROP INDEX CONCURRENTLY IF EXISTS idx_workspaces_user_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_workspaces_slug;
DROP INDEX CONCURRENTLY IF EXISTS idx_workspaces_status;
DROP INDEX CONCURRENTLY IF EXISTS idx_subscriptions_user_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_subscriptions_status;
DROP INDEX CONCURRENTLY IF EXISTS idx_subscriptions_plan_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_subscriptions_current_period_end;
DROP INDEX CONCURRENTLY IF EXISTS idx_payment_transactions_user_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_payment_transactions_transaction_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_payment_transactions_status;
DROP INDEX CONCURRENTLY IF EXISTS idx_payment_transactions_created_at;
DROP INDEX CONCURRENTLY IF EXISTS idx_user_sessions_user_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_user_sessions_session_token;
DROP INDEX CONCURRENTLY IF EXISTS idx_user_sessions_is_active;
DROP INDEX CONCURRENTLY IF EXISTS idx_user_sessions_expires_at;
DROP INDEX CONCURRENTLY IF EXISTS idx_audit_logs_actor_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_audit_logs_action;
DROP INDEX CONCURRENTLY IF EXISTS idx_audit_logs_created_at;
DROP INDEX CONCURRENTLY IF EXISTS idx_audit_logs_target_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_admin_actions_admin_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_admin_actions_target_user_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_admin_actions_created_at;
DROP INDEX CONCURRENTLY IF EXISTS idx_security_events_user_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_security_events_event_type;
DROP INDEX CONCURRENTLY IF EXISTS idx_security_events_created_at;
DROP INDEX CONCURRENTLY IF EXISTS idx_profiles_email;
DROP INDEX CONCURRENTLY IF EXISTS idx_profiles_workspace;
DROP INDEX CONCURRENTLY IF EXISTS idx_profiles_role;
DROP INDEX CONCURRENTLY IF EXISTS idx_profiles_subscription;
DROP INDEX CONCURRENTLY IF EXISTS idx_bcm_workspace;
DROP INDEX CONCURRENTLY IF EXISTS idx_bcm_version;
DROP INDEX CONCURRENTLY IF EXISTS idx_bcm_checksum;
DROP INDEX CONCURRENTLY IF EXISTS idx_foundations_workspace;
DROP INDEX CONCURRENTLY IF EXISTS idx_foundations_status;
DROP INDEX CONCURRENTLY IF EXISTS idx_foundations_embedding;
DROP INDEX CONCURRENTLY IF EXISTS idx_icp_workspace;
DROP INDEX CONCURRENTLY IF EXISTS idx_icp_name;
DROP INDEX CONCURRENTLY IF EXISTS idx_icp_firmographics_profile;
DROP INDEX CONCURRENTLY IF EXISTS idx_icp_pain_profile;
DROP INDEX CONCURRENTLY IF EXISTS idx_icp_psycholinguistics_profile;
DROP INDEX CONCURRENTLY IF EXISTS idx_icp_disqualifiers_profile;

-- STEP 9: GRANT NECESSARY PERMISSIONS
GRANT ALL ON public.plans TO authenticated;
GRANT ALL ON public.plans TO service_role;
GRANT SELECT ON public.audit_logs TO authenticated;
GRANT ALL ON public.audit_logs TO service_role;
GRANT SELECT ON public.admin_actions TO authenticated;
GRANT ALL ON public.admin_actions TO service_role;
GRANT SELECT ON public.security_events TO authenticated;
GRANT ALL ON public.security_events TO service_role;
GRANT EXECUTE ON FUNCTION public.update_updated_at_column TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_user_by_auth_uid TO authenticated;
GRANT EXECUTE ON FUNCTION public.handle_new_user TO service_role;
GRANT EXECUTE ON FUNCTION public.update_updated_at TO authenticated;
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

-- STEP 10: UPDATE DATABASE SEARCH PATH
ALTER DATABASE postgres SET search_path = "$user", public, extensions;

-- =================================================================
-- COMPLETION MESSAGE
-- All security and performance fixes have been applied!
-- 
-- Next Steps:
-- 1. Enable leaked password protection in Supabase Dashboard > Authentication > Settings
-- 2. Run the Database Advisor again to verify all issues are resolved
-- =================================================================
