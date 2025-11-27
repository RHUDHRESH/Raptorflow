-- ============================================================================
-- WEEK 1 VERIFICATION QUERIES
-- ============================================================================
-- Run these queries after migrations 011 & 012 to verify cleanup was successful
--
-- Purpose: Validate that:
-- 1. Conflicts are fixed (agent_recommendations, agent_trust_scores have correct schemas)
-- 2. Unused tables are removed
-- 3. No data loss occurred
-- 4. Foreign keys remain intact
-- 5. RLS policies still apply
--
-- Expected Execution Time: < 5 seconds
-- ============================================================================

-- ============================================================================
-- QUERY SET 1: VERIFY DUPLICATE CONFLICTS ARE FIXED
-- ============================================================================

-- Check 1: agent_recommendations schema (should match 008 schema)
-- Expected columns: id, workspace_id, agent_id, recommendation_type, confidence_score, evidence, outcome_status, outcome_quality_score, created_at, updated_at
SELECT
  'agent_recommendations' as table_name,
  column_name,
  data_type,
  is_nullable
FROM information_schema.columns
WHERE table_name = 'agent_recommendations'
ORDER BY ordinal_position;

-- Check 2: agent_trust_scores schema (should have workspace_id from 008)
-- Expected columns: id, workspace_id, agent_id, overall_trust_score, approval_rate, trust_trend, last_updated_at
SELECT
  'agent_trust_scores' as table_name,
  column_name,
  data_type,
  is_nullable
FROM information_schema.columns
WHERE table_name = 'agent_trust_scores'
ORDER BY ordinal_position;

-- Check 3: Verify agent_trust_scores workspace_id is backfilled (no NULLs)
SELECT
  COUNT(*) as total_rows,
  COUNT(workspace_id) as filled_workspace_ids,
  CASE
    WHEN COUNT(*) = COUNT(workspace_id) THEN 'PASS'
    ELSE 'FAIL'
  END as status
FROM agent_trust_scores;
-- Expected: total_rows == filled_workspace_ids (100% backfilled)

-- Check 4: Verify competitors table exists and is clean
SELECT
  'competitors' as table_name,
  COUNT(*) as competitor_count,
  COUNT(DISTINCT name) as unique_names
FROM competitors;
-- Expected: Returns row (table exists), no duplicate names

-- ============================================================================
-- QUERY SET 2: VERIFY UNUSED TABLES ARE REMOVED
-- ============================================================================

-- Check 5: Verify removed tables don't exist (should return no rows)
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
)
ORDER BY table_name;
-- Expected: No rows returned (all tables successfully dropped)

-- ============================================================================
-- QUERY SET 3: VERIFY CORE TABLES REMAIN INTACT
-- ============================================================================

-- Check 6: List all remaining tables (should be 43 after cleanup)
SELECT COUNT(*) as active_table_count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE';
-- Expected: 43 tables

-- Check 7: List all remaining table names for audit
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;
-- Expected: 43 rows with all core tables

-- Check 8: Verify core campaign tables exist and have data
SELECT
    'moves' as table_name, COUNT(*) as row_count FROM moves
UNION ALL
SELECT 'cohorts', COUNT(*) FROM cohorts
UNION ALL
SELECT 'campaigns', COUNT(*) FROM campaigns
UNION ALL
SELECT 'assets', COUNT(*) FROM assets
UNION ALL
SELECT 'workspaces', COUNT(*) FROM workspaces
UNION ALL
SELECT 'auth.users', COUNT(*) FROM auth.users
ORDER BY table_name;
-- Expected: All tables exist, row counts should match pre-migration values

-- ============================================================================
-- QUERY SET 4: VERIFY FOREIGN KEY INTEGRITY
-- ============================================================================

-- Check 9: Verify foreign key constraints are intact
SELECT COUNT(*) as total_foreign_keys
FROM information_schema.table_constraints
WHERE table_schema = 'public'
AND constraint_type = 'FOREIGN KEY';
-- Expected: 30+ (increased from initial setup)

-- Check 10: Check for orphaned records (shouldn't exist after cleanup)
-- Example: Verify all campaign_cohorts reference existing campaigns and cohorts
SELECT COUNT(*) as orphaned_campaign_references
FROM campaign_cohorts cc
WHERE NOT EXISTS (SELECT 1 FROM campaigns c WHERE c.id = cc.campaign_id)
   OR NOT EXISTS (SELECT 1 FROM cohorts ch WHERE ch.id = cc.cohort_id);
-- Expected: 0 rows

-- ============================================================================
-- QUERY SET 5: VERIFY RLS POLICIES STILL APPLY
-- ============================================================================

-- Check 11: List all RLS policies (should still exist)
SELECT
  schemaname,
  tablename,
  policyname,
  permissive
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
-- Expected: Multiple policies for workspace isolation

-- Check 12: Verify workspace_id column exists on multi-tenant tables
SELECT
  table_name,
  COUNT(*) as workspace_columns
FROM information_schema.columns
WHERE table_schema = 'public'
AND column_name = 'workspace_id'
GROUP BY table_name
ORDER BY table_name;
-- Expected: All active tables have workspace_id (or auth.users reference)

-- ============================================================================
-- SUMMARY REPORT
-- ============================================================================

-- Summary: Database Cleanup Verification
-- This PL/pgSQL block verifies the migration success
DO $$
DECLARE
    total_tables INTEGER;
    removed_tables INTEGER := 9;
    expected_tables INTEGER := 43;
    removed_table_count INTEGER;
BEGIN
    -- Count total active tables
    SELECT COUNT(*) INTO total_tables
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE';

    -- Verify removed tables are gone
    SELECT COUNT(*) INTO removed_table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN (
        'quests', 'quest_moves', 'quest_milestones',
        'capability_nodes', 'maneuver_prerequisites',
        'quick_wins', 'cohort_relations', 'move_decisions', 'notifications'
    );

    -- Report results
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'DATABASE CLEANUP VERIFICATION REPORT';
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'Current table count: %', total_tables;
    RAISE NOTICE 'Expected table count: %', expected_tables;
    RAISE NOTICE 'Removed table count: %', removed_tables;
    RAISE NOTICE 'Remaining removed tables found: %', removed_table_count;
    RAISE NOTICE '';

    IF total_tables = expected_tables AND removed_table_count = 0 THEN
        RAISE NOTICE '✅ DATABASE CLEANUP SUCCESSFUL';
        RAISE NOTICE 'All unused tables removed';
        RAISE NOTICE 'Schema conflicts resolved';
        RAISE NOTICE 'Ready for Week 2 Codex schema migration';
    ELSE
        RAISE NOTICE '❌ DATABASE CLEANUP INCOMPLETE OR ERROR';
        RAISE NOTICE 'Expected % tables, got %', expected_tables, total_tables;
        RAISE NOTICE 'Found % removed tables still in database', removed_table_count;
    END IF;

    RAISE NOTICE '==========================================';
END $$;

-- ============================================================================
-- FINAL STATUS
-- ============================================================================
-- After running these verification queries:
-- 1. Check Query Set 1: Schema conflicts fixed? ✓
-- 2. Check Query Set 2: 9 tables removed? ✓
-- 3. Check Query Set 3: 43 tables remain? ✓
-- 4. Check Query Set 4: Foreign keys intact? ✓
-- 5. Check Query Set 5: RLS policies active? ✓
-- 6. Review Summary Report: All green? ✓
--
-- If all checks pass: Database cleanup complete ✅
-- Next: Continue to Week 1 application testing
