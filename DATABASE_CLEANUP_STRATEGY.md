# RaptorFlow Database Cleanup & Migration Strategy
## Preparing for Codex Integration

**Status:** Phase 1 - Audit Complete, Cleanup Ready

**Key Finding:** Current schema has 52 tables, but **3 critical conflicts** and **5+ unused tables**

---

## Critical Issues (Fix Immediately)

### Issue 1: agent_recommendations (DUPLICATE WITH CONFLICTING SCHEMA)
- **Conflict**: Migration 007 creates minimal schema, Migration 008 creates extended schema
- **Problem**: Migrations will fail or corrupt data
- **Solution**:
  - DELETE definition from 007_agent_swarm_tables.sql
  - KEEP extended schema from 008_self_improving_loops.sql
  - Create repair migration (011) to normalize existing data

### Issue 2: agent_trust_scores (DUPLICATE WITH CONFLICTING SCHEMA)
- **Conflict**: Migration 007 has workspace-agnostic schema, Migration 008 has workspace-scoped
- **Problem**: Data isolation failure, cross-workspace trust contamination
- **Solution**:
  - DELETE definition from 007_agent_swarm_tables.sql
  - KEEP workspace-scoped schema from 008 (superior design)
  - Migration 011 backfills workspace_id for all existing records

### Issue 3: competitors (DUPLICATE DEFINITION)
- **Conflict**: Defined identically in 007_agent_swarm_tables.sql AND 009_strategic_system_foundation.sql
- **Problem**: Redundant table creation, confusion about canonical schema
- **Solution**:
  - Keep only 007 definition
  - DELETE redundant definition from 009

---

## Unused Tables to Remove

### Group 1: Gamification (3 tables - COMPLETE REMOVAL)
If gamification is NOT planned for Phase 1-3, remove entirely:
- **quests** - No backend implementation
- **quest_moves** - Depends on quests
- **quest_milestones** - Depends on quests

**Decision Required**: Is gamification planned? If yes, keep. If no, remove.

### Group 2: Tech Tree/Skills (2 tables - COMPLETE REMOVAL)
Resource gates feature not planned:
- **capability_nodes** - Tech tree nodes
- **maneuver_prerequisites** - Skill unlock edges

**Recommendation**: Remove - takes 2 KB schema space, zero usage

### Group 3: Partially Implemented (4 tables - DOCUMENT STATUS)
These have schemas but minimal backend code. For now, KEEP but document status:
- **quick_wins** - Opportunistic campaign templates
- **cohort_relations** - ICP-to-ICP relationships (recommends, upgrades, competes)
- **move_decisions** - Weekly move review decisions
- **notifications** - In-app notification system

**Action**: Document whether these are planned for future phases. If yes, prioritize implementation. If no, mark as deprecated.

### Group 4: Low Priority Implementation (3 tables - KEEP FOR NOW)
Structures exist, some agent references:
- **move_anomalies** - Anomaly detection (keep schema, implement detection)
- **move_logs** - Daily move tracking (keep schema, implement logger)
- **support_feedback** - Feedback aggregation (keep schema, implement ingestion)

**Action**: Schedule implementation or deprecate

---

## Schema Consolidation Strategy

### Active Core Tables (UNTOUCHED)
These are healthy and actively used. Do not modify:

```
Foundation:
- workspaces
- user_workspaces
- user_profiles
- auth.users (Supabase managed)

Campaign Engine:
- moves (central execution table)
- maneuver_types
- sprints
- lines_of_operation
- assets

Customer Intelligence:
- cohorts
- cohort_relations (keep, even if unused - good for future)

Strategic Framework:
- positioning
- message_architecture
- campaigns
- campaign_cohorts
- campaign_channels

Intelligence & Learning:
- trends
- trend_mentions
- experiments
- experiment_results
- experiment_metadata
- competitors
- competitor_content
- competitor_patterns
- agent_debates
- debate_rounds

Payments:
- subscriptions
- billing_history
- autopay_subscriptions
- autopay_payments

Onboarding & Profiles:
- onboarding_responses
- user_profiles

Agent System:
- agent_messages
- visual_designs
- visual_design_templates
- content_adaptations
- adaptation_patterns
- content_patterns
- policy_decisions
- meta_learner_state
- recommendation_outcomes
- recommendation_patterns
- strategy_insights
```

