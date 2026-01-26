-- =================================================================
-- SECURITY FIXES: Extension Schema Issues
-- Migration: 132_fix_extension_security.sql
-- Priority: MEDIUM - Moves vector extension to secure schema
-- =================================================================

-- Create extensions schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS extensions;

-- Move vector extension from public to extensions schema
-- First, check if vector extension exists in public
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'vector'
        AND extnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
    ) THEN
        -- Drop vector extension from public schema
        DROP EXTENSION IF EXISTS vector CASCADE;

        -- Recreate vector extension in extensions schema
        CREATE EXTENSION IF NOT EXISTS vector SCHEMA extensions;

        RAISE NOTICE 'Vector extension moved from public to extensions schema';
    ELSE
        -- Just create vector extension in extensions schema if it doesn't exist
        CREATE EXTENSION IF NOT EXISTS vector SCHEMA extensions;

        RAISE NOTICE 'Vector extension created in extensions schema';
    END IF;
END $$;

-- Update search_path to include extensions schema
-- This allows functions to find vector extension
ALTER DATABASE postgres SET search_path = "$user", public, extensions;

-- Grant usage on extensions schema
GRANT USAGE ON SCHEMA extensions TO authenticated;
GRANT USAGE ON SCHEMA extensions TO service_role;
GRANT USAGE ON SCHEMA extensions TO anon;
