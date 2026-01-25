-- =================================================================
-- GET REMAINING SCHEMA INFO FOR COMPLETE AUDIT
-- =================================================================

-- Get all tables in public schema
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Get RLS status on all tables
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Get all existing RLS policies
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Get key columns for critical tables (sample)
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name IN ('plans', 'audit_logs', 'admin_actions', 'security_events', 'profiles', 'workspaces', 'users')
ORDER BY table_name, ordinal_position;
