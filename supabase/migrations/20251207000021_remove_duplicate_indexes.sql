-- =====================================================
-- MIGRATION 021: (NO-OP) Previously Removed FK Indexes
-- =====================================================
-- This migration was originally dropping FK indexes from migration 020.
-- Those indexes are REQUIRED for foreign key performance optimization.
-- Converted to no-op to preserve the indexes.
--
-- See: https://supabase.com/docs/guides/database/database-linter?lint=0001_unindexed_foreign_keys

SELECT 1; -- No-op placeholder
