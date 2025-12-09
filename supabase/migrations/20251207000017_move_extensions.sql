-- =====================================================
-- MIGRATION 017: Move Extensions to Extensions Schema
-- =====================================================

-- Create extensions schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS extensions;

-- Grant usage to relevant roles
GRANT USAGE ON SCHEMA extensions TO postgres, anon, authenticated, service_role;

-- Move extensions from public to extensions schema
-- Note: This recreates the extensions, which briefly locks dependent objects

-- pg_trgm (trigram text search)
DROP EXTENSION IF EXISTS pg_trgm CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA extensions;

-- btree_gist (GiST index support)
DROP EXTENSION IF EXISTS btree_gist CASCADE;
CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA extensions;

-- citext (case-insensitive text)
DROP EXTENSION IF EXISTS citext CASCADE;
CREATE EXTENSION IF NOT EXISTS citext WITH SCHEMA extensions;

-- PostgreSQL automatically updates all dependent objects (indexes, functions, etc.)
