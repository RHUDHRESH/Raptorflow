-- Database Health Check and Fix Script
-- Run this in Supabase SQL Editor to diagnose and fix issues

-- 1. Check PostgreSQL version and database status
SELECT 
    version() as postgres_version,
    current_database() as database_name,
    current_user as current_user,
    inet_server_addr() as server_ip;

-- 2. Check if key tables exist
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN (
        'profiles', 
        'workspaces', 
        'business_context_manifests',
        'foundations',
        'icp_profiles',
        'moves',
        'campaigns'
    )
ORDER BY tablename;

-- 3. Check migration status
SELECT 
    version,
    name,
    inserted_at
FROM supabase_migrations.schema_migrations 
ORDER BY inserted_at DESC;

-- 4. Check for any broken constraints or orphaned records
SELECT 
    tc.constraint_name,
    tc.table_name,
    tc.constraint_type
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'public'
    AND tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;

-- 5. Check RLS status on key tables
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN (
        'profiles', 
        'workspaces', 
        'business_context_manifests'
    );

-- 6. Check indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public'
    AND tablename IN (
        'profiles', 
        'workspaces', 
        'business_context_manifests'
    )
ORDER BY tablename, indexname;
