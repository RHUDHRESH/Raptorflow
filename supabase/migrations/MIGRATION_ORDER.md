# Migration Execution Order

This document defines the canonical migration execution order for RaptorFlow's Supabase database.

## Canonical Migrations (Execute in Order)

### Phase 1: Foundation
1. **001_canonical_base_schema.sql**
   - Creates core tables: `users`, `workspaces`, `workspace_members`
   - Establishes base indexes and triggers
   - **Dependencies**: None (requires Supabase auth.users table)
   - **Status**: ✅ Production-ready

2. **002_canonical_auth_system.sql**
   - Creates auth trigger functions
   - Implements automatic user/workspace creation on signup
   - **Dependencies**: 001_canonical_base_schema.sql
   - **Status**: ✅ Production-ready

### Phase 2: Business Logic
3. **003_canonical_subscription_system.sql**
   - Creates subscription plans (Ascent, Glide, Soar)
   - Creates user subscriptions, events, and payment transactions
   - Inserts default plan data
   - **Dependencies**: 001_canonical_base_schema.sql
   - **Status**: ✅ Production-ready

### Phase 3: Security
4. **004_canonical_rls_policies.sql**
   - Implements Row Level Security policies for all tables
   - Enforces workspace isolation and role-based access
   - **Dependencies**: 001, 002, 003
   - **Status**: ✅ Production-ready

## Legacy Migrations (Archived)

The following migrations have been superseded by the canonical migrations above:

### Superseded Base Schema Migrations
- `000_base_schema.sql` → Replaced by `001_canonical_base_schema.sql`
- `000_base_schema_clean.sql` → Replaced by `001_canonical_base_schema.sql`
- `20260130000000_define_core_tables.sql` → Replaced by `001_canonical_base_schema.sql`

### Superseded Auth Migrations
- `001_auth_triggers.sql` → Replaced by `002_canonical_auth_system.sql`
- `20250210_auth_system_fix.sql` → Replaced by `002_canonical_auth_system.sql`
- `20260122074403_final_auth_consolidation.sql` → Replaced by `002_canonical_auth_system.sql`

### Superseded Subscription Migrations
- `005_subscriptions.sql` → Replaced by `003_canonical_subscription_system.sql`
- `20260126_unified_subscription_system.sql` → Replaced by `003_canonical_subscription_system.sql`
- `20250130_subscription_cleanup.sql` → Replaced by `003_canonical_subscription_system.sql`
- `20250130_subscription_unification_fix.sql` → Replaced by `003_canonical_subscription_system.sql`
- `20260126_populate_plans.sql` → Replaced by `003_canonical_subscription_system.sql`
- `20260130_drop_old_table_adopt_archive_schema.sql` → Replaced by `003_canonical_subscription_system.sql`

### Superseded RLS Migrations
- `20260130000000_rls_consolidation.sql` → Replaced by `004_canonical_rls_policies.sql`
- `130_fix_critical_rls_security.sql` → Replaced by `004_canonical_rls_policies.sql`
- `134_fix_rls_performance.sql` → Replaced by `004_canonical_rls_policies.sql`
- `20260130_comprehensive_security_fixes.sql` → Replaced by `004_canonical_rls_policies.sql`
- `20260205000000_workspace_rls_isolation.sql` → Replaced by `004_canonical_rls_policies.sql`

### Superseded Fix Migrations
- `20260126_fix_duplicate_plans.sql` → Functionality in `003_canonical_subscription_system.sql`
- `20260126_CRITICAL_FIX_INFINITE_RECURSION.sql` → Fixed in `004_canonical_rls_policies.sql`
- `20260126_fix_foreign_key_references.sql` → Fixed in `003_canonical_subscription_system.sql`
- `20260129000000_fix_user_identification.sql` → Fixed in `002_canonical_auth_system.sql`

## Execution Instructions

### Fresh Database Setup
```bash
# Execute in order:
psql -f supabase/migrations/001_canonical_base_schema.sql
psql -f supabase/migrations/002_canonical_auth_system.sql
psql -f supabase/migrations/003_canonical_subscription_system.sql
psql -f supabase/migrations/004_canonical_rls_policies.sql
```

### Supabase CLI
```bash
# Migrations are automatically executed in alphanumeric order
supabase db reset
```

### Supabase Dashboard
1. Navigate to SQL Editor
2. Execute migrations in order (001 → 002 → 003 → 004)
3. Verify each migration completes successfully before proceeding

## Verification Queries

After running all migrations, verify the setup:

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;

-- Check subscription plans
SELECT name, slug, price_monthly, price_annual FROM subscription_plans 
ORDER BY sort_order;

-- Check policies
SELECT tablename, policyname FROM pg_policies 
WHERE schemaname = 'public' 
ORDER BY tablename, policyname;
```

## Migration Governance

- **New migrations** must follow the naming convention: `XXX_descriptive_name.sql`
- **Canonical migrations** (001-004) should NOT be modified after production deployment
- **Hotfixes** should be created as new migrations (e.g., `005_fix_specific_issue.sql`)
- **All migrations** must be idempotent (safe to run multiple times)
- **Breaking changes** require a new major migration version

## Rollback Strategy

Canonical migrations do NOT include rollback scripts. For production rollbacks:

1. Create a new migration that reverses the changes
2. Test thoroughly in staging environment
3. Document the rollback migration in this file
4. Execute during maintenance window

## Archive Location

Superseded migrations are moved to: `supabase/migrations/archive/`

This preserves historical context while keeping the active migration directory clean.
