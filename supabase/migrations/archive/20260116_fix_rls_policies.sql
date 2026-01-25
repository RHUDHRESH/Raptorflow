-- Fix RLS policies to use consistent auth.uid() pattern
-- Migration: 20260116_fix_rls_policies.sql
-- This migration fixes the inconsistency where some policies use auth_user_id instead of auth.uid()

-- Drop and recreate users table policies with correct auth.uid() usage
DROP POLICY IF EXISTS "Users can view own profile" ON users;
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Admins can view all users" ON users;
CREATE POLICY "Admins can view all users" ON users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = id 
            AND role IN ('admin', 'super_admin', 'support', 'billing_admin')
        )
    );

DROP POLICY IF EXISTS "Users can update own profile" ON users;
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

DROP POLICY IF EXISTS "Admins can update users" ON users;
CREATE POLICY "Admins can update users" ON users
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = id 
            AND role IN ('admin', 'super_admin')
        )
    );

DROP POLICY IF EXISTS "Super admins can delete users" ON users;
CREATE POLICY "Super admins can delete users" ON users
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = id 
            AND role = 'super_admin'
        )
    );

-- Fix workspace policies
DROP POLICY IF EXISTS "Users can view workspaces" ON workspaces;
CREATE POLICY "Users can view workspaces" ON workspaces
    FOR SELECT
    USING (
        id IN (
            SELECT workspace_id FROM public.workspace_members
            WHERE user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can create workspaces (they become owner)" ON workspaces;
CREATE POLICY "Users can create workspaces (they become owner)" ON workspaces
    FOR INSERT
    WITH CHECK (auth.uid() = owner_id);

DROP POLICY IF EXISTS "Workspace admins and owners can update" ON workspaces;
CREATE POLICY "Workspace admins and owners can update" ON workspaces
    FOR UPDATE
    USING (
        id IN (
            SELECT workspace_id FROM public.workspace_members
            WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
        )
    )
    OR auth.uid() = owner_id;

DROP POLICY IF EXISTS "Only owners can delete workspaces" ON workspaces;
CREATE POLICY "Only owners can delete workspaces" ON workspaces
    FOR DELETE
    USING (owner_id = auth.uid());

-- Fix workspace members policies
DROP POLICY IF EXISTS "Users can view memberships for their workspaces" ON workspace_members;
CREATE POLICY "Users can view memberships for their workspaces" ON workspace_members
    FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM public.workspace_members
            WHERE user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can insert themselves into workspaces" ON workspace_members;
CREATE POLICY "Users can insert themselves into workspaces" ON workspace_members
    FOR INSERT
    WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS "Workspace admins can update members" ON workspace_members;
CREATE POLICY "Workspace admins can update members" ON workspace_members
    FOR UPDATE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM public.workspace_members
            WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
        )
        OR user_id = auth.uid()
    );

DROP POLICY IF EXISTS "Workspace admins can remove members" ON workspace_members;
CREATE POLICY "Workspace admins can remove members" ON workspace_members
    FOR DELETE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM public.workspace_members
            WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
        )
        OR user_id = auth.uid()
    );

-- Fix subscription policies
DROP POLICY IF EXISTS "Users can view own subscription" ON subscriptions;
CREATE POLICY "Users can view own subscription" ON subscriptions
    FOR SELECT
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Admins can view all subscriptions" ON subscriptions;
CREATE POLICY "Admins can view all subscriptions" ON subscriptions
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = id 
            AND role IN ('admin', 'super_admin', 'billing_admin')
        )
    );

-- Fix payment transactions policies
DROP POLICY IF EXISTS "Users can view own transactions" ON payment_transactions;
CREATE POLICY "Users can view own transactions" ON payment_transactions
    FOR SELECT
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Admins can view all transactions" ON payment_transactions;
CREATE POLICY "Admins can view all transactions" ON payment_transactions
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = id 
            AND role IN ('admin', 'super_admin', 'billing_admin')
        )
    );

-- Fix audit logs policies
DROP POLICY IF EXISTS "Users can view own audit logs" ON audit_logs;
CREATE POLICY "Users can view own audit logs" ON audit_logs
    FOR SELECT
    USING (actor_id = auth.uid());

DROP POLICY IF EXISTS "Admins can view all audit logs" ON audit_logs;
CREATE POLICY "Admins can view all audit logs" ON audit_logs
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = id 
            AND role IN ('admin', 'super_admin', 'support')
        )
    );

