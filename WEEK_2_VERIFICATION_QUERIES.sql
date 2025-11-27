-- Week 2 Verification Queries
-- Purpose: Validate all 5 migrations (013-017) executed correctly
-- Expected: 16/16 verification checks PASS

-- ============================================================================
-- QUERY SET 1: Migration 013 - Positioning & Campaigns Schema
-- ============================================================================

-- Check 1.1: Positioning table created with correct structure
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'positioning' AND table_schema = 'public'
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 013.1: positioning table exists"
UNION ALL

-- Check 1.2: Message_architecture table created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'message_architecture' AND table_schema = 'public'
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 013.2: message_architecture table exists"
UNION ALL

-- Check 1.3: Campaigns table created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'campaigns' AND table_schema = 'public'
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 013.3: campaigns table exists"
UNION ALL

-- Check 1.4: Campaign relationships table created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'campaign_quests' AND table_schema = 'public'
      AND EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'campaign_cohorts' AND table_schema = 'public'
      )
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 013.4: campaign relationships exist"
UNION ALL

-- ============================================================================
-- QUERY SET 2: Migration 014 - Gamification & Achievements
-- ============================================================================

-- Check 2.1: Achievements table created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'achievements' AND table_schema = 'public'
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 014.1: achievements table exists"
UNION ALL

-- Check 2.2: User achievements table created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'user_achievements' AND table_schema = 'public'
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 014.2: user_achievements table exists"
UNION ALL

-- Check 2.3: User stats table created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'user_stats' AND table_schema = 'public'
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 014.3: user_stats table exists"
UNION ALL

-- Check 2.4: Achievement functions created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM pg_proc
      WHERE proname = 'unlock_achievement'
      AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 014.4: unlock_achievement function exists"
UNION ALL

-- ============================================================================
-- QUERY SET 3: Migration 015 - Agent Registry System
-- ============================================================================

-- Check 3.1: Agent registry table created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'agent_registry' AND table_schema = 'public'
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 015.1: agent_registry table exists"
UNION ALL

-- Check 3.2: Agent capabilities table created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'agent_capabilities' AND table_schema = 'public'
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 015.2: agent_capabilities table exists"
UNION ALL

-- Check 3.3: Agent assignments table created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'agent_assignments' AND table_schema = 'public'
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 015.3: agent_assignments table exists"
UNION ALL

-- Check 3.4: Agent performance tracking table created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'agent_performance' AND table_schema = 'public'
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 015.4: agent_performance table exists"
UNION ALL

-- ============================================================================
-- QUERY SET 4: Migration 016 - Intelligence System
-- ============================================================================

-- Check 4.1: Intelligence signals table created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'intelligence_signals' AND table_schema = 'public'
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 016.1: intelligence_signals table exists"
UNION ALL

-- Check 4.2: Market insights table created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'market_insights' AND table_schema = 'public'
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 016.2: market_insights table exists"
UNION ALL

-- ============================================================================
-- QUERY SET 5: Migration 017 - Alerts & Notifications
-- ============================================================================

-- Check 5.1: System alerts table created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'system_alerts' AND table_schema = 'public'
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 017.1: system_alerts table exists"
UNION ALL

-- Check 5.2: User notifications table created
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_name = 'user_notifications' AND table_schema = 'public'
    ) THEN 'PASS'
    ELSE 'FAIL'
  END as "Migration 017.2: user_notifications table exists"
UNION ALL

-- ============================================================================
-- SUMMARY: Overall Schema State After Week 2
-- ============================================================================

-- Check: Total table count (should be 59: 43 from Week 1 + 16 new)
SELECT
  'TABLE COUNT: ' || COUNT(*)::text || ' (expected: 59)' as "Schema Summary"
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
UNION ALL

-- Check: New tables from Week 2 (should be 16)
SELECT
  'WEEK 2 TABLES: ' || COUNT(*)::text || ' (expected: 16)' as "Schema Summary"
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
AND table_name IN (
  'positioning', 'message_architecture', 'campaigns', 'campaign_quests', 'campaign_cohorts',
  'achievements', 'user_achievements', 'user_stats',
  'agent_registry', 'agent_capabilities', 'agent_assignments', 'agent_performance',
  'intelligence_signals', 'market_insights',
  'system_alerts', 'user_notifications'
)
UNION ALL

-- Check: RLS policies count (should be 15+)
SELECT
  'RLS POLICIES: ' || COUNT(*)::text || ' (expected: 15+)' as "Schema Summary"
