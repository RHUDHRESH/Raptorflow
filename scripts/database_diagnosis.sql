-- Complete Database Diagnosis
-- Run this first to understand current state

-- 1. Check what tables actually exist
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- 2. Check workspaces table structure
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'workspaces' 
    AND table_schema = 'public'
ORDER BY ordinal_position;

-- 3. Check for any existing BCM-related tables
SELECT 
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename LIKE '%manifest%' OR tablename LIKE '%bcm%'
ORDER BY tablename;

-- 4. Check migration status
SELECT 
    version,
    name
FROM supabase_migrations.schema_migrations 
ORDER BY version;

-- 5. Check for any orphaned constraints
SELECT 
    tc.constraint_name,
    tc.table_name,
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_schema = 'public'
    AND tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;