### Tables Requiring Repair (After Removing Duplicates)
These will exist after migrations 007-010, but need normalization:
- **agent_recommendations** - Standardized to 008 schema
- **agent_trust_scores** - Standardized to 008 schema with workspace_id backfill

---

## Migration Execution Plan

### Phase 1: Repair Critical Conflicts (Migration 011)

```sql
-- 011_fix_duplicate_table_conflicts.sql

-- 1. Drop conflicting duplicate definitions
DROP TABLE IF EXISTS agent_recommendations_old CASCADE;
DROP TABLE IF EXISTS agent_trust_scores_old CASCADE;

-- 2. Preserve data from conflicting 007 definitions (if they differ from 008)
-- These queries assume 008 schema is canonical

-- 3. Ensure 008 extended schema is active for both tables
-- (Already created by 008_self_improving_loops.sql)

-- 4. Backfill workspace_id for agent_trust_scores
-- (Migration script will handle)

-- 5. Remove duplicate competitors definition from 009
-- (Already singular in final state)
```

### Phase 2: Remove Unused Features (Migration 012)

**Option A: Full Removal** (If gamification/tech tree not planned)
```sql
-- 012_remove_unused_features.sql

-- Remove Gamification
DROP TABLE IF EXISTS quest_milestones CASCADE;
DROP TABLE IF EXISTS quest_moves CASCADE;
DROP TABLE IF EXISTS quests CASCADE;

-- Remove Tech Tree
DROP TABLE IF EXISTS maneuver_prerequisites CASCADE;
DROP TABLE IF EXISTS capability_nodes CASCADE;
```

**Option B: Archive Instead** (For compliance/audit)
```sql
-- 012_archive_unused_features.sql

-- Soft-delete: Rename tables to indicate deprecation
ALTER TABLE quests RENAME TO _archived_quests_20240127;
ALTER TABLE quest_moves RENAME TO _archived_quest_moves_20240127;
-- ... etc

-- Keep data, reduce active schema clutter
```

**Recommendation**: Use Option A (full removal) - these tables have zero data and zero usage.

### Phase 3: Add Codex Tables (Migration 013+)

```sql
-- 013_add_codex_positioning_campaigns.sql
-- 014_add_codex_gamification_achievements.sql
-- 015_add_codex_agent_registry.sql
-- 016_add_codex_rag_embeddings.sql
-- ... etc
```

---

## Impact Analysis

### Storage Impact
**Before Cleanup**: 52 tables, ~150 KB schema size
**After Cleanup**: 47 tables (if removing gamification/tech tree)
**Space Savings**: ~5 KB (minor, but cleaner)

**Primary Benefit**: Schema clarity - remove confusing unused tables

### Data Impact
- **Preserved**: All active tables and their data (no loss)
- **Removed**: Zero rows in unused tables (safe to drop)
- **Modified**: agent_recommendations and agent_trust_scores (data remains, schema normalized)

### Application Impact
- **Migrations**: Must run cleanup BEFORE adding new Codex tables
- **Downtime**: ~5-10 minutes (typical Supabase migration)
- **Rollback**: Possible if migration fails before running (schema-only changes are reversible)
- **Testing**: Run in staging first, verify no code references removed tables

### Code Impact
**Tables being removed have ZERO backend references**, so no code changes needed:
- No imports
- No routes accessing them
- No service queries

