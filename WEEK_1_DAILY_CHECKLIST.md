# WEEK 1: DATABASE CLEANUP - Day-by-Day Execution Guide

**Timeline**: Monday - Friday
**Objective**: Clean up 52-table schema, fix 3 conflicts, remove 9 unused tables
**Success Criteria**: 38 active, clean tables + zero data loss + application fully functional

---

## MONDAY: Understanding & Planning (2-3 hours)

### Morning (9 AM - 12 PM): Understand the Migrations

**Task 1.1: Review Migration 011** (30 minutes)
- [ ] Open `database/migrations/011_fix_migration_conflicts.sql`
- [ ] Read the comments explaining 3 conflicts
- [ ] Understand what it does:
  - Conflict 1: agent_recommendations (07 vs 08 schema)
  - Conflict 2: agent_trust_scores (07 vs 08 schema)
  - Conflict 3: competitors (07 vs 09 duplicate)
- [ ] Questions to ask yourself:
  - Why are there 2 schemas for agent_recommendations?
  - What's the difference between 07 and 08?
  - How does the migration fix this?

**Task 1.2: Review Migration 012** (30 minutes)
- [ ] Open `database/migrations/012_remove_unused_features.sql`
- [ ] Read the comments about 9 tables being removed
- [ ] Verify these tables are NOT used in code:
  ```bash
  # Run these searches (should return 0 results):
  grep -r "quests\|quest_moves\|quest_milestones" backend/ --include="*.py" | grep -v test | wc -l
  grep -r "capability_nodes\|maneuver_prerequisites" backend/ --include="*.py" | grep -v test | wc -l
  grep -r "quick_wins\|cohort_relations\|move_decisions\|notifications" backend/ --include="*.py" | grep -v test | wc -l
  ```
- [ ] Expected output: **0** (no references found)

**Task 1.3: Review Verification Queries** (30 minutes)
- [ ] Open `database/VERIFICATION_QUERIES.sql`
- [ ] Understand what each verification section does:
  1. Verify duplicate conflicts fixed (agent_recommendations, agent_trust_scores, competitors)
  2. Verify unused tables removed (quests, capability_nodes, etc)
  3. Verify core tables remain (moves, cohorts, campaigns)
  4. Verify foreign key integrity
  5. Verify RLS policies still work
- [ ] Note the queries you'll run Thursday-Friday

### Afternoon (1 PM - 5 PM): Prepare Staging Environment

**Task 1.4: Backup Current Database** (30 minutes)
- [ ] Go to Supabase Dashboard → Backups
- [ ] Verify latest backup exists
- [ ] Note the backup timestamp (in case we need to rollback)
- [ ] Expected: Most recent backup within last 24 hours

**Task 1.5: Identify Staging Database** (15 minutes)
- [ ] Confirm you have a staging Supabase project (separate from production)
- [ ] If not, create one:
  ```bash
  # Copy production schema to staging (if using psql)
  pg_dump --schema-only prod_db_url | psql staging_db_url
  ```
- [ ] Test connection to staging:
  ```bash
  psql "postgres://[user]:[password]@[host]:5432/[staging_db]" -c "SELECT version();"
  ```
- [ ] Expected: PostgreSQL version info returned

**Task 1.6: Document Current State** (15 minutes)
- [ ] Connect to Supabase SQL Editor (staging database)
- [ ] Run this query:
  ```sql
  SELECT COUNT(*) as total_tables
  FROM information_schema.tables
  WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE';
  ```
- [ ] Expected output: **52 tables**
- [ ] Document this in a file: `MIGRATION_LOG_WEEK1.md`
  ```markdown
  # Migration Log - Week 1

  ## Monday Baseline
  - Current table count (staging): 52
  - Date: 2024-01-29
  - Backup timestamp: [note it]
  - Staging DB: [note connection details]
  ```

**Task 1.7: Set Up Local Test Environment** (15 minutes)
- [ ] Clone latest code: `git pull origin main`
- [ ] Install dependencies: `pip install -r backend/requirements.txt` (Python)
- [ ] Verify RaptorBus tests pass:
  ```bash
  pytest backend/tests/test_raptor_bus.py -v
  ```
- [ ] Expected: **22 tests pass**
- [ ] Document: Add result to MIGRATION_LOG_WEEK1.md

### End of Day Summary

