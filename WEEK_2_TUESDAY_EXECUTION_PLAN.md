# Week 2 Tuesday - Staging Validation Plan

**Scheduled Date**: 2024-02-06 (Tuesday)
**Phase**: Week 2 - Codex Schema Creation
**Planned Hours**: 5 hours
**Status**: 📋 PLAN READY

---

## 🎯 OBJECTIVE

Validate all 5 migrations (013-017) on staging database. Confirm 16 new tables create correctly, all constraints and triggers work, and schema expands from 43 to 59 tables successfully.

---

## 📋 PRE-EXECUTION CHECKLIST

Safety Verifications:
- [x] All migrations reviewed and idempotent
- [x] Verification queries prepared (16 checks)
- [x] Staging database available
- [x] Backup procedure in place
- [x] Rollback strategy documented
- [x] Team notification plan

Expected Initial State:
- Tables: 43 (from Week 1)
- Foreign keys: 42
- RLS policies: 18
- Database size: ~244 MB

---

## ⏰ EXECUTION TIMELINE

### 09:00 - Preparation (30 min)

```
09:00 - Pre-execution verification
  ├─ Connect to staging database
  ├─ Verify current state (43 tables)
  ├─ Confirm backups in place
  ├─ Review all 5 migration files
  ├─ Load verification query file
  └─ Team notification: migration starting

09:15 - Final safety checks
  ├─ Active connections: Confirm low traffic
  ├─ Replication lag: Verify 0 seconds
  ├─ Database size: Record baseline
  └─ All systems: Ready for execution
```

### 09:30 - Migration Execution Phase (1 hour)

```
09:30 - Execute Migration 013
  ├─ Apply: 013_create_positioning_campaigns.sql
  ├─ Expected execution: 400-500ms
  ├─ Creates: 5 tables (positioning, message_architecture, campaigns, campaign_quests, campaign_cohorts)
  ├─ Adds: 12 indexes, 5 RLS policies, 2 triggers
  └─ Status: Monitor for errors

09:35 - Execute Migration 014
  ├─ Apply: 014_create_gamification_achievements.sql
  ├─ Expected execution: 350-400ms
  ├─ Creates: 3 tables (achievements, user_achievements, user_stats)
  ├─ Adds: 10 indexes, 5 RLS policies, 3 functions
  └─ Status: Monitor for errors

09:40 - Execute Migration 015
  ├─ Apply: 015_create_agent_registry.sql
  ├─ Expected execution: 400-450ms
  ├─ Creates: 4 tables (agent_registry, agent_capabilities, agent_assignments, agent_performance)
  ├─ Adds: 15 indexes, 4 RLS policies, 1 function
  └─ Status: Monitor for errors

09:45 - Execute Migration 016
  ├─ Apply: 016_create_intelligence_system.sql
  ├─ Expected execution: 300-350ms
  ├─ Creates: 2 tables (intelligence_signals, market_insights)
  ├─ Adds: 10 indexes, 2 RLS policies, 3 functions
  └─ Status: Monitor for errors

09:50 - Execute Migration 017
  ├─ Apply: 017_create_alerts_notifications.sql
  ├─ Expected execution: 350-400ms
  ├─ Creates: 2 tables (system_alerts, user_notifications)
  ├─ Adds: 12 indexes, 4 RLS policies, 4 functions
  └─ Status: Monitor for errors

10:00 - All migrations complete
  ├─ Total execution time: ~2000ms (2 seconds actual migration time)
  ├─ Expected errors: 0
  ├─ Expected warnings: 0
  └─ Proceed to verification
```

### 10:00 - Verification Phase (1.5 hours)

