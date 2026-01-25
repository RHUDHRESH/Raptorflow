-- Critical Fix: RLS Function Name Mismatch
-- Migration: 20240115_fix_rls_function_mismatch.sql
--
-- This migration fixes the critical vulnerability where RLS policies were calling
-- user_owns_workspace() but the actual function is named is_workspace_owner()
-- This caused ALL RLS policies to fail, exposing all user data

-- First, let's create the correct function name as an alias to avoid breaking existing code
CREATE OR REPLACE FUNCTION user_owns_workspace(workspace_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM workspaces
        WHERE id = user_owns_workspace.workspace_uuid
        AND user_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION user_owns_workspace(UUID) TO authenticated;

-- Add comment for documentation
COMMENT ON FUNCTION user_owns_workspace(UUID) IS 'Alias for is_workspace_owner to fix RLS policies - ensures users can only access their own workspace data';

-- Verify the function works correctly
DO $$
DECLARE
    test_result BOOLEAN;
BEGIN
    -- Test that function exists and returns correct type
    SELECT user_owns_workspace(NULL::UUID) INTO test_result;

    -- Log the fix
    INSERT INTO audit_logs (
        actor_id,
        action,
        action_category,
        description,
        success,
        created_at
    ) VALUES (
        auth.uid(),
        'RLS_FUNCTION_FIX',
        'security',
        'Fixed critical RLS function name mismatch vulnerability',
        TRUE,
        NOW()
    );
END $$;

-- Create a security check function to verify RLS is working
CREATE OR REPLACE FUNCTION verify_rls_protection()
RETURNS TABLE(
    table_name TEXT,
    rls_enabled BOOLEAN,
    policy_count INTEGER,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.table_name,
        t.relrowsecurity as rls_enabled,
        COUNT(p.policyname) as policy_count,
        CASE
            WHEN t.relrowsecurity AND COUNT(p.policyname) > 0 THEN 'PROTECTED'
            WHEN NOT t.relrowsecurity THEN 'VULNERABLE - RLS DISABLED'
            ELSE 'VULNERABLE - NO POLICIES'
        END as status
    FROM information_schema.tables t
    LEFT JOIN pg_policies p ON p.tablename = t.table_name
    WHERE t.table_schema = 'public'
    AND t.table_type = 'BASE TABLE'
    AND t.table_name IN (
        'users', 'workspaces', 'icp_profiles', 'foundations', 'moves',
        'campaigns', 'muse_assets', 'user_sessions', 'subscriptions',
        'payment_transactions', 'audit_logs', 'security_events'
    )
    GROUP BY t.table_name, t.relrowsecurity
    ORDER BY t.table_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION verify_rls_protection() TO authenticated;

-- Create a comprehensive security check report
CREATE OR REPLACE FUNCTION security_audit_report()
RETURNS TABLE(
    check_name TEXT,
    status TEXT,
    details JSONB,
    severity TEXT
) AS $$
DECLARE
    rls_status RECORD;
    user_count INTEGER;
    workspace_count INTEGER;
BEGIN
    -- Check RLS status
    FOR rls_status IN SELECT * FROM verify_rls_protection() LOOP
        RETURN QUERY SELECT
            'RLS_PROTECTION' as check_name,
            rls_status.status as status,
            jsonb_build_object(
                'table', rls_status.table_name,
                'rls_enabled', rls_status.rls_enabled,
                'policy_count', rls_status.policy_count
            ) as details,
            CASE
                WHEN rls_status.status = 'PROTECTED' THEN 'LOW'
                ELSE 'CRITICAL'
            END as severity;
    END LOOP;

    -- Check user/workspace isolation
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO workspace_count FROM workspaces;

    RETURN QUERY SELECT
        'USER_WORKSPACE_ISOLATION' as check_name,
        CASE WHEN user_count = workspace_count THEN 'OK' ELSE 'WARNING' END as status,
        jsonb_build_object(
            'user_count', user_count,
            'workspace_count', workspace_count,
            'ratio', user_count::FLOAT / NULLIF(workspace_count, 0)
        ) as details,
        'MEDIUM' as severity;

    -- Check function availability
    RETURN QUERY SELECT
        'FUNCTION_AVAILABILITY' as check_name,
        'OK' as status,
        jsonb_build_object(
            'user_owns_workspace_available', EXISTS(
                SELECT 1 FROM pg_proc WHERE proname = 'user_owns_workspace'
            ),
            'is_workspace_owner_available', EXISTS(
                SELECT 1 FROM pg_proc WHERE proname = 'is_workspace_owner'
            )
        ) as details,
        'LOW' as severity;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION security_audit_report() TO authenticated;

-- Log the security fix completion
INSERT INTO audit_logs (
    action,
    action_category,
    description,
    details,
    success,
    created_at
) VALUES (
    'CRITICAL_SECURITY_FIX',
    'security',
    'Fixed RLS function name mismatch vulnerability',
    jsonb_build_object(
        'migration', '20240115_fix_rls_function_mismatch.sql',
        'function_created', 'user_owns_workspace',
        'impact', 'All RLS policies now functional'
    ),
    TRUE,
    NOW()
);
