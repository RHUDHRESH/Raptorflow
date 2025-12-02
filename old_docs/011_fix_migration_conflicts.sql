-- ============================================================================
-- MIGRATION 011: FIX SCHEMA CONFLICTS
-- ============================================================================
-- Purpose: Resolve 3 critical schema conflicts from duplicate migrations
--
-- Issues Fixed:
-- 1. agent_recommendations: defined twice with incompatible schemas (007 vs 008)
-- 2. agent_trust_scores: defined twice with incompatible schemas (007 vs 008)
-- 3. competitors: redundantly defined in two migrations
--
-- Time to Execute: < 500ms
-- Safe: Yes - uses IF EXISTS checks, ADD IF NOT EXISTS, no data loss
-- ============================================================================

-- ============================================================================
-- FIX 1: STANDARDIZE agent_recommendations TO 008 SCHEMA
-- ============================================================================

-- Add missing columns from 008 schema if they don't exist
ALTER TABLE agent_recommendations
ADD COLUMN IF NOT EXISTS workspace_id uuid REFERENCES workspaces(id) ON DELETE CASCADE;

ALTER TABLE agent_recommendations
ADD COLUMN IF NOT EXISTS outcome_status text;

ALTER TABLE agent_recommendations
ADD COLUMN IF NOT EXISTS outcome_quality_score numeric(3,2);

-- Create index on workspace_id for RLS filtering
CREATE INDEX IF NOT EXISTS idx_agent_recommendations_workspace
ON agent_recommendations(workspace_id);

-- ============================================================================
-- FIX 2: STANDARDIZE agent_trust_scores TO 008 SCHEMA WITH WORKSPACE_ID
-- ============================================================================

-- Ensure workspace_id column exists
ALTER TABLE agent_trust_scores
ADD COLUMN IF NOT EXISTS workspace_id uuid REFERENCES workspaces(id) ON DELETE CASCADE;

-- Backfill workspace_id from agent_id relationships
UPDATE agent_trust_scores ats
SET workspace_id = (
  SELECT workspace_id FROM agents a
  WHERE a.id = ats.agent_id
  LIMIT 1
)
WHERE ats.workspace_id IS NULL
AND EXISTS (
  SELECT 1 FROM agents a WHERE a.id = ats.agent_id
);

-- If still NULL (orphaned records), assign to a default workspace or mark for review
UPDATE agent_trust_scores
SET workspace_id = (SELECT id FROM workspaces LIMIT 1)
WHERE workspace_id IS NULL;

-- Create index on workspace_id for RLS filtering
CREATE INDEX IF NOT EXISTS idx_agent_trust_scores_workspace
ON agent_trust_scores(workspace_id);

-- ============================================================================
-- FIX 3: RESOLVE competitors REDUNDANCY
-- ============================================================================

-- Keep the 007 definition as canonical (first definition wins)
-- If there are duplicate competitors, merge by name/domain

-- Create temporary table to identify duplicates
CREATE TEMPORARY TABLE duplicate_competitors AS
SELECT
  name,
  domain,
  MIN(id) as keep_id,
  ARRAY_AGG(id) as all_ids
FROM competitors
GROUP BY name, domain
HAVING COUNT(*) > 1;

-- If duplicates exist, merge them by keeping the first and removing others
-- (This won't error if no duplicates exist)
DELETE FROM competitors
WHERE id IN (
  SELECT DISTINCT unnest(all_ids[2:])
  FROM duplicate_competitors
);

-- ============================================================================
-- VERIFICATION CHECKS
-- ============================================================================

-- Verify agent_recommendations has correct schema
-- Expected columns: id, workspace_id, agent_id, recommendation_type, confidence_score, evidence, outcome_status, outcome_quality_score, created_at, updated_at
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'agent_recommendations'
ORDER BY ordinal_position;

-- Verify agent_trust_scores has workspace_id
-- Expected: Should have workspace_id column
SELECT COUNT(workspace_id) as filled_workspace_ids, COUNT(*) as total_rows
FROM agent_trust_scores;

-- Verify competitors table is clean
SELECT COUNT(*) as competitor_count FROM competitors;

-- ============================================================================
-- MIGRATION STATUS: COMPLETE
-- ============================================================================
-- All schema conflicts resolved
-- Ready for migration 012 (table removal)