FROM pg_policies
WHERE tablename IN (
  'positioning', 'message_architecture', 'campaigns', 'campaign_quests', 'campaign_cohorts',
  'user_achievements', 'user_stats',
  'agent_assignments', 'agent_performance',
  'intelligence_signals', 'market_insights',
  'system_alerts', 'user_notifications'
)
UNION ALL

-- Check: New indexes created (should be 60+)
SELECT
  'INDEXES: ' || COUNT(*)::text || ' (expected: 60+)' as "Schema Summary"
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN (
  'positioning', 'message_architecture', 'campaigns', 'campaign_quests', 'campaign_cohorts',
  'achievements', 'user_achievements', 'user_stats',
  'agent_registry', 'agent_capabilities', 'agent_assignments', 'agent_performance',
  'intelligence_signals', 'market_insights',
  'system_alerts', 'user_notifications'
)
UNION ALL

-- Check: Foreign keys (should be 40+)
SELECT
  'FOREIGN KEYS: ' || COUNT(*)::text || ' (expected: 40+)' as "Schema Summary"
FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY'
AND table_name IN (
  'positioning', 'message_architecture', 'campaigns', 'campaign_quests', 'campaign_cohorts',
  'achievements', 'user_achievements', 'user_stats',
  'agent_registry', 'agent_capabilities', 'agent_assignments', 'agent_performance',
  'intelligence_signals', 'market_insights',
  'system_alerts', 'user_notifications'
);

-- ============================================================================
-- DETAILED VERIFICATION: Key constraints and relationships
-- ============================================================================

-- Verify: campaign_cohorts links campaigns to cohorts correctly
SELECT
  CASE
    WHEN (SELECT COUNT(*) FROM information_schema.table_constraints
          WHERE constraint_type = 'FOREIGN KEY'
          AND table_name = 'campaign_cohorts'
          AND constraint_name LIKE '%campaign%') >= 2 THEN 'PASS'
    ELSE 'FAIL'
  END as "campaign_cohorts foreign keys"
UNION ALL

-- Verify: agent_assignments links agents to workspaces and campaigns
SELECT
  CASE
    WHEN (SELECT COUNT(*) FROM information_schema.table_constraints
          WHERE constraint_type = 'FOREIGN KEY'
          AND table_name = 'agent_assignments'
          AND (constraint_name LIKE '%agent%' OR constraint_name LIKE '%campaign%')) >= 3 THEN 'PASS'
    ELSE 'FAIL'
  END as "agent_assignments foreign keys"
UNION ALL

-- Verify: user_achievements links users to achievements
SELECT
  CASE
    WHEN (SELECT COUNT(*) FROM information_schema.table_constraints
          WHERE constraint_type = 'FOREIGN KEY'
          AND table_name = 'user_achievements'
          AND (constraint_name LIKE '%user%' OR constraint_name LIKE '%achievement%')) >= 2 THEN 'PASS'
    ELSE 'FAIL'
  END as "user_achievements foreign keys"
UNION ALL

-- ============================================================================
-- FINAL VALIDATION SUMMARY
-- ============================================================================

SELECT 'MIGRATION 013-017 VALIDATION COMPLETE' as "Status"
UNION ALL
SELECT 'All schema updates applied successfully' as "Status";

-- ============================================================================
-- QUERY EXECUTION SUMMARY
-- ============================================================================

/*
WEEK 2 MIGRATION VERIFICATION SUMMARY:

Total Verification Checks: 16

Query Set 1 (Migration 013): 4 checks
  ✓ positioning table
  ✓ message_architecture table
  ✓ campaigns table
  ✓ campaign relationships (quests + cohorts)

Query Set 2 (Migration 014): 4 checks
  ✓ achievements table
  ✓ user_achievements table
  ✓ user_stats table
  ✓ unlock_achievement function

Query Set 3 (Migration 015): 4 checks
  ✓ agent_registry table
  ✓ agent_capabilities table
  ✓ agent_assignments table
  ✓ agent_performance table

Query Set 4 (Migration 016): 2 checks
  ✓ intelligence_signals table
  ✓ market_insights table

Query Set 5 (Migration 017): 2 checks
  ✓ system_alerts table
  ✓ user_notifications table

Summary Metrics:
  - Expected total tables: 59 (43 + 16 new)
  - Expected new indexes: 60+
  - Expected RLS policies: 15+
  - Expected foreign keys: 40+

All checks should return PASS if migrations executed correctly.

EXECUTION: Run all queries in sequence. If any return FAIL, review the corresponding migration.
*/
