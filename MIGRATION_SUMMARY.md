# RaptorFlow Database Migration Summary

## Overview

This document summarizes the canonical database migrations for RaptorFlow. All migrations follow the consolidation plan and reference only existing, production-ready migration files.

**Last Updated:** 2026-01-30

---

## Canonical Migrations

RaptorFlow uses a consolidated set of 4 canonical migrations that establish the complete database schema:

### 1. Base Schema Migration
**File:** `@C:\Users\hp\.windsurf\worktrees\Raptorflow\Raptorflow-b28c609d\supabase\migrations\001_canonical_base_schema.sql`

**Purpose:** Creates core tables for user management and workspace multi-tenancy

**Tables Created:**
- `users` - User profiles linked to Supabase auth
- `workspaces` - Multi-tenant workspace containers
- `workspace_members` - Workspace membership and roles

**Features:**
- UUID primary keys with auto-generation
- Automatic `updated_at` timestamp triggers
- Performance indexes on foreign keys and lookup columns
- JSONB columns for flexible metadata storage

### 2. Auth System Migration
**File:** `@C:\Users\hp\.windsurf\worktrees\Raptorflow\Raptorflow-b28c609d\supabase\migrations\002_canonical_auth_system.sql`

**Purpose:** Implements automatic user provisioning on signup

**Functions Created:**
- `generate_workspace_slug()` - Generates unique workspace slugs
- `handle_new_auth_user()` - Auto-creates user profile and workspace

**Trigger:**
- `trg_handle_new_auth_user` - Fires on `auth.users` INSERT

**Behavior:**
- New Supabase auth users automatically get a `users` record
- Each user gets a default workspace created
- User is added as workspace owner in `workspace_members`

### 3. Subscription System Migration
**File:** `@C:\Users\hp\.windsurf\worktrees\Raptorflow\Raptorflow-b28c609d\supabase\migrations\003_canonical_subscription_system.sql`

**Purpose:** Establishes subscription plans and payment infrastructure

**Tables Created:**
- `subscription_plans` - Available plans (Ascent, Glide, Soar)
- `user_subscriptions` - Active workspace subscriptions
- `subscription_events` - Audit log of subscription changes
- `payment_transactions` - Payment records

**Default Plans:**

| Plan | Monthly (INR) | Annual (INR) | Features |
|------|---------------|--------------|----------|
| **Ascent** | ₹5,000 | ₹50,000 | Basic ICP profiling, 3 moves/week, Email support |
| **Glide** | ₹7,000 | ₹70,000 | Advanced ICP, 10 moves/week, Priority support, A/B testing |
| **Soar** | ₹10,000 | ₹100,000 | Enterprise ICP, Unlimited moves, 24/7 support, API access |

**Constraints:**
- Plan names restricted to: 'Ascent', 'Glide', 'Soar'
- Positive price validation
- Unique workspace subscription constraint
- Foreign key cascades and restrictions

### 4. RLS Policies Migration
**File:** `@C:\Users\hp\.windsurf\worktrees\Raptorflow\Raptorflow-b28c609d\supabase\migrations\004_canonical_rls_policies.sql`

**Purpose:** Implements Row Level Security for all tables

**Security Model:**
- **Users:** Can view/update own profile only
- **Workspaces:** Members can view, admins can update, owners can delete
- **Workspace Members:** Members can view, admins can manage
- **Subscriptions:** Workspace members can view, admins can manage
- **Payments:** Workspace members can view their transactions
- **Plans:** All authenticated users can view active plans

**Service Role:**
- Bypasses all RLS policies for backend operations
- Used for webhooks and administrative tasks

---

## Execution Order

Migrations **must** be executed in this exact order:

```bash
1. 001_canonical_base_schema.sql       # Foundation tables
2. 002_canonical_auth_system.sql       # Auth triggers
3. 003_canonical_subscription_system.sql # Business logic
4. 004_canonical_rls_policies.sql      # Security layer
```

**Dependencies:**
- Migration 002 depends on 001 (requires `users`, `workspaces` tables)
- Migration 003 depends on 001 (requires `workspaces` table)
- Migration 004 depends on 001, 002, 003 (requires all tables)

---

## How to Execute

### Option 1: Supabase CLI (Recommended)
```bash
# Reset database and run all migrations
supabase db reset

# Migrations execute automatically in alphanumeric order
```

