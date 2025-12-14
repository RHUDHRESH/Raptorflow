-- =====================================================
-- MIGRATION 001: Extensions & Domains
-- =====================================================

-- Extensions are managed via Supabase Dashboard to avoid permission issues
-- Expected: uuid-ossp, pgcrypto, pg_trgm

-- Custom domains
CREATE DOMAIN amount_paise AS BIGINT CHECK (VALUE >= 0);

CREATE DOMAIN percentage AS DECIMAL(5,2) CHECK (VALUE >= 0 AND VALUE <= 100);