```
10:00 - Run WEEK_2_VERIFICATION_QUERIES.sql
  ├─ Execute all 16 verification checks
  ├─ Expected duration: 5-10 seconds
  ├─ Expected results: 16/16 PASS
  └─ Document all results

10:10 - Individual Migration Verification
  ├─ Verify Migration 013:
  │  ├─ Query: SELECT COUNT(*) FROM information_schema.tables
  │  │         WHERE table_name IN (5 positioning tables);
  │  └─ Expected: 5 tables created
  │
  ├─ Verify Migration 014:
  │  ├─ Query: SELECT COUNT(*) FROM information_schema.tables
  │  │         WHERE table_name IN (3 gamification tables);
  │  └─ Expected: 3 tables created
  │
  ├─ Verify Migration 015:
  │  ├─ Query: SELECT COUNT(*) FROM information_schema.tables
  │  │         WHERE table_name IN (4 agent registry tables);
  │  └─ Expected: 4 tables created
  │
  ├─ Verify Migration 016:
  │  ├─ Query: SELECT COUNT(*) FROM information_schema.tables
  │  │         WHERE table_name IN (2 intelligence tables);
  │  └─ Expected: 2 tables created
  │
  └─ Verify Migration 017:
     ├─ Query: SELECT COUNT(*) FROM information_schema.tables
     │         WHERE table_name IN (2 alert/notification tables);
     └─ Expected: 2 tables created

10:20 - Schema Integrity Checks
  ├─ Total table count:
  │  └─ SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'
  │     Expected: 59 tables (43 + 16)
  │
  ├─ Foreign key count:
  │  └─ SELECT COUNT(*) FROM information_schema.table_constraints WHERE constraint_type='FK'
  │     Expected: 82+ total (42 from Week 1 + 40+ from Week 2)
  │
  ├─ RLS policy count:
  │  └─ SELECT COUNT(*) FROM pg_policies
  │     Expected: 33+ total (18 from Week 1 + 15 from Week 2)
  │
  └─ Index count:
     └─ SELECT COUNT(*) FROM pg_indexes WHERE schemaname='public'
        Expected: 130+ total (70+ from existing + 60+ from Week 2)

10:35 - Function Verification
  ├─ Check: calculate_move_success_rate (from Migration 014)
  ├─ Check: update_experience_level (from Migration 014)
  ├─ Check: unlock_achievement (from Migration 014)
  ├─ Check: record_agent_execution (from Migration 015)
  ├─ Check: create_insight_from_signals (from Migration 016)
  ├─ Check: get_active_insights (from Migration 016)
  ├─ Check: get_priority_signals (from Migration 016)
  ├─ Check: create_system_alert (from Migration 017)
  ├─ Check: send_user_notification (from Migration 017)
  ├─ Check: acknowledge_alert (from Migration 017)
  ├─ Check: mark_notification_as_read (from Migration 017)
  └─ Check: get_user_unread_notifications (from Migration 017)
     Expected: All 12+ functions created and callable

10:50 - Data Integrity Verification
  ├─ Check: No orphaned records from existing tables
  ├─ Check: All foreign key relationships valid
  ├─ Check: No constraint violations
  ├─ Check: RLS policies properly enforced
  └─ Expected: 100% integrity maintained

11:00 - Sample Data Testing (Optional)
  ├─ Insert test record into campaigns table
  ├─ Insert test record into achievements table
  ├─ Insert test record into agent_registry table
  ├─ Verify RLS isolation on workspace_id
  ├─ Verify constraints enforced correctly
  └─ Verify triggers fire on insert/update
```

### 11:00 - Post-Validation (30 min)

```
11:00 - Performance Analysis
  ├─ Verify index usage on new tables
  ├─ Check query execution plans
  ├─ Confirm no slow queries (>1s)
  └─ Database performance: Normal

11:15 - Final Checklist
  ├─ All 16 verification queries: PASS
  ├─ Table count: 59 confirmed
  ├─ Foreign keys: All intact
  ├─ RLS policies: All active
  ├─ Functions: All created
  ├─ Triggers: All active
  ├─ No errors in logs
  └─ Ready for production migration

11:30 - Documentation
  ├─ Record all execution times
  ├─ Document verification results
  ├─ Note any deviations (expected: none)
  ├─ Prepare Wednesday production plan
  └─ Generate Tuesday execution report
```

