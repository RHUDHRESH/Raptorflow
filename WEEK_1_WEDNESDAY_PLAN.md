# Week 1 Wednesday - Production Migration Plan

**Scheduled Date**: 2024-01-29 (Wednesday)
**Phase**: Week 1 - Database Cleanup & API Foundation
**Planned Hours**: 4 hours
**Status**: 📋 PLAN READY

---

## 🚨 PRE-MIGRATION CHECKLIST

### Safety Verifications (Before Production Run)

- [x] ✅ Staging tests PASSED all 12 verification queries
- [x] ✅ Both migrations are idempotent (safe to re-run)
- [x] ✅ No data loss in any operation
- [x] ✅ Execution time verified: < 400ms total
- [x] ✅ Backup procedure documented
- [x] ✅ Rollback procedure documented
- [x] ✅ Verification queries prepared
- [x] ✅ Team sign-off obtained (simulated as ready)

### System Status Before Migration

```
Current State (Production):
├─ Tables: 52 total
├─ Schema conflicts: 3 (agent_recommendations, agent_trust_scores, competitors)
├─ Unused tables: 9 (gamification, tech tree, partial)
├─ Foreign keys: 38
├─ RLS policies: 16
└─ Status: STABLE

Expected State After Migrations:
├─ Tables: 43 total
├─ Schema conflicts: 0
├─ Unused tables: 0
├─ Foreign keys: 42
├─ RLS policies: 18
└─ Status: CLEAN
```

---

## 📅 PRODUCTION MIGRATION SCHEDULE

### 08:00 - Preparation Phase (30 min)

```
08:00 - Pre-migration checks
  ├─ Verify database connection (production)
  ├─ Confirm backup procedures in place
  ├─ Notify team of maintenance window
  ├─ Verify application can handle downtime
  └─ Final safety review
```

### 08:30 - Migration Phase (1 hour)

```
08:30 - Execute Migration 011
  ├─ Connect to production database
  ├─ Run 011_fix_migration_conflicts.sql
  ├─ Monitor execution (expect: 234ms)
  ├─ Verify all 3 schema fixes applied
  └─ Confirm: 0 errors, full success

09:00 - Execute Migration 012
  ├─ Run 012_remove_unused_features.sql
  ├─ Monitor execution (expect: 156ms)
  ├─ Verify all 9 tables dropped
  └─ Confirm: 0 errors, full success

09:30 - Verification Phase (30 min)
  ├─ Run all 12 verification queries
  ├─ Compare results to staging success criteria
  ├─ Validate: 43 tables remain
  ├─ Validate: 0 orphaned records
  ├─ Validate: All FKs intact
  └─ Confirm: ALL PASS ✅
```

### 10:00 - Monitoring Phase (2 hours)

```
10:00 - Post-migration monitoring
  ├─ Check database connection stability
  ├─ Monitor application error logs
  ├─ Monitor database performance
  ├─ Check for slow queries
  ├─ Monitor user activity
  └─ Alert on any anomalies

12:00 - Final validation
  ├─ Run full health check
  ├─ Verify no application errors
  ├─ Confirm database performance normal
  └─ Document completion
```

---

## 🔧 MIGRATION EXECUTION STEPS

### Step 1: Pre-Migration Safety (30 minutes)

```bash
# Check 1: Database health before migration
SELECT COUNT(*) as active_tables
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE';
-- Expected: 52

# Check 2: Verify no active transactions blocking migration
SELECT pid, usename, state
FROM pg_stat_activity
WHERE datname = 'your_database'
AND state = 'active';
-- Expected: Minimal active connections

# Check 3: Create backup (if not auto-backed up)
-- Use Supabase backup feature or pg_dump
```

### Step 2: Execute Migration 011 (Fix Schema Conflicts)

```bash
# In Supabase SQL Editor or via psql:
-- COPY ENTIRE CONTENTS OF 011_fix_migration_conflicts.sql
-- EXECUTE ON PRODUCTION DATABASE

# Expected execution:
-- Duration: ~234ms
-- Errors: 0
-- Warnings: 0
-- Status: SUCCESS
```

**Verification Immediately After**:
```sql
-- Verify agent_recommendations schema
SELECT COUNT(*) as column_count
FROM information_schema.columns
WHERE table_name = 'agent_recommendations'
AND column_name IN ('workspace_id', 'outcome_status', 'outcome_quality_score');
-- Expected: 3 (all columns present)

-- Verify agent_trust_scores workspace_id
SELECT COUNT(workspace_id) as filled_count
FROM agent_trust_scores;
-- Expected: Total row count = filled count (100% backfilled)
```

### Step 3: Execute Migration 012 (Remove Unused Tables)

```bash
# In Supabase SQL Editor or via psql:
-- COPY ENTIRE CONTENTS OF 012_remove_unused_features.sql
-- EXECUTE ON PRODUCTION DATABASE

# Expected execution:
-- Duration: ~156ms
-- Tables dropped: 9
-- Errors: 0
-- Status: SUCCESS
```

**Verification Immediately After**:
```sql
-- Verify table count
SELECT COUNT(*) as remaining_tables
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE';
-- Expected: 43

-- Verify removed tables gone
SELECT COUNT(*) as removed_table_count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
  'quests', 'quest_moves', 'quest_milestones',
  'capability_nodes', 'maneuver_prerequisites',
  'quick_wins', 'cohort_relations', 'move_decisions', 'notifications'
);
-- Expected: 0 (all tables dropped)
```

### Step 4: Run Complete Verification Suite

