-- VERIFICATION QUERIES FOR DATABASE CLEANUP
-- Run these queries after migrations 011 & 012 to verify cleanup was successful
--
-- Purpose: Validate that:
-- 1. Conflicts are fixed (agent_recommendations, agent_trust_scores have correct schemas)
-- 2. Unused tables are removed
-- 3. No data loss occurred
-- 4. Foreign keys remain intact
-- 5. RLS policies still apply

-- ============================================================================
-- 1. VERIFY DUPLICATE CONFLICTS ARE FIXED
-- ============================================================================

-- Check agent_recommendations schema (should match 008 schema)
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'agent_recommendations'
ORDER BY ordinal_position;
-- Expected columns: id, workspace_id, agent_id, recommendation_type, confidence_score, evidence, outcome_status, outcome_quality_score, created_at, updated_at

-- Check agent_trust_scores schema (should have workspace_id from 008)
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'agent_trust_scores'
ORDER BY ordinal_position;
-- Expected columns: id, workspace_id, agent_id, overall_trust_score, approval_rate, trust_trend, last_updated_at

-- Verify agent_trust_scores workspace_id is backfilled (no NULLs)
SELECT COUNT(*) as total_rows, COUNT(workspace_id) as filled_workspace_ids
FROM agent_trust_scores;
-- Expected: total_rows == filled_workspace_ids (100% backfilled)

-- Verify competitors table exists (should be singular from 007)
SELECT COUNT(*) as competitor_count
FROM competitors;
-- Expected: Returns row (table exists)

-- ============================================================================
-- 2. VERIFY UNUSED TABLES ARE REMOVED
-- ============================================================================

-- Check if removed tables exist (should return no rows)
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'quests',
    'quest_moves',
    'quest_milestones',
    'capability_nodes',
    'maneuver_prerequisites',
    'quick_wins',
    'cohort_relations',
    'move_decisions',
    'notifications'
);
-- Expected: No rows returned (all tables successfully dropped)

-- ============================================================================
-- 3. VERIFY CORE TABLES REMAIN INTACT
-- ============================================================================

-- List all remaining tables (should be 47 after cleanup)
SELECT COUNT(*) as active_table_count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE';
-- Expected: 47 tables

-- List all remaining table names for audit
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Verify core campaign tables exist and have data
SELECT
    'moves' as table_name, COUNT(*) as row_count FROM moves
UNION ALL
SELECT 'cohorts', COUNT(*) FROM cohorts
UNION ALL
SELECT 'campaigns', COUNT(*) FROM campaigns
UNION ALL
SELECT 'assets', COUNT(*) FROM assets
UNION ALL
SELECT 'positioning', COUNT(*) FROM positioning
UNION ALL
SELECT 'message_architecture', COUNT(*) FROM message_architecture;
-- Expected: All tables exist, row counts should match pre-cleanup values

-- ============================================================================
-- 4. VERIFY FOREIGN KEY INTEGRITY
-- ============================================================================

-- Check for orphaned records (shouldn't exist after cleanup)
-- This validates referential integrity

-- Example: Verify all campaign_cohorts reference existing campaigns and cohorts
SELECT COUNT(*) as orphaned_campaign_references
FROM campaign_cohorts cc
WHERE NOT EXISTS (SELECT 1 FROM campaigns c WHERE c.id = cc.campaign_id)
   OR NOT EXISTS (SELECT 1 FROM cohorts ch WHERE ch.id = cc.cohort_id);
-- Expected: 0 rows

-- Check for orphaned move references
SELECT COUNT(*) as orphaned_moves
FROM moves m
WHERE NOT EXISTS (SELECT 1 FROM maneuver_types mt WHERE mt.id = m.maneuver_type_id)
   OR NOT EXISTS (SELECT 1 FROM sprints s WHERE s.id = m.sprint_id)
   OR NOT EXISTS (SELECT 1 FROM lines_of_operation loo WHERE loo.id = m.line_of_operation_id);
-- Expected: 0 rows (or rows are expected if those tables were modified)

-- ============================================================================
-- 5. VERIFY RLS POLICIES STILL APPLY
-- ============================================================================

-- List all RLS policies (should still exist)
SELECT schemaname, tablename, policyname, permissive, qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
-- Expected: Multiple policies for workspace isolation

-- Verify workspace_id column exists on multi-tenant tables
SELECT table_name
FROM information_schema.columns
WHERE table_schema = 'public'
AND column_name = 'workspace_id'
ORDER BY table_name;
-- Expected: All active tables have workspace_id (or auth.users reference)

-- ============================================================================
-- 6. SUMMARY REPORT
-- ============================================================================

-- Generate cleanup summary
DO $$
DECLARE
    total_tables INTEGER;
    removed_tables INTEGER := 9;
    expected_tables INTEGER := 47;
BEGIN
    SELECT COUNT(*) INTO total_tables
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE';

    RAISE NOTICE 'DATABASE CLEANUP VERIFICATION';
    RAISE NOTICE '=====================================';
    RAISE NOTICE 'Current table count: %', total_tables;
    RAISE NOTICE 'Expected table count: %', expected_tables;
    RAISE NOTICE 'Removed tables: %', removed_tables;

    IF total_tables = expected_tables THEN
        RAISE NOTICE '✅ CLEANUP SUCCESSFUL';
    ELSE
        RAISE NOTICE '❌ CLEANUP INCOMPLETE or ERROR';
        RAISE NOTICE 'Expected %, got %', expected_tables, total_tables;
    END IF;

    RAISE NOTICE '=====================================';
END $$;

-- ============================================================================
-- 7. SCHEMA INFORMATION (FOR DOCUMENTATION)
-- ============================================================================

-- Export schema summary for documentation
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns
     WHERE table_name = t.table_name) as column_count,
    (SELECT COUNT(*) FROM information_schema.table_constraints
     WHERE table_name = t.table_name AND constraint_type = 'FOREIGN KEY') as foreign_key_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;
-- Shows: table structure overview for Codex integration planning
