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

-- Create RLS policies for plans table
-- Only authenticated users can view plans
CREATE POLICY "plans_select_authenticated" ON public.plans
    FOR SELECT USING (auth.role() = 'authenticated');

-- Only service role can insert/update/delete plans
CREATE POLICY "plans_manage_service_role" ON public.plans
    FOR ALL USING (auth.role() = 'service_role');

-- Create RLS policies for audit_logs table
-- Only authenticated users can view their own audit logs
CREATE POLICY "audit_logs_select_own" ON public.audit_logs
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        user_id = (select auth.uid())
    );

-- Admins can view all audit logs
CREATE POLICY "audit_logs_select_admin" ON public.audit_logs
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = (select auth.uid()) AND role = 'admin'
        )
    );

-- Only service role can insert audit logs
CREATE POLICY "audit_logs_insert_service" ON public.audit_logs
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- Create RLS policies for admin_actions table
-- Only admins can view admin actions
CREATE POLICY "admin_actions_select_admin" ON public.admin_actions
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = (select auth.uid()) AND role = 'admin'
        )
    );

-- Only service role can insert admin actions
CREATE POLICY "admin_actions_insert_service" ON public.admin_actions
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- Create RLS policies for security_events table
-- Users can view their own security events
CREATE POLICY "security_events_select_own" ON public.security_events
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        user_id = (select auth.uid())
    );

-- Admins can view all security events
CREATE POLICY "security_events_select_admin" ON public.security_events
    FOR SELECT USING (
        auth.role() = 'authenticated' AND
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = (select auth.uid()) AND role = 'admin'
        )
    );

-- Only service role can insert security events
CREATE POLICY "security_events_insert_service" ON public.security_events
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- Grant necessary permissions
GRANT ALL ON public.plans TO authenticated;
GRANT ALL ON public.plans TO service_role;
GRANT SELECT ON public.audit_logs TO authenticated;
GRANT ALL ON public.audit_logs TO service_role;
GRANT SELECT ON public.admin_actions TO authenticated;
GRANT ALL ON public.admin_actions TO service_role;
GRANT SELECT ON public.security_events TO authenticated;
GRANT ALL ON public.security_events TO service_role;