---

## ✅ SUCCESS CRITERIA

All of the following MUST be true for Tuesday validation to PASS:

```
EXECUTION CRITERIA:
✅ All 5 migrations execute without errors
✅ No schema conflicts or constraint violations
✅ Execution time < 5 seconds total
✅ No data loss (no existing records affected)

VERIFICATION CRITERIA:
✅ 16/16 verification queries PASS
✅ 59 total tables (43 + 16 new)
✅ 82+ total foreign keys
✅ 33+ total RLS policies
✅ 130+ total indexes
✅ 12+ new functions created
✅ All triggers firing correctly

INTEGRITY CRITERIA:
✅ No orphaned records
✅ All relationships valid
✅ All constraints enforced
✅ RLS policies working
✅ Zero data loss confirmed

PERFORMANCE CRITERIA:
✅ No slow queries (>1s)
✅ Index usage optimal
✅ Database performance normal
✅ Replication lag: 0 seconds
```

---

## 📊 EXPECTED RESULTS

### Query Set 1: Migration 013 - Positioning & Campaigns

```sql
-- 4 PASS checks expected:

✅ positioning table exists
✅ message_architecture table exists
✅ campaigns table exists
✅ campaign_quests & campaign_cohorts tables exist

Result: 4/4 PASS
```

### Query Set 2: Migration 014 - Gamification & Achievements

```sql
-- 4 PASS checks expected:

✅ achievements table exists
✅ user_achievements table exists
✅ user_stats table exists
✅ unlock_achievement function exists

Result: 4/4 PASS
```

### Query Set 3: Migration 015 - Agent Registry

```sql
-- 4 PASS checks expected:

✅ agent_registry table exists
✅ agent_capabilities table exists
✅ agent_assignments table exists
✅ agent_performance table exists

Result: 4/4 PASS
```

### Query Set 4: Migration 016 - Intelligence System

```sql
-- 2 PASS checks expected:

✅ intelligence_signals table exists
✅ market_insights table exists

Result: 2/2 PASS
```

### Query Set 5: Migration 017 - Alerts & Notifications

```sql
-- 2 PASS checks expected:

✅ system_alerts table exists
✅ user_notifications table exists

Result: 2/2 PASS
```

### Schema Summary Checks

```sql
-- Expected results:

✅ TABLE COUNT: 59 (43 + 16 new)
✅ WEEK 2 TABLES: 16 new tables
✅ RLS POLICIES: 33+ total (18 + 15 new)
✅ INDEXES: 130+ total (70+ existing + 60+ new)
✅ FOREIGN KEYS: 82+ total (42 + 40+ new)
```

### Overall Verification Result

```
WEEK_2_MIGRATION_STATUS: ✅ PASS - All 16/16 checks successful
SCHEMA_EXPANSION: ✅ COMPLETE - 43 → 59 tables
READINESS_FOR_PRODUCTION: ✅ YES - All criteria met
```

---

## ⚠️ ROLLBACK PROCEDURE

If validation FAILS, execute:

### Option 1: Restore from Staging Backup (Recommended)

```sql
-- Restore to pre-migration state
-- If using Supabase: Use backup restore feature
-- Time to restore: 5-10 minutes
```

### Option 2: Manual Rollback (If Needed)

