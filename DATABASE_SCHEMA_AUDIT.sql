-- =================================================================
-- DATABASE SCHEMA AUDIT - Understand Current Structure
-- Run this first to see all tables and their columns
-- =================================================================

-- Get all tables in public schema
SELECT
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Get all columns for each table (run this after seeing table list)
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

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

-- Get all existing indexes
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Get all functions
SELECT
    proname,
    pronamespace::regschema as schema_name,
    prosrc as source_code,
    prolang::reglanguage as language
FROM pg_proc
WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
ORDER BY proname;

-- Check RLS status on all tables
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Check extensions
SELECT
    extname,
    extnamespace::regschema as schema_name,
    extversion
FROM pg_extension
ORDER BY extname;