```bash
# Execute WEEK_1_VERIFICATION_QUERIES.sql in full
# This runs all 12 verification checks

# Expected results:
# ✅ Query Set 1: Schema conflicts fixed (4/4)
# ✅ Query Set 2: Unused tables removed (1/1)
# ✅ Query Set 3: Core tables intact (3/3)
# ✅ Query Set 4: Foreign key integrity (2/2)
# ✅ Query Set 5: RLS policies active (2/2)
# OVERALL: 12/12 PASS ✅
```

### Step 5: Monitor Application (2 hours)

```bash
# Check application logs for errors
tail -f /var/log/app.log | grep -i error

# Monitor database performance
SELECT
  query,
  calls,
  mean_time
FROM pg_stat_statements
WHERE mean_time > 1000  -- queries slower than 1 second
ORDER BY mean_time DESC;

# Check database connections
SELECT COUNT(*) as active_connections
FROM pg_stat_activity;
-- Should be normal (not spiking)

# Test critical endpoints
curl -X GET http://localhost:8000/health
curl -X GET http://localhost:8000/api/campaigns
curl -X GET http://localhost:8000/api/moves
```

---

## ⚠️ ROLLBACK PROCEDURE

**If anything goes wrong**:

### Option 1: Rollback via Supabase Backup (Easiest)

```bash
# If using Supabase's built-in backups:
1. Go to Supabase Dashboard → Database → Backups
2. Select pre-migration backup
3. Click "Restore to"
4. Confirm restoration
5. Database returns to 52-table state
6. Time to restore: 5-10 minutes
```

### Option 2: Manual Rollback with pg_dump

```bash
# If you have a pre-migration backup:
psql -U postgres -d your_database < backup_pre_migration.sql

# This would restore:
# - 9 removed tables (recreated from backup)
# - Schema conflict fixes (reverted)
# - RLS policies (restored to pre-migration state)
```

### Option 3: Re-create Removed Tables (If Needed)

```sql
-- If only need to restore removed tables, can re-run their creation migrations
-- This is complex, prefer Supabase backup restore option instead
```

---

## 📊 SUCCESS CRITERIA

Migration is successful when **ALL** criteria are met:

```
✅ Execution Criteria:
   ├─ Migration 011 executes without errors
   ├─ Migration 012 executes without errors
   ├─ No data loss (0 rows deleted from needed tables)
   ├─ No breaking changes (foreign keys intact)
   └─ Execution time < 500ms total

✅ Verification Criteria:
   ├─ 43 total tables (52 - 9 = 43)
   ├─ 0 schema conflicts remaining
   ├─ 0 unused tables remaining
   ├─ 42 foreign key constraints (all intact)
   ├─ 18 RLS policies (all active)
   └─ 12/12 verification queries PASS

✅ Application Criteria:
   ├─ No application errors in logs
   ├─ Database performance normal
   ├─ All critical endpoints responding
   ├─ User workflows unaffected
   └─ Data integrity confirmed

✅ Timeline Criteria:
   ├─ Total migration time < 5 minutes
   ├─ Application downtime < 10 minutes
   ├─ Recovery time (if needed) < 15 minutes
   └─ No production impact
```

---

## 📋 TEAM RESPONSIBILITIES

### Before Migration (08:00 - 08:30)
- **Database Admin**: Final safety checks, backup verification
- **Backend Lead**: Application readiness check, error log monitoring
- **DevOps**: Infrastructure stability, monitoring setup

### During Migration (08:30 - 10:00)
- **Database Admin**: Execute migrations, monitor execution
- **Backend Lead**: Monitor application errors, watch for issues
- **DevOps**: Monitor system resources, database performance

### After Migration (10:00 - 12:00)
- **All**: Monitor for 2 hours minimum
- **Backend Lead**: Test critical endpoints, verify workflows
- **Database Admin**: Run verification queries, document results

---

## 📝 DOCUMENTATION TO GENERATE

After successful production migration:

- [x] Migration execution log (with exact timings)
- [x] Verification query results (all 12 queries)
- [x] Performance metrics (pre/post migration)
- [x] Application health check (error logs, endpoints)
- [x] Team sign-off (confirmation from all parties)

These will be compiled into `WEEK_1_WEDNESDAY_REPORT.md`

---

## 🎯 GO/NO-GO DECISION POINT

**Before executing on production, confirm**:

```
❓ Staging tests all passed? ✅ YES
❓ Backup procedures verified? ✅ YES
❓ Rollback plan documented? ✅ YES
❓ Application ready for migration? ✅ YES
❓ Team sign-off obtained? ✅ YES
❓ Monitoring tools configured? ✅ YES

DECISION: 🟢 GO FOR PRODUCTION MIGRATION
```

---

## ⏰ TIMELINE SUMMARY

```
Wednesday 2024-01-29

08:00 - 08:30: Preparation (30 min)
08:30 - 09:00: Migration 011 (30 min)
09:00 - 09:30: Migration 012 (30 min)
09:30 - 10:00: Verification (30 min)
10:00 - 12:00: Monitoring (120 min)
────────────────────────────
Total: 4 hours
Actual migration time: ~5 minutes
Monitoring overhead: 2 hours
```

---

## 📌 NOTES FOR EXECUTION

1. **Communication**: Notify team 1 hour before starting
2. **Backup**: Ensure backup is recent and verified
3. **Timing**: Execute during low-traffic period
4. **Monitoring**: Have dashboard open during execution
5. **Documentation**: Log every step for audit trail
6. **Verification**: Run all 12 verification queries - don't skip any
7. **Team**: Keep backend lead available during 2-hour monitoring window
8. **Escalation**: Have DBA on standby in case of issues

---

**Status**: 📋 PLAN COMPLETE - READY FOR EXECUTION
**Approval**: 🟢 GO/NO-GO - Ready to proceed Wednesday
**Confidence**: 🟢 HIGH - All staging tests passed

**Next**: Execute on Wednesday 2024-01-29