-- Fix security events policies
DROP POLICY IF EXISTS "Users can view own security events" ON security_events;
CREATE POLICY "Users can view own security events" ON security_events
    FOR SELECT
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Admins can view all security events" ON security_events;
CREATE POLICY "Admins can view all security events" ON security_events
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = id 
            AND role IN ('admin', 'super_admin', 'support')
        )
    );

-- Fix admin actions policies
DROP POLICY IF EXISTS "Admins can log actions" ON admin_actions;
CREATE POLICY "Admins can log actions" ON admin_actions
    FOR INSERT
    WITH CHECK (admin_id = auth.uid());

-- Fix user sessions policies
DROP POLICY IF EXISTS "Users can view own sessions" ON user_sessions;
CREATE POLICY "Users can view own sessions" ON user_sessions
    FOR SELECT
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can delete own sessions" ON user_sessions;
CREATE POLICY "Users can delete own sessions" ON user_sessions
    FOR DELETE
    USING (user_id = auth.uid());

-- Fix data export requests policies
DROP POLICY IF EXISTS "Users can view own export requests" ON data_export_requests;
CREATE POLICY "Users can view own export requests" ON data_export_requests
    FOR SELECT
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can create export requests" ON data_export_requests;
CREATE POLICY "Users can create export requests" ON data_export_requests
    FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- Fix user_workspaces policies
DROP POLICY IF EXISTS "Users can view their workspaces" ON user_workspaces;
CREATE POLICY "Users can view their workspaces" ON user_workspaces
    FOR SELECT
    USING (
        user_workspaces.workspace_id = workspaces.id 
        AND user_workspaces.user_id = auth.uid()
    );

DROP POLICY IF EXISTS "Users can update their workspaces" ON user_workspaces;
CREATE POLICY "Users can update their workspaces" ON user_workspaces
    FOR UPDATE
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can delete their workspaces" ON user_workspaces;
CREATE POLICY "Users can delete their workspaces" ON user_workspaces
    FOR DELETE
    USING (user_id = auth.uid());

-- Fix ICP profiles policies
DROP POLICY IF EXISTS "Users can view their ICPs" ON icp_profiles;
CREATE POLICY "Users can view their ICPs" ON icp_profiles
    FOR SELECT
    USING (
        icp_profiles.workspace_id IN (
            SELECT workspace_id FROM public.workspace_members
            WHERE user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can create ICPs in their workspaces" ON icp_profiles;
CREATE POLICY "Users can create ICPs in their workspaces" ON icp_profiles
    FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM public.workspace_members
            WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
        )
    );

DROP POLICY IF EXISTS "Users can update their ICPs" ON icp_profiles;
CREATE POLICY "Users can update their ICPs" ON icp_profiles
    FOR UPDATE
    USING (
        icp_profiles.workspace_id IN (
            SELECT workspace_id FROM public.workspace_members
            WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
        )
        OR icp_profiles.created_by = auth.uid()
    );

DROP POLICY IF EXISTS "Users can delete their ICPs" ON icp_profiles;
CREATE POLICY "Users can delete their ICPs" ON icp_profiles
    FOR DELETE
    USING (
        icp_profiles.workspace_id IN (
            SELECT workspace_id FROM public.workspace_members
            WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
        )
        OR icp_profiles.created_by = auth.uid()
    );

-- Add comments for clarity
COMMENT ON POLICY "Users can view own profile" ON users IS 'Users can only view their own profile using auth.uid()';
COMMENT ON POLICY "Users can update own profile" ON users IS 'Users can only update their own profile using auth.uid()';
COMMENT ON POLICY "Users can view workspaces" ON workspaces IS 'Users can only view workspaces they are members of';
COMMENT ON POLICY "Users can create workspaces (they become owner)" ON workspaces IS 'Users can create workspaces and become the owner';
COMMENT ON POLICY "Users can view memberships for their workspaces" ON workspace_members IS 'Users can view workspace memberships for workspaces they belong to';
COMMENT ON POLICY "Users can insert themselves into workspaces" ON workspace_members IS 'Users can add themselves to workspaces';
COMMENT ON POLICY "Workspace admins can update members" ON workspace_members IS 'Workspace admins can update member roles and permissions';
COMMENT ON POLICY "Workspace admins can remove members" ON workspace_members IS 'Workspace admins can remove members from workspaces';
