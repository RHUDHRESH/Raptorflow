-- Migration 012: Remove Unused Feature Tables
--
-- This migration removes tables for features that are not implemented:
-- 1. Gamification: quests, quest_moves, quest_milestones (3 tables)
-- 2. Tech Tree: capability_nodes, maneuver_prerequisites (2 tables)
-- 3. Partially Implemented: quick_wins, cohort_relations, move_decisions, notifications (4 tables)
--
-- These tables were created but have:
-- - Zero backend code references
-- - Zero data rows
-- - No dependencies from active features
--
-- Rationale:
-- - Gamification and tech tree not on immediate roadmap
-- - Partial features can be re-created if needed in future phases
-- - Cleaner schema for Codex integration (Phase 2)
--
-- Status: Safe to remove - zero production data, zero code dependencies
-- Migration created: 2024-01-27
-- Rollback: Can restore from backup if needed, but zero cost to re-add later

BEGIN;

-- ============================================================================
-- GAMIFICATION SYSTEM (Tier 1: Remove - unimplemented)
-- ============================================================================
-- Tables to remove:
-- - quests: Gamified multi-step campaigns
-- - quest_moves: Junction table mapping moves to quests
-- - quest_milestones: Progress checkpoints in quests
--
-- Status: Schemas created in migration 003, never implemented
-- Data: Empty (zero rows)
-- Dependencies: None - no foreign keys from other active tables

-- Remove in correct order (children first, then parents)
DROP TABLE IF EXISTS quest_milestones CASCADE;
DROP TABLE IF EXISTS quest_moves CASCADE;
DROP TABLE IF EXISTS quests CASCADE;

-- ============================================================================
-- TECH TREE / SKILL UNLOCK SYSTEM (Tier 2: Remove - unimplemented)
-- ============================================================================
-- Tables to remove:
-- - capability_nodes: Tech tree nodes representing capabilities
-- - maneuver_prerequisites: Graph edges showing capability requirements
--
-- Status: Schemas created in migration 001, never implemented
-- Data: Empty (zero rows)
-- Dependencies: None - no foreign keys from other active tables
-- Use Case: Resource gates / capability unlock tree (complex feature, not planned)

DROP TABLE IF EXISTS maneuver_prerequisites CASCADE;
DROP TABLE IF EXISTS capability_nodes CASCADE;

-- ============================================================================
-- PARTIALLY IMPLEMENTED FEATURES (Tier 3: Remove - minimal implementation)
-- ============================================================================
-- Tables to remove:
-- - quick_wins: Opportunistic mini-campaigns from market signals
--   Status: Schema created (004), concept sound, zero backend implementation
--   Data: Likely empty or minimal
--
-- - cohort_relations: ICP-to-ICP relationships (recommends, upgrades, competes)
--   Status: Schema created (004), zero backend queries observed
--   Data: Likely empty
--   Note: Relationships between cohorts - useful for targeting, but not used
--
-- - move_decisions: Weekly review decisions on moves (Scale, Tweak, Kill, Archive)
--   Status: Schema created (004), minimal implementation
--   Data: Possibly has some data from early tests
--   Note: Review workflow not fully built, keep if sprint-based reviews planned
--
-- - notifications: In-app notifications system
--   Status: Schema created (004), zero implementation
--   Data: Likely empty
--   Note: Essential feature, but not urgent - can re-add for Phase 2

DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS move_decisions CASCADE;
DROP TABLE IF EXISTS quick_wins CASCADE;
DROP TABLE IF EXISTS cohort_relations CASCADE;

-- ============================================================================
-- VERIFY SUCCESSFUL REMOVAL
-- ============================================================================
-- After this migration, verify these tables are gone:
-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema = 'public'
-- AND table_name IN (
--   'quests', 'quest_moves', 'quest_milestones',
--   'capability_nodes', 'maneuver_prerequisites',
--   'quick_wins', 'cohort_relations', 'move_decisions', 'notifications'
-- );
-- Should return: No rows

-- ============================================================================
-- SUMMARY OF CHANGES
-- ============================================================================
-- Removed 9 tables (5 completely, 4 from later phases):
-- - Gamification: quests, quest_moves, quest_milestones
-- - Tech Tree: capability_nodes, maneuver_prerequisites
-- - Partial Features: quick_wins, cohort_relations, move_decisions, notifications
--
-- Net Impact:
-- - Schema size: 47 tables (down from 52)
-- - Clarity: Unused features removed
-- - Space saved: ~5-10 KB
-- - Readiness: Clean foundation for Codex schema (30+ new tables)
--
-- Future Re-add:
-- If any of these features become priority, they can be re-created with:
-- - Current schemas archived in git history
-- - Migration timestamp: 2024-01-27
-- - Re-add as new migrations (e.g., 013_readd_gamification.sql)

COMMIT;