### Option 2: Manual psql
```bash
psql -h <host> -U <user> -d <database> -f supabase/migrations/001_canonical_base_schema.sql
psql -h <host> -U <user> -d <database> -f supabase/migrations/002_canonical_auth_system.sql
psql -h <host> -U <user> -d <database> -f supabase/migrations/003_canonical_subscription_system.sql
psql -h <host> -U <user> -d <database> -f supabase/migrations/004_canonical_rls_policies.sql
```

### Option 3: Supabase Dashboard
1. Navigate to SQL Editor
2. Copy contents of each migration file
3. Execute in order (001 → 002 → 003 → 004)
4. Verify success before proceeding to next migration

---

## Verification

After running all migrations, verify the setup:

```sql
-- Check all tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Verify RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables
WHERE schemaname = 'public' AND rowsecurity = true
ORDER BY tablename;

-- Check subscription plans
SELECT name, slug, price_monthly, price_annual, is_active
FROM subscription_plans
ORDER BY sort_order;

-- Count RLS policies
SELECT tablename, COUNT(*) as policy_count
FROM pg_policies
WHERE schemaname = 'public'
GROUP BY tablename
ORDER BY tablename;
```

**Expected Results:**
- 8+ tables in public schema
- All tables have RLS enabled
- 3 subscription plans (Ascent, Glide, Soar)
- Multiple RLS policies per table

---

## Archived Migrations

The following legacy migrations have been **superseded** and moved to `@C:\Users\hp\.windsurf\worktrees\Raptorflow\Raptorflow-b28c609d\supabase\migrations\archive\superseded\`:

**Base Schema (replaced by 001):**
- `000_base_schema.sql`
- `000_base_schema_clean.sql`
- `20260130000000_define_core_tables.sql`

**Auth System (replaced by 002):**
- `001_auth_triggers.sql`
- `20250210_auth_system_fix.sql`
- `20260122074403_final_auth_consolidation.sql`

**Subscription System (replaced by 003):**
- `005_subscriptions.sql`
- `20260126_unified_subscription_system.sql`
- `20250130_subscription_cleanup.sql`
- `20250130_subscription_unification_fix.sql`
- `20260126_populate_plans.sql`
- `20260130_drop_old_table_adopt_archive_schema.sql`

**RLS Policies (replaced by 004):**
- `20260130000000_rls_consolidation.sql`
- `130_fix_critical_rls_security.sql`
- `134_fix_rls_performance.sql`
- `20260130_comprehensive_security_fixes.sql`
- `20260205000000_workspace_rls_isolation.sql`

These files are preserved for historical reference but should **not** be executed.

---

## Migration Governance

For detailed migration management policies, see:
- `@C:\Users\hp\.windsurf\worktrees\Raptorflow\Raptorflow-b28c609d\supabase\migrations\MIGRATION_ORDER.md` - Execution order and dependencies
- `@C:\Users\hp\.windsurf\worktrees\Raptorflow\Raptorflow-b28c609d\supabase\migrations\MIGRATION_GOVERNANCE.md` - Best practices and policies

**Key Principles:**
- Canonical migrations (001-004) are **immutable** after production deployment
- All migrations must be **idempotent** (safe to run multiple times)
- New features require **new migration files** (005+)
- Never modify deployed migrations - create rollback migrations instead

---

## Support & Troubleshooting

### Common Issues

**Issue:** Migration fails with "relation already exists"
**Solution:** Migrations are idempotent - this is expected. Check for actual errors below this message.

**Issue:** RLS policies blocking queries
**Solution:** Ensure user is authenticated and has workspace membership. Check `workspace_members` table.

**Issue:** Subscription plans not visible
**Solution:** Verify `is_active = true` on plans and user has `authenticated` role.

### Getting Help

1. Review migration file comments for detailed documentation
2. Check `MIGRATION_ORDER.md` for execution sequence
3. Consult `MIGRATION_GOVERNANCE.md` for best practices
4. Verify database state with verification queries above

---

**Migration Status:** ✅ Production Ready

**Canonical Migrations:** 4 files (001-004)

**Archived Migrations:** 17 files (superseded)

**Total Database Objects:** 8+ tables, 20+ policies, 10+ indexes, 5+ triggers