```sql
-- Drop all newly created tables in reverse order
DROP TABLE IF EXISTS user_notifications CASCADE;
DROP TABLE IF EXISTS system_alerts CASCADE;
DROP TABLE IF EXISTS market_insights CASCADE;
DROP TABLE IF EXISTS intelligence_signals CASCADE;
DROP TABLE IF EXISTS agent_performance CASCADE;
DROP TABLE IF EXISTS agent_assignments CASCADE;
DROP TABLE IF EXISTS agent_capabilities CASCADE;
DROP TABLE IF EXISTS agent_registry CASCADE;
DROP TABLE IF EXISTS user_stats CASCADE;
DROP TABLE IF EXISTS user_achievements CASCADE;
DROP TABLE IF EXISTS achievements CASCADE;
DROP TABLE IF EXISTS campaign_cohorts CASCADE;
DROP TABLE IF EXISTS campaign_quests CASCADE;
DROP TABLE IF EXISTS campaigns CASCADE;
DROP TABLE IF EXISTS message_architecture CASCADE;
DROP TABLE IF EXISTS positioning CASCADE;

-- Verify rollback
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
-- Expected: 43 (back to post-Week-1 state)
```

---

## 📝 DOCUMENTATION TO GENERATE

After successful validation:

1. **WEEK_2_TUESDAY_EXECUTION_LOG.md**
   - Actual execution times for each migration
   - Verification query results
   - Any deviations from expected
   - Performance metrics
   - Team sign-off

2. **Migration Execution Summary**
   - Migration 013: ✅ PASS (expected 400-500ms)
   - Migration 014: ✅ PASS (expected 350-400ms)
   - Migration 015: ✅ PASS (expected 400-450ms)
   - Migration 016: ✅ PASS (expected 300-350ms)
   - Migration 017: ✅ PASS (expected 350-400ms)
   - Total: ~2 seconds actual execution

3. **Verification Results**
   - All 16 checks: PASS
   - Table count: 59 confirmed
   - Performance: Normal

---

## 🎯 GO/NO-GO DECISION POINT

Before Wednesday production migration, confirm:

```
❓ All 16 verification queries passed? ✅ YES
❓ Table count is 59? ✅ YES
❓ All foreign keys intact? ✅ YES
❓ All RLS policies active? ✅ YES
❓ All functions created? ✅ YES
❓ No schema errors? ✅ YES

DECISION: 🟢 GO FOR PRODUCTION MIGRATION (Wednesday)
```

---

## 📌 TEAM RESPONSIBILITIES

### Before Execution (09:00 - 09:30)
- **Database Admin**: Staging environment verification
- **Backend Lead**: Application staging readiness
- **DevOps**: Backup and monitoring setup

### During Execution (09:30 - 10:00)
- **Database Admin**: Execute migrations, monitor progress
- **DevOps**: Monitor database metrics
- **Backend Lead**: Monitor for any application issues

### During Verification (10:00 - 11:30)
- **All**: Run verification queries
- **Database Admin**: Validate schema integrity
- **Backend Lead**: Check function execution
- **DevOps**: Performance monitoring

---

## ⏰ TIMELINE SUMMARY

```
Tuesday 2024-02-06

09:00 - 09:30: Preparation (30 min)
09:30 - 10:00: Migration Execution (30 min)
10:00 - 11:30: Verification (90 min)
11:30 - 12:00: Documentation (30 min)
────────────────────────────────────────
Total: 5 hours
Actual Migration Time: ~2 seconds
Verification Time: ~10 seconds
```

---

## 📌 NOTES FOR EXECUTION

1. **Communication**: Keep team updated on progress
2. **Monitoring**: Watch for warnings even if migrations succeed
3. **Verification**: Run ALL 16 checks - don't skip any
4. **Documentation**: Record all actual times and results
5. **Rollback Ready**: Know how to rollback immediately if needed
6. **Team Available**: Keep backup DBA available
7. **Success Confidence**: High - all migrations idempotent and tested

---

**Status**: 📋 PLAN COMPLETE - READY FOR TUESDAY EXECUTION
**Approval**: 🟢 READY TO PROCEED
**Confidence**: 🟢 HIGH - Migrations well-designed

**Next**: Execute Tuesday 2024-02-06

---

**Plan Created**: 2024-02-03
**Scheduled Execution**: 2024-02-06 Tuesday 09:00
**Expected Duration**: 5 hours
**Expected Result**: All 16 verification checks PASS, 59 tables confirmed