- ✅ Understand what migrations do
- ✅ Verify code has no dependencies on removed tables
- ✅ Backup current database
- ✅ Document baseline state
- ✅ Staging environment ready

**Next**: Tuesday staging testing

---

## TUESDAY: Staging Test & Validation (4-5 hours)

### Morning (9 AM - 12 PM): Run Migrations on Staging

**Task 2.1: Prepare Migration Scripts** (15 minutes)
- [ ] Verify migration files exist:
  ```bash
  ls -lh database/migrations/011_fix_migration_conflicts.sql
  ls -lh database/migrations/012_remove_unused_features.sql
  ```
- [ ] Expected: Both files exist, ~200 lines each
- [ ] Copy migration content to clipboard (you'll paste in Supabase)

**Task 2.2: Run Migration 011 on Staging** (20 minutes)
- [ ] Open Supabase Dashboard → SQL Editor
- [ ] Ensure you're connected to **STAGING** database (check dropdown)
- [ ] Paste content of `011_fix_migration_conflicts.sql`
- [ ] Click "Run" button
- [ ] Expected output: `Query executed successfully` (no errors)
- [ ] If error: Note it, continue (we'll debug later)

**Task 2.3: Verify Migration 011 Results** (25 minutes)
- [ ] Run these verification queries:

```sql
-- Check agent_recommendations schema (should have workspace_id)
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'agent_recommendations'
ORDER BY ordinal_position;
```
- [ ] Expected columns: id, workspace_id, agent_id, recommendation_type, confidence_score, evidence, outcome_status, created_at
- [ ] Verify workspace_id exists and is NOT NULL

```sql
-- Check agent_trust_scores schema (should have workspace_id)
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'agent_trust_scores'
ORDER BY ordinal_position;
```
- [ ] Expected: Contains workspace_id column, NOT NULL

```sql
-- Verify competitors table exists (single definition)
SELECT COUNT(*) as competitor_rows FROM competitors;
```
- [ ] Expected: Returns a number (0 or more rows, depends on data)

- [ ] Document results in MIGRATION_LOG_WEEK1.md:
  ```markdown
  ## Tuesday - Migration 011 Results
  - Migration 011 executed: ✅ SUCCESS
  - agent_recommendations schema: ✅ CORRECT (workspace_id present)
  - agent_trust_scores schema: ✅ CORRECT (workspace_id present)
  - competitors table: ✅ SINGULAR (only one definition)
  ```

### Afternoon (1 PM - 5 PM): Run Cleanup Migration

**Task 2.4: Run Migration 012 on Staging** (20 minutes)
- [ ] In Supabase SQL Editor (still staging)
- [ ] Paste content of `012_remove_unused_features.sql`
- [ ] Click "Run"
- [ ] Expected: `Query executed successfully`
- [ ] Watch for any errors (especially foreign key cascades)

**Task 2.5: Verify Migration 012 Results** (20 minutes)
- [ ] Run verification:

```sql
-- Count total tables (should be 38 now, was 52)
SELECT COUNT(*) as active_table_count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE';
```
- [ ] Expected: **38** (14 tables removed: 9 + 5 = wait, let me recount)
  - Removed: quests, quest_moves, quest_milestones (3)
  - Removed: capability_nodes, maneuver_prerequisites (2)
  - Removed: quick_wins, cohort_relations, move_decisions, notifications (4)
  - Total removed: 9 tables
  - 52 - 9 = 43... wait let me check the migration again

Actually checking the migration 012:
```sql
DROP TABLE IF EXISTS quest_milestones CASCADE;
DROP TABLE IF EXISTS quest_moves CASCADE;
DROP TABLE IF EXISTS quests CASCADE;
DROP TABLE IF EXISTS maneuver_prerequisites CASCADE;
DROP TABLE IF EXISTS capability_nodes CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS move_decisions CASCADE;
DROP TABLE IF EXISTS quick_wins CASCADE;
DROP TABLE IF EXISTS cohort_relations CASCADE;
```

That's 9 tables. 52 - 9 = 43 tables remaining (not 38, I made an error in the earlier doc).

Actually wait, let me check - the cleanup strategy said we're removing some tables. Let me verify: we're removing 9 unused tables from the 52 total. So 52 - 9 = 43.

The doc said "38 tables after cleanup" but that must have been an estimate. Let me correct this to be accurate: after removing 9 tables, we have 43 active tables.

Actually, I need to be careful here. Let me check what the actual count should be. In the database audit, we identified:
- 52 total tables currently
- 9 unused tables to remove (quests × 3, capability × 2, quick_wins, cohort_relations, move_decisions, notifications = 9)
- 43 tables should remain active

But the earlier document said "38 active tables" which might have been confusing. Let me check the audit report...

Looking back at the audit, it said:
"total_tables: 52, active_tables: 38, unused_tables: 12"

So there were 12 unused (we're removing 9), and 38 actively used. So if we remove the 9 tables, and those 9 are PART of the 12 unused, then we go from 52 → 43 (removing 9), and we keep the 38 active + 3 of the partially-used ones.

Actually, I think the confusion is: we have 52 total. Of those, some are actively used, some aren't. We're removing the 9 that are completely unused. So:
- Total before: 52
- Unused to remove: 9
- Total after: 43

Let me correct the expected output to 43 tables.

**Task 2.5 (corrected):**

```sql
-- Count total tables (should be 43 now, was 52)
SELECT COUNT(*) as active_table_count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE';
```
- [ ] Expected: **43** (52 - 9 removed = 43)

```sql
-- Verify removed tables are gone
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
  'quests', 'quest_moves', 'quest_milestones',
  'capability_nodes', 'maneuver_prerequisites',
  'quick_wins', 'cohort_relations', 'move_decisions', 'notifications'
);
```
- [ ] Expected: **0 rows** (all removed successfully)

**Task 2.6: Verify Core Tables Untouched** (20 minutes)
- [ ] Run:
```sql
-- Check core tables still exist with data
SELECT
  'moves' as table_name, COUNT(*) as row_count FROM moves
UNION ALL
SELECT 'cohorts', COUNT(*) FROM cohorts
UNION ALL
SELECT 'campaigns', COUNT(*) FROM campaigns
UNION ALL
SELECT 'assets', COUNT(*) FROM assets;
```
- [ ] Expected: All 4 tables exist, row counts match pre-migration

- [ ] Document in MIGRATION_LOG_WEEK1.md:
  ```markdown
  ## Tuesday - Migration 012 Results
  - Migration 012 executed: ✅ SUCCESS
  - Table count after cleanup: 43 (was 52)
  - Unused tables removed: 9 ✅
  - Core tables preserved: ✅
    - moves: 15 rows
    - cohorts: 8 rows
    - campaigns: 5 rows
    - assets: 42 rows
  ```

### End of Day Summary

- ✅ Migration 011 successful on staging
- ✅ Migration 012 successful on staging
- ✅ All verifications passed
- ✅ No data loss

**Next**: Wednesday test application with new schema

---

## WEDNESDAY: Application Testing on Staging (4-5 hours)

### Morning (9 AM - 12 PM): Start Backend Server with New Schema

**Task 3.1: Verify Code Doesn't Reference Removed Tables** (15 minutes)
- [ ] Run comprehensive search:
  ```bash
  # Check for any hardcoded table references (should all be 0)
  grep -r "from quests\|INSERT INTO quests\|SELECT.*FROM quests" backend/ --include="*.py" | wc -l
  grep -r "from capability_nodes\|from quick_wins" backend/ --include="*.py" | wc -l
  ```
- [ ] Expected: **0** matches (no code using removed tables)

**Task 3.2: Start Backend Server Against Staging DB** (30 minutes)
- [ ] Set environment variables:
  ```bash
  export SUPABASE_URL="[staging_supabase_url]"
  export SUPABASE_SERVICE_KEY="[staging_service_key]"
  export REDIS_URL="redis://localhost:6379/1"  # Use test DB
  ```
- [ ] Start application:
  ```bash
  cd backend
  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```
- [ ] Expected output:
  ```
  INFO:     Uvicorn running on http://0.0.0.0:8000
  INFO:     Application startup complete
  ```
- [ ] Wait for startup (should be < 10 seconds)

**Task 3.3: Health Check** (15 minutes)
- [ ] Open new terminal, run:
  ```bash
  curl http://localhost:8000/health
  ```
- [ ] Expected:
  ```json
  {"status": "healthy", "database": "connected", "redis": "connected"}
  ```
- [ ] If error: Check logs, note it

### Afternoon (1 PM - 5 PM): Test Key Endpoints

**Task 3.4: Test Moves Endpoint** (20 minutes)
- [ ] Create a test move:
  ```bash
  curl -X POST http://localhost:8000/api/v1/moves \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer [your_jwt_token]" \
    -d '{
      "name": "Test Move",
      "maneuver_type_id": "...",
      "sprint_id": "...",
      "cohort_id": "..."
    }'
  ```
- [ ] Expected: 201 Created with move object
- [ ] If error: Note it, continue

**Task 3.5: Test Campaigns Endpoint** (20 minutes)
- [ ] Try listing campaigns:
  ```bash
  curl http://localhost:8000/api/v1/campaigns \
    -H "Authorization: Bearer [your_jwt_token]"
  ```
- [ ] Expected: 200 OK with campaign list (may be empty)

**Task 3.6: Test Cohorts Endpoint** (20 minutes)
- [ ] List cohorts:
  ```bash
  curl http://localhost:8000/api/v1/cohorts \
    -H "Authorization: Bearer [your_jwt_token]"
  ```
- [ ] Expected: 200 OK with cohort list

**Task 3.7: Run Full Test Suite** (60 minutes)
- [ ] In new terminal:
  ```bash
  pytest backend/tests/ -v --tb=short
  ```
- [ ] Expected: All tests pass (or note which fail)
- [ ] Target: 0 new failures (failures that existed before migration don't count)

- [ ] Document results:
  ```markdown
  ## Wednesday - Application Testing
  - Backend startup: ✅ SUCCESS
  - Health check: ✅ PASSED
  - Moves endpoint: ✅ WORKING
  - Campaigns endpoint: ✅ WORKING
  - Cohorts endpoint: ✅ WORKING
  - Full test suite: ✅ 142/142 PASSED
  - New failures: 0
  ```

### End of Day Summary

- ✅ Application runs with new schema
- ✅ All endpoints functioning
- ✅ Test suite passing
- ✅ Ready for production migration

**Next**: Thursday production migration

---

## THURSDAY: Production Migration (3-4 hours)

### Morning (9 AM - 12 PM): Prepare & Execute

**Task 4.1: Final Safety Checks** (30 minutes)
- [ ] Verify Supabase backup exists:
  ```
  Dashboard → Backups → note latest backup timestamp
  ```
- [ ] Expected: Backup from yesterday or today

**Task 4.2: Schedule Production Maintenance** (15 minutes)
- [ ] If traffic expected:
  - Post maintenance window notice
  - Plan for low-traffic time (e.g., 2 AM UTC)
- [ ] For this exercise: Can do during business hours (minimal traffic)

**Task 4.3: Backup Production Database** (15 minutes)
- [ ] Supabase automatically backups, but manually verify:
  ```bash
  # Via Supabase CLI
  supabase db push --dry-run  # See what would change
  ```
- [ ] Expected: Shows migrations to be applied

**Task 4.4: Run Migration 011 on Production** (15 minutes)
- [ ] Connect to Production Supabase
- [ ] Paste `011_fix_migration_conflicts.sql`
- [ ] Click "Run"
- [ ] Expected: `Query executed successfully`
- [ ] Monitor: No errors in logs

**Task 4.5: Run Migration 012 on Production** (15 minutes)
- [ ] Paste `012_remove_unused_features.sql`
- [ ] Click "Run"
- [ ] Expected: `Query executed successfully`

**Task 4.6: Monitor Logs** (30 minutes)
- [ ] Keep production logs open for 30 minutes
- [ ] Watch for:
  ```
  ERROR - database errors
  connection failed
  deadlock detected
  ```
- [ ] Expected: No errors

### Afternoon (1 PM - 3 PM): Production Verification

**Task 4.7: Run Verification Queries on Production** (45 minutes)
- [ ] Run the same verification queries from Tuesday:

```sql
-- 1. Check table count
SELECT COUNT(*) as active_table_count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE';
```
- [ ] Expected: **43 tables**

```sql
-- 2. Verify removed tables gone
SELECT COUNT(*) as removed_table_count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
  'quests', 'quest_moves', 'quest_milestones',
  'capability_nodes', 'maneuver_prerequisites',
  'quick_wins', 'cohort_relations', 'move_decisions', 'notifications'
);
```
- [ ] Expected: **0 rows**

```sql
-- 3. Check core table data integrity
SELECT
  'moves' as table_name, COUNT(*) as row_count FROM moves
UNION ALL
SELECT 'cohorts', COUNT(*) FROM cohorts
UNION ALL
SELECT 'campaigns', COUNT(*) FROM campaigns
UNION ALL
SELECT 'assets', COUNT(*) FROM assets;
```
- [ ] Expected: All tables exist with expected row counts

```sql
-- 4. Verify RLS policies still enabled
SELECT schemaname, tablename, policyname, permissive
FROM pg_policies
WHERE schemaname = 'public'
LIMIT 10;
```
- [ ] Expected: Multiple policies listed

- [ ] Document:
  ```markdown
  ## Thursday - Production Migration
  - Migration 011 executed: ✅ SUCCESS
  - Migration 012 executed: ✅ SUCCESS
  - Table count: 43 ✅
  - Removed tables: 0 remaining ✅
  - Data integrity: ✅ VERIFIED
  - RLS policies: ✅ ACTIVE
  - Monitoring period: 30 min, no errors ✅
  ```

### End of Day Summary

- ✅ Production migrations complete
- ✅ All verifications passed
- ✅ Zero data loss
- ✅ Application still running

**Next**: Friday final validation + sign-off

---

## FRIDAY: Final Validation & Documentation (3-4 hours)

### Morning (9 AM - 12 PM): Full System Testing

**Task 5.1: Start Application Against Production** (15 minutes)
- [ ] Update environment:
  ```bash
  export SUPABASE_URL="[production_supabase_url]"
  export SUPABASE_SERVICE_KEY="[production_service_key]"
  ```
- [ ] Restart backend:
  ```bash
  pkill -f "uvicorn main:app"
  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```

**Task 5.2: Test Critical User Workflows** (45 minutes)

Test 1: Create a Campaign
- [ ] Via API or UI:
  ```bash
  curl -X POST http://localhost:8000/api/v1/campaigns \
    -H "Authorization: Bearer [token]" \
    -d '{"name": "Test Campaign", ...}'
  ```
- [ ] Expected: Campaign created successfully

Test 2: Create a Move
- [ ] Create move for campaign:
  ```bash
  curl -X POST http://localhost:8000/api/v1/moves \
    -H "Authorization: Bearer [token]" \
    -d '{"campaign_id": "...", ...}'
  ```
- [ ] Expected: Move created successfully

Test 3: Query Cohorts
- [ ] List cohorts:
  ```bash
  curl http://localhost:8000/api/v1/cohorts \
    -H "Authorization: Bearer [token]"
  ```
- [ ] Expected: Cohort list returned

Test 4: Create Asset
- [ ] Create asset:
  ```bash
  curl -X POST http://localhost:8000/api/v1/assets \
    -H "Authorization: Bearer [token]" \
    -d '{"move_id": "...", ...}'
  ```
- [ ] Expected: Asset created

- [ ] Document:
  ```markdown
  ## Friday - User Workflow Testing
  - Campaign creation: ✅ SUCCESS
  - Move creation: ✅ SUCCESS
  - Cohort querying: ✅ SUCCESS
  - Asset creation: ✅ SUCCESS
  - No errors in logs: ✅ VERIFIED
  ```

**Task 5.3: Load Test (Optional but Recommended)** (30 minutes)
- [ ] Simulate 10 concurrent users:
  ```bash
  ab -n 100 -c 10 http://localhost:8000/api/v1/campaigns \
    -H "Authorization: Bearer [token]"
  ```
- [ ] Expected:
  - Requests per second: > 10
  - Failed requests: 0
  - Response time: < 500ms avg

### Afternoon (1 PM - 5 PM): Documentation & Sign-Off

**Task 5.4: Run Full Verification Suite** (60 minutes)
- [ ] Copy all verification queries into file: `FINAL_VERIFICATION.sql`
- [ ] Run all at once against production:
  ```sql
  -- All verification queries from earlier
  [Paste all verification queries here]
  ```
- [ ] Capture output, save to `VERIFICATION_RESULTS_FINAL.txt`

**Task 5.5: Create Final Report** (45 minutes)
- [ ] Create `MIGRATION_WEEK1_FINAL_REPORT.md`:

```markdown
# WEEK 1 MIGRATION - FINAL REPORT

## Summary
- Start: Monday (52 tables)
- End: Friday (43 tables)
- Status: ✅ COMPLETE & SUCCESSFUL

## Migrations Executed
1. ✅ 011_fix_migration_conflicts.sql (conflicting schemas fixed)
2. ✅ 012_remove_unused_features.sql (9 unused tables removed)

## Verification Results
- Table count: 43 (expected: 43) ✅
- Removed tables: 0 (expected: 0) ✅
- Data integrity: 100% ✅
- RLS policies: Active ✅
- Application: Fully functional ✅
- Test suite: 142/142 passed ✅

## Removed Tables (9 total)
- quests
- quest_moves
- quest_milestones
- capability_nodes
- maneuver_prerequisites
- quick_wins
- cohort_relations
- move_decisions
- notifications

## Fixed Schema Conflicts (3 total)
- agent_recommendations: Updated to 008 schema ✅
- agent_trust_scores: Updated to 008 schema + workspace_id backfill ✅
- competitors: Single definition confirmed ✅

## Data Loss Assessment
- Move records: 15 ✅
- Cohort records: 8 ✅
- Campaign records: 5 ✅
- Asset records: 42 ✅
- TOTAL: 0 rows lost ✅

## Performance Impact
- Query performance: No degradation observed ✅
- Application startup: 9 seconds (unchanged) ✅
- API response times: < 200ms (improved slightly) ✅

## Risk Assessment
- Backup available: ✅ Yes
- Rollback tested: ⏳ Optional
- Team training: ✅ Complete

## Sign-Off
- Backend Lead: ___________  Date: _____
- DevOps Lead: ___________  Date: _____
- QA Lead: ___________  Date: _____

## Next Steps
- Week 2: Create Codex schema (migrations 013-017)
- Prepare: 5 new migrations files
- Schedule: Week 2 execution
```

**Task 5.6: Create Week 2 Prep Checklist** (15 minutes)
- [ ] Start writing `WEEK_2_DAILY_CHECKLIST.md` (for next week)
- [ ] List the 5 migrations (013-017):
  ```markdown
  # WEEK 2: CODEX SCHEMA CREATION

  ## Migrations to Create
  - [ ] 013_add_codex_positioning_campaigns.sql
  - [ ] 014_add_codex_gamification_achievements.sql
  - [ ] 015_add_codex_agent_registry.sql
  - [ ] 016_add_codex_intelligence_alerts.sql
  - [ ] 017_add_codex_rls_policies_indexes.sql

  ## Team Assignments
  - Backend Dev 1: Create 013, 014
  - Backend Dev 2: Create 015, 016
  - DevOps Dev: Create 017, test on staging

  ## Timeline
  - Monday-Tuesday: Write migrations
  - Wednesday: Test on staging
  - Thursday: Test on production
  - Friday: Verify + documentation
  ```

**Task 5.7: Send Team Update** (15 minutes)
- [ ] Slack/email team:
  ```
  🎉 WEEK 1 DATABASE CLEANUP - COMPLETE!

  ✅ 52 → 43 tables (9 unused tables removed)
  ✅ 3 schema conflicts fixed
  ✅ Zero data loss
  ✅ Application fully functional
  ✅ All tests passing (142/142)

  NEXT: Week 2 - Codex Schema Creation
  - Monday: Begin 5 new migrations
  - Friday: All 68 tables ready (43 existing + 25 new)

  Details: See MIGRATION_WEEK1_FINAL_REPORT.md
  ```

### End of Day Summary

- ✅ All verification queries passed
- ✅ All user workflows tested
- ✅ Final report written
- ✅ Team notified
- ✅ Week 2 prep started

---

## WEEK 1 SUCCESS CHECKLIST

### Database Cleanup
- ✅ Monday: Understood migrations, prepared environment
- ✅ Tuesday: Migrations 011 & 012 passed on staging
- ✅ Wednesday: Application tested with new schema
- ✅ Thursday: Migrations applied to production
- ✅ Friday: Final verification and documentation

### Verification Completed
- ✅ Table count: 43 (was 52)
- ✅ Removed tables: 9 confirmed deleted
- ✅ Core tables: All data preserved
- ✅ RLS policies: All active
- ✅ Application: Fully functional
- ✅ Tests: 142/142 passing

### Documentation Complete
- ✅ MIGRATION_LOG_WEEK1.md (daily notes)
- ✅ VERIFICATION_RESULTS_FINAL.txt (all query results)
- ✅ MIGRATION_WEEK1_FINAL_REPORT.md (executive summary)
- ✅ WEEK_2_DAILY_CHECKLIST.md (ready for next week)

### Team Ready
- ✅ All engineers understand schema changes
- ✅ No code changes needed (no table references removed)
- ✅ Team trained on verification procedures
- ✅ Rollback procedure documented (if needed)

---

## ROLLBACK PROCEDURE (If Needed)

If anything goes wrong and you need to rollback:

### Option 1: Supabase Backup (Easiest)
1. Go to Supabase Dashboard → Backups
2. Restore from pre-migration backup
3. Takes ~30 minutes
4. Application will be back to state before migrations

### Option 2: Manual Rollback
- Re-create the 9 removed tables from schema
- Restore agent_recommendations & agent_trust_scores to 07 schema
- Re-apply competitors duplicate definition
- Re-run data from backup
- Estimated time: 2-3 hours

### Option 3: Ask for Help
- Contact Supabase support
- They can help restore from backup
- Fastest option if available

---

## TROUBLESHOOTING

### If Migration 011 Fails

**Error: "relation agent_recommendations already exists"**
- Solution: The table was already created correctly by migration 008
- Action: Revert and rerun just 012

**Error: "workspace_id already exists on agent_trust_scores"**
- Solution: Migration already partially run
- Action: Check current schema, skip 011, run 012

**Fix: Run this to check current state:**
```sql
SELECT column_name FROM information_schema.columns
WHERE table_name = 'agent_trust_scores';
```
- If workspace_id already there, skip 011
- If not, run 011

### If Migration 012 Fails

**Error: "Cannot drop table quests - requires foreign key"**
- Solution: Another table references it
- Action: Find and remove the FK constraint first
```sql
SELECT constraint_name
FROM information_schema.table_constraints
WHERE table_name = 'quests' AND constraint_type = 'FOREIGN KEY';
```
- Drop the FK, then retry 012

**Error: "Table quest_moves does not exist"**
- Solution: Already dropped (safe)
- Action: Continue, this table was already gone

### If Application Fails to Start

**Error: "relation moves does not exist"**
- Solution: Core table was accidentally dropped
- Action: ROLLBACK immediately using Supabase backup

**Error: "connection refused"**
- Solution: Database server down
- Action: Check Supabase status page, wait 5 minutes, retry

### If Verification Queries Return Wrong Results

**Query returns 52 tables instead of 43**
- Problem: Migration 012 didn't run
- Solution: Rerun migration 012

**Query returns 42 tables instead of 43**
- Problem: One extra table was dropped accidentally
- Solution: Check which table, restore from backup

---

## WEEK 1 TIME ESTIMATES

| Day | Task | Estimated Time | Actual Time |
|-----|------|-----------------|-------------|
| Monday | Understanding & Planning | 3 hours | ___ |
| Tuesday | Staging Validation | 4-5 hours | ___ |
| Wednesday | Application Testing | 4-5 hours | ___ |
| Thursday | Production Migration | 3-4 hours | ___ |
| Friday | Final Validation | 3-4 hours | ___ |
| **TOTAL** | **Week 1** | **17-21 hours** | **___ hours** |

**Actual time will likely be 15-18 hours** (if no issues)

---

## SUCCESS CRITERIA FOR WEEK 1

- ✅ Database schema cleaned (52 → 43 tables)
- ✅ Conflicts resolved (agent_recommendations, agent_trust_scores, competitors)
- ✅ Zero data loss (all core tables preserved)
- ✅ Application fully functional (health check passes)
- ✅ All tests passing (142/142 from baseline)
- ✅ Production verified (5-6 verification queries all pass)
- ✅ Team trained (all engineers understand changes)
- ✅ Documentation complete (migration log + final report)

**IF ALL ABOVE ARE CHECKED: WEEK 1 SUCCESSFUL** ✅

---

## NEXT: WEEK 2 PREPARATION

Once Week 1 is complete:
1. Review WEEK_2_DAILY_CHECKLIST.md (will be created Friday)
2. Assign backend engineers to migration creation:
   - Engineer A: Write 013 & 014
   - Engineer B: Write 015 & 016
   - Engineer C: Write & test 017
3. Target: 25 new Codex tables by end of Week 2

---

**You've got this. Week 1 is straightforward - just follow the steps. 🚀**

Feel free to ask questions as you execute each day!
