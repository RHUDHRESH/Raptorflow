-- =================================================================
-- CHUNK 1: CRITICAL SECURITY FIXES
-- Run this first - fixes the 4 ERROR level RLS issues
-- =================================================================

-- STEP 1: Enable RLS on critical tables (ERROR level issues)
ALTER TABLE public.plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.admin_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_events ENABLE ROW LEVEL SECURITY;

-- STEP 2: Create basic RLS policies for critical tables
-- Plans table policies
CREATE POLICY "plans_select_authenticated" ON public.plans
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "plans_manage_service_role" ON public.plans
    FOR ALL USING (auth.role() = 'service_role');

-- Audit logs policies
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

CREATE POLICY "audit_logs_insert_service" ON public.audit_logs
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- Admin actions policies
CREATE POLICY "admin_actions_select_admin" ON public.admin_actions
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth_user_id = auth.uid() 
            AND role IN ('admin', 'super_admin', 'support', 'billing_admin')
        )
    );

CREATE POLICY "admin_actions_insert_service" ON public.admin_actions
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- Security events policies
CREATE POLICY "security_events_select_own" ON public.security_events
    FOR SELECT USING (
        auth.role() = 'authenticated' AND 
        user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY "security_events_select_admin" ON public.security_events
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth_user_id = auth.uid() 
            AND role IN ('admin', 'super_admin', 'support', 'billing_admin')
        )
    );

CREATE POLICY "security_events_insert_service" ON public.security_events
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- STEP 3: Grant permissions for critical tables
GRANT ALL ON public.plans TO authenticated;
GRANT ALL ON public.plans TO service_role;
GRANT SELECT ON public.audit_logs TO authenticated;
GRANT ALL ON public.audit_logs TO service_role;
GRANT SELECT ON public.admin_actions TO authenticated;
GRANT ALL ON public.admin_actions TO service_role;
GRANT SELECT ON public.security_events TO authenticated;
GRANT ALL ON public.security_events TO service_role;

-- =================================================================
-- CHUNK 1 COMPLETE
-- Fixed: 4 ERROR level RLS disabled issues
-- Next: Run CHUNK 2 for function and extension security
-- =================================================================
