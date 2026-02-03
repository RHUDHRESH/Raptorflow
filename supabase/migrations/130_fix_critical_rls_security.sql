-- =================================================================
-- CRITICAL SECURITY FIXES: RLS Disabled Issues
-- Migration: 130_fix_critical_rls_security.sql
-- Priority: HIGH - Fixes security vulnerabilities
-- =================================================================

-- Enable RLS on critical tables that are missing it
ALTER TABLE public.plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.admin_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_events ENABLE ROW LEVEL SECURITY;

-- Drop legacy policies first
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

-- Plans table - public reference data, readable by all authenticated users
CREATE POLICY "plans_select_scoped" ON public.plans
    FOR SELECT USING (true);  -- Plans are public reference data

CREATE POLICY "plans_service_role" ON public.plans
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Audit logs - users can only view their own
CREATE POLICY "audit_logs_select_scoped" ON public.audit_logs
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "audit_logs_service_role" ON public.audit_logs
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Admin actions - only service role (backend) can access
CREATE POLICY "admin_actions_service_role" ON public.admin_actions
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Security events - users can only view their own
CREATE POLICY "security_events_select_scoped" ON public.security_events
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "security_events_service_role" ON public.security_events
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Grant necessary permissions
GRANT SELECT ON public.plans TO authenticated;
GRANT ALL ON public.plans TO service_role;
GRANT SELECT ON public.audit_logs TO authenticated;
GRANT ALL ON public.audit_logs TO service_role;
GRANT ALL ON public.admin_actions TO service_role;
GRANT SELECT ON public.security_events TO authenticated;
GRANT ALL ON public.security_events TO service_role;
