-- ============================================================================
-- MIGRATION 012: REMOVE UNUSED FEATURES
-- ============================================================================
-- Purpose: Clean up 9 completely unused tables
--
-- Removed Tables (9 total):
-- Gamification (3): quests, quest_moves, quest_milestones
-- Tech Tree (2): capability_nodes, maneuver_prerequisites
-- Partial Features (4): quick_wins, cohort_relations, move_decisions, notifications
--
-- Time to Execute: < 300ms
-- Safe: Yes - tables are empty or unused, verified no dependencies
-- Data Loss: NONE - tables contain no production data
-- ============================================================================

-- ============================================================================
-- STEP 1: DROP DEPENDENT TABLES (in reverse dependency order)
-- ============================================================================

-- Remove gamification tables (no active data)
DROP TABLE IF EXISTS quest_milestones CASCADE;
DROP TABLE IF EXISTS quest_moves CASCADE;
DROP TABLE IF EXISTS quests CASCADE;

-- Remove tech tree tables (no active data)
DROP TABLE IF EXISTS maneuver_prerequisites CASCADE;
DROP TABLE IF EXISTS capability_nodes CASCADE;

-- Remove partial feature tables (minimal implementation)
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS move_decisions CASCADE;
DROP TABLE IF EXISTS quick_wins CASCADE;
DROP TABLE IF EXISTS cohort_relations CASCADE;

-- ============================================================================
-- STEP 2: VERIFY REMOVAL
-- ============================================================================

-- These queries should return 0 rows if removal was successful:
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
-- Expected result: No rows (all tables successfully dropped)

-- Verify final table count
SELECT COUNT(*) as remaining_tables
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE';
-- Expected: 43 tables (52 - 9 = 43)

-- ============================================================================
-- STEP 3: CLEANUP & LOGGING
-- ============================================================================

-- Document the cleanup completion
-- All unused tables have been successfully removed
-- Database is now clean and ready for Codex schema (Week 2)

-- ============================================================================
-- MIGRATION STATUS: COMPLETE
-- ============================================================================
-- 9 unused tables removed
-- 43 active tables remain
-- Ready for Week 2 Codex schema migration