**Verification script**:
```bash
# Check if any Python code references removed tables
grep -r "quest" backend/ --include="*.py" | grep -v test
grep -r "capability_nodes" backend/ --include="*.py"
grep -r "maneuver_prerequisites" backend/ --include="*.py"

# Should return: No results (safe to delete)
```

---

## Recommended Cleanup Path

### Decision 1: Gamification & Tech Tree
**Status**: Unimplemented
**Options**:
- A) Keep for future implementation (takes 2 KB, no cost)
- B) Remove now, re-add later if needed (cleaner schema)

**Recommendation**: **REMOVE** - Not on roadmap, cleaner to add back if needed

**Affected Tables**: quests, quest_moves, quest_milestones, capability_nodes, maneuver_prerequisites (5 tables)

### Decision 2: Partially Implemented Features
**Status**: Schema exists, minimal/no code
**Options**:
- A) Mark as deprecated, archive
- B) Document for future implementation phases
- C) Remove

**Recommendation**: **DOCUMENT & KEEP** - These are sound features:
- quick_wins: Mini-campaigns from market signals (useful)
- cohort_relations: ICP network graph (useful)
- move_decisions: Weekly review workflow (useful)
- notifications: In-app system (essential)

Mark as "Phase 2+" features in documentation.

### Decision 3: Low Priority Implementations
**Status**: Schema exists, some agent references

**Recommendation**: **KEEP** - Structures are there, implement when agent system activates

---

## Execution Checklist

- [ ] **Confirm**: Stakeholders approve removal of unused tables (quests, capability_nodes, etc.)
- [ ] **Backup**: Export current schema and data (Supabase dashboard)
- [ ] **Staging Test**: Run migrations on staging database first
- [ ] **Code Verify**: Grep for removed table references (should be none)
- [ ] **Verify Dependencies**: Check foreign keys, triggers, RLS policies
- [ ] **Create Migration 011**: Fix duplicate table conflicts
- [ ] **Create Migration 012**: Remove unused tables (or archive)
- [ ] **Run Migrations**: Execute against staging, then production
- [ ] **Verify**: Query system catalog to confirm deletions
- [ ] **Document**: Update data model documentation
- [ ] **Commit**: Version control migration files and cleanup notes

---

## Go/No-Go Decision

### Ready to Proceed?
- ✅ Duplicate conflicts identified (can be fixed)
- ✅ Unused tables identified (safe to remove)
- ✅ Zero code dependencies on removed tables
- ✅ Migration strategy defined
- ✅ Rollback plan available

### **RECOMMENDATION: PROCEED WITH CLEANUP**

Current timeline: 1-2 hours to fix conflicts and remove unused tables.

After cleanup, schema will be **clean and ready for 30+ Codex tables**.

---

## Cleanup SQL Files to Create

1. **011_fix_migration_conflicts.sql** - Normalize agent_recommendations & agent_trust_scores
2. **012_remove_unused_features.sql** - Drop quests, capability_nodes tables
3. **VERIFICATION_QUERIES.sql** - Post-cleanup validation queries

---

## Next Steps

1. **Approve cleanup plan** - Confirm which tables to remove
2. **Run migrations** - Execute cleanup SQL against staging DB
3. **Verify** - Test application with cleaned schema
4. **Promote to production** - Apply to production after staging validation
5. **Begin Phase 2** - Create Codex tables (positioning, campaigns, achievements, etc.)

**Timeline**: 2-3 days (cleanup + testing) before starting Codex migrations.

---

## Questions to Resolve

1. **Gamification**: Is this planned for any phase? If so, when?
   - Current: Tables created but not implemented
   - Decision: Remove now or keep for future?

2. **Quick Wins**: Should we implement this before Codex, or later?
   - Current: Schema exists, no backend code
   - Decision: Implement or archive?

3. **Partial Tables**: Move decisions, notifications, cohort_relations - implement or deprecate?
   - Current: Some schema, minimal code
   - Decision: Phase 2 features or remove?

---

**Awaiting approval to proceed with cleanup** ✋
