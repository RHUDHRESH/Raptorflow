# Subscription Plans Migration Guide

## Overview

This guide documents the migration process for dropping the old `subscription_plans` table and adopting the archive schema. This migration ensures data integrity, proper foreign key relationships, and eliminates duplicate plan rows.

## Migration Files

### 1. Primary Migration: `20260130_drop_old_table_adopt_archive_schema.sql`

**Location:** `supabase/migrations/20260130_drop_old_table_adopt_archive_schema.sql`

**Purpose:** Migrate from old subscription_plans table to archive schema

**Steps:**
1. **Backup Existing Data** - Creates a temporary backup of existing subscription_plans data
2. **Drop Foreign Key Constraints** - Removes FK constraints from dependent tables
3. **Drop Old Table** - Removes the old subscription_plans table
4. **Create New Archive Schema Table** - Creates table with proper structure:
   - `id` (UUID, primary key)
   - `name` (VARCHAR, unique: 'Ascent', 'Glide', 'Soar')
   - `slug` (VARCHAR, unique: 'ascent', 'glide', 'soar')
   - `display_name` (VARCHAR)
   - `description` (TEXT)
   - `price_monthly` (INTEGER, in paise)
   - `price_annual` (INTEGER, in paise)
   - `currency` (VARCHAR, default: 'INR')
   - `features` (JSONB)
   - `limits` (JSONB)
   - `is_active` (BOOLEAN)
   - `sort_order` (INTEGER)
   - `created_at` (TIMESTAMPTZ)
   - `updated_at` (TIMESTAMPTZ)
5. **Migrate Data** - Restores data from backup with schema compatibility
6. **Insert Default Plans** - Adds default plans if table is empty:
   - **Ascent**: ₹5,000/month, ₹50,000/year
   - **Glide**: ₹7,000/month, ₹70,000/year
   - **Soar**: ₹10,000/month, ₹100,000/year
7. **Recreate Foreign Key Constraints** - Restores FK relationships:
   - `user_subscriptions.plan_id` → `subscription_plans.id`
   - `subscription_events.previous_plan_id` → `subscription_plans.id`
   - `subscription_events.new_plan_id` → `subscription_plans.id`
   - `payment_transactions.plan_id` → `subscription_plans.id` (if exists)
8. **Create Indexes** - Performance optimization indexes
9. **Create Triggers** - Auto-update `updated_at` timestamp
10. **Enable RLS** - Row Level Security
11. **Create RLS Policies** - Security policies for data access
12. **Grant Permissions** - User and service role permissions
13. **Add Documentation** - Table and column comments
14. **Cleanup** - Remove temporary backup table

### 2. Secondary Migration: `20260126_fix_duplicate_plans.sql`

**Location:** `supabase/migrations/20260126_fix_duplicate_plans.sql`

**Purpose:** Remove duplicate plan rows and fix infinite recursion in policies

**Steps:**
1. **Remove Recursive Policies** - Drops policies causing infinite recursion
2. **Create Simple Policies** - Replaces with simple auth-based policies
3. **Remove Duplicate Plans** - Keeps only one row per plan ID
4. **Ensure Primary Key** - Validates and recreates primary key constraint

## Running the Migration

### Option 1: Using Python Script (Recommended)

```bash
# Ensure you have the required dependencies
pip install psycopg2-binary python-dotenv

# Set up your environment variables in .env file
# DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# Run the migration script
python run_subscription_migration.py
```

### Option 2: Manual SQL Execution

```bash
# Using psql
psql -h <host> -p <port> -U <user> -d <database> -f supabase/migrations/20260130_drop_old_table_adopt_archive_schema.sql

# Then run the duplicate fix
psql -h <host> -p <port> -U <user> -d <database> -f supabase/migrations/20260126_fix_duplicate_plans.sql
```

### Option 3: Using Supabase Dashboard

1. Go to Supabase Dashboard → SQL Editor
2. Copy and paste the content of `20260130_drop_old_table_adopt_archive_schema.sql`
3. Click "Run"
4. Copy and paste the content of `20260126_fix_duplicate_plans.sql`
5. Click "Run"

## Pre-Migration Checklist

- [ ] **Backup Database** - Create a full database backup before running migrations
- [ ] **Check Dependencies** - Ensure no active transactions or locks on subscription_plans table
- [ ] **Review Data** - Verify current subscription_plans data
- [ ] **Test Environment** - Run migrations in staging/test environment first
- [ ] **Notify Users** - Schedule maintenance window if needed

## Post-Migration Verification

### 1. Verify Table Structure

```sql
-- Check table exists and has correct structure
\d public.subscription_plans

-- Verify columns
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'subscription_plans'
ORDER BY ordinal_position;
```

### 2. Verify Data Integrity

```sql
-- Check plan count (should be 3)
SELECT COUNT(*) as plan_count FROM public.subscription_plans;

-- Verify plan names
SELECT name, slug, price_monthly, price_annual, is_active
FROM public.subscription_plans
ORDER BY sort_order;

-- Check for duplicates
SELECT id, name, slug, COUNT(*)
FROM public.subscription_plans
GROUP BY id, name, slug
HAVING COUNT(*) > 1;
```

### 3. Verify Foreign Keys

```sql
-- Check foreign key constraints
SELECT
    tc.table_name,
    tc.constraint_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name IN ('user_subscriptions', 'subscription_events', 'payment_transactions')
    AND ccu.table_name = 'subscription_plans';
```

### 4. Verify RLS Policies

```sql
-- Check RLS is enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND tablename = 'subscription_plans';

-- Check policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE tablename = 'subscription_plans';
```

### 5. Verify Indexes

```sql
-- Check indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'subscription_plans' AND schemaname = 'public';
```

### 6. Test Application Functionality

- [ ] **Plan Selection** - Verify users can select plans
- [ ] **Subscription Creation** - Test creating new subscriptions
- [ ] **Payment Processing** - Verify payment transactions work
- [ ] **Plan Upgrades** - Test plan upgrade/downgrade functionality
- [ ] **API Endpoints** - Check all subscription-related API endpoints

## Rollback Plan

If issues occur after migration, you can rollback using:

```sql
-- Note: This requires you to have a backup of the old table structure
-- 1. Drop the new table
DROP TABLE IF EXISTS public.subscription_plans CASCADE;

-- 2. Restore from backup (if you have one)
-- This depends on your backup strategy
```

**Important:** Always have a recent database backup before running migrations.

## Troubleshooting

### Issue: Foreign Key Constraint Violations

**Error:** `insert or update on table violates foreign key constraint`

**Solution:**
```sql
-- Check for orphaned records
SELECT us.id, us.plan_id
FROM user_subscriptions us
LEFT JOIN subscription_plans sp ON us.plan_id = sp.id
WHERE sp.id IS NULL;

-- Update or delete orphaned records
DELETE FROM user_subscriptions
WHERE plan_id NOT IN (SELECT id FROM subscription_plans);
```

### Issue: Duplicate Plan Rows

**Error:** Plans appearing multiple times in UI

**Solution:**
```sql
-- Run the duplicate fix migration
-- Or manually remove duplicates
DELETE FROM subscription_plans p1
WHERE p1.ctid > (
    SELECT MIN(p2.ctid)
    FROM subscription_plans p2
    WHERE p1.slug = p2.slug
);
```

### Issue: RLS Policy Recursion

**Error:** `stack depth limit exceeded` or infinite recursion

**Solution:**
```sql
-- Run the duplicate fix migration which includes policy fixes
-- Or manually simplify policies
DROP POLICY IF EXISTS "subscription_plans_view_active" ON public.subscription_plans;
CREATE POLICY "subscription_plans_view_simple" ON public.subscription_plans
    FOR SELECT USING (auth.role() = 'authenticated');
```

## Migration Summary

### What Changed

1. **Table Schema** - Adopted archive schema with proper constraints
2. **Data Migration** - Preserved existing data with schema compatibility
3. **Foreign Keys** - Updated all FK relationships
4. **Indexes** - Added performance optimization indexes
5. **RLS Policies** - Simplified to prevent infinite recursion
6. **Permissions** - Properly granted to authenticated users and service role

### What Stayed the Same

1. **Plan Names** - Ascent, Glide, Soar
2. **Pricing** - ₹5,000, ₹7,000, ₹10,000 monthly
3. **Features** - JSONB feature arrays preserved
4. **Limits** - JSONB limit objects preserved

## Support

For issues or questions:
1. Check the migration logs
2. Review the troubleshooting section
3. Verify database connection and permissions
4. Check Supabase dashboard for any errors

## Additional Resources

- [Supabase Migration Guide](https://supabase.com/docs/guides/database/migrations)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [RLS Policies](https://supabase.com/docs/guides/auth/row-level-security)

## Overview

This guide documents the migration process for dropping the old `subscription_plans` table and adopting the archive schema. This migration ensures data integrity, proper foreign key relationships, and eliminates duplicate plan rows.

## Migration Files

### 1. Primary Migration: `20260130_drop_old_table_adopt_archive_schema.sql`

**Location:** `supabase/migrations/20260130_drop_old_table_adopt_archive_schema.sql`

**Purpose:** Migrate from old subscription_plans table to archive schema

**Steps:**
1. **Backup Existing Data** - Creates a temporary backup of existing subscription_plans data
2. **Drop Foreign Key Constraints** - Removes FK constraints from dependent tables
3. **Drop Old Table** - Removes the old subscription_plans table
4. **Create New Archive Schema Table** - Creates table with proper structure:
   - `id` (UUID, primary key)
   - `name` (VARCHAR, unique: 'Ascent', 'Glide', 'Soar')
   - `slug` (VARCHAR, unique: 'ascent', 'glide', 'soar')
   - `display_name` (VARCHAR)
   - `description` (TEXT)
   - `price_monthly` (INTEGER, in paise)
   - `price_annual` (INTEGER, in paise)
   - `currency` (VARCHAR, default: 'INR')
   - `features` (JSONB)
   - `limits` (JSONB)
   - `is_active` (BOOLEAN)
   - `sort_order` (INTEGER)
   - `created_at` (TIMESTAMPTZ)
   - `updated_at` (TIMESTAMPTZ)
5. **Migrate Data** - Restores data from backup with schema compatibility
6. **Insert Default Plans** - Adds default plans if table is empty:
   - **Ascent**: ₹5,000/month, ₹50,000/year
   - **Glide**: ₹7,000/month, ₹70,000/year
   - **Soar**: ₹10,000/month, ₹100,000/year
7. **Recreate Foreign Key Constraints** - Restores FK relationships:
   - `user_subscriptions.plan_id` → `subscription_plans.id`
   - `subscription_events.previous_plan_id` → `subscription_plans.id`
   - `subscription_events.new_plan_id` → `subscription_plans.id`
   - `payment_transactions.plan_id` → `subscription_plans.id` (if exists)
8. **Create Indexes** - Performance optimization indexes
9. **Create Triggers** - Auto-update `updated_at` timestamp
10. **Enable RLS** - Row Level Security
11. **Create RLS Policies** - Security policies for data access
12. **Grant Permissions** - User and service role permissions
13. **Add Documentation** - Table and column comments
14. **Cleanup** - Remove temporary backup table

### 2. Secondary Migration: `20260126_fix_duplicate_plans.sql`

**Location:** `supabase/migrations/20260126_fix_duplicate_plans.sql`

**Purpose:** Remove duplicate plan rows and fix infinite recursion in policies

**Steps:**
1. **Remove Recursive Policies** - Drops policies causing infinite recursion
2. **Create Simple Policies** - Replaces with simple auth-based policies
3. **Remove Duplicate Plans** - Keeps only one row per plan ID
4. **Ensure Primary Key** - Validates and recreates primary key constraint

## Running the Migration

### Option 1: Using Python Script (Recommended)

```bash
# Ensure you have the required dependencies
pip install psycopg2-binary python-dotenv

# Set up your environment variables in .env file
# DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# Run the migration script
python run_subscription_migration.py
```

### Option 2: Manual SQL Execution

```bash
# Using psql
psql -h <host> -p <port> -U <user> -d <database> -f supabase/migrations/20260130_drop_old_table_adopt_archive_schema.sql

# Then run the duplicate fix
psql -h <host> -p <port> -U <user> -d <database> -f supabase/migrations/20260126_fix_duplicate_plans.sql
```

### Option 3: Using Supabase Dashboard

1. Go to Supabase Dashboard → SQL Editor
2. Copy and paste the content of `20260130_drop_old_table_adopt_archive_schema.sql`
3. Click "Run"
4. Copy and paste the content of `20260126_fix_duplicate_plans.sql`
5. Click "Run"

## Pre-Migration Checklist

- [ ] **Backup Database** - Create a full database backup before running migrations
- [ ] **Check Dependencies** - Ensure no active transactions or locks on subscription_plans table
- [ ] **Review Data** - Verify current subscription_plans data
- [ ] **Test Environment** - Run migrations in staging/test environment first
- [ ] **Notify Users** - Schedule maintenance window if needed

## Post-Migration Verification

### 1. Verify Table Structure

```sql
-- Check table exists and has correct structure
\d public.subscription_plans

-- Verify columns
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'subscription_plans'
ORDER BY ordinal_position;
```

### 2. Verify Data Integrity

```sql
-- Check plan count (should be 3)
SELECT COUNT(*) as plan_count FROM public.subscription_plans;

-- Verify plan names
SELECT name, slug, price_monthly, price_annual, is_active
FROM public.subscription_plans
ORDER BY sort_order;

-- Check for duplicates
SELECT id, name, slug, COUNT(*)
FROM public.subscription_plans
GROUP BY id, name, slug
HAVING COUNT(*) > 1;
```

### 3. Verify Foreign Keys

```sql
-- Check foreign key constraints
SELECT
    tc.table_name,
    tc.constraint_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name IN ('user_subscriptions', 'subscription_events', 'payment_transactions')
    AND ccu.table_name = 'subscription_plans';
```

### 4. Verify RLS Policies

```sql
-- Check RLS is enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND tablename = 'subscription_plans';

-- Check policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE tablename = 'subscription_plans';
```

### 5. Verify Indexes

```sql
-- Check indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'subscription_plans' AND schemaname = 'public';
```

### 6. Test Application Functionality

- [ ] **Plan Selection** - Verify users can select plans
- [ ] **Subscription Creation** - Test creating new subscriptions
- [ ] **Payment Processing** - Verify payment transactions work
- [ ] **Plan Upgrades** - Test plan upgrade/downgrade functionality
- [ ] **API Endpoints** - Check all subscription-related API endpoints

## Rollback Plan

If issues occur after migration, you can rollback using:

```sql
-- Note: This requires you to have a backup of the old table structure
-- 1. Drop the new table
DROP TABLE IF EXISTS public.subscription_plans CASCADE;

-- 2. Restore from backup (if you have one)
-- This depends on your backup strategy
```

**Important:** Always have a recent database backup before running migrations.

## Troubleshooting

### Issue: Foreign Key Constraint Violations

**Error:** `insert or update on table violates foreign key constraint`

**Solution:**
```sql
-- Check for orphaned records
SELECT us.id, us.plan_id
FROM user_subscriptions us
LEFT JOIN subscription_plans sp ON us.plan_id = sp.id
WHERE sp.id IS NULL;

-- Update or delete orphaned records
DELETE FROM user_subscriptions
WHERE plan_id NOT IN (SELECT id FROM subscription_plans);
```

### Issue: Duplicate Plan Rows

**Error:** Plans appearing multiple times in UI

**Solution:**
```sql
-- Run the duplicate fix migration
-- Or manually remove duplicates
DELETE FROM subscription_plans p1
WHERE p1.ctid > (
    SELECT MIN(p2.ctid)
    FROM subscription_plans p2
    WHERE p1.slug = p2.slug
);
```

### Issue: RLS Policy Recursion

**Error:** `stack depth limit exceeded` or infinite recursion

**Solution:**
```sql
-- Run the duplicate fix migration which includes policy fixes
-- Or manually simplify policies
DROP POLICY IF EXISTS "subscription_plans_view_active" ON public.subscription_plans;
CREATE POLICY "subscription_plans_view_simple" ON public.subscription_plans
    FOR SELECT USING (auth.role() = 'authenticated');
```

## Migration Summary

### What Changed

1. **Table Schema** - Adopted archive schema with proper constraints
2. **Data Migration** - Preserved existing data with schema compatibility
3. **Foreign Keys** - Updated all FK relationships
4. **Indexes** - Added performance optimization indexes
5. **RLS Policies** - Simplified to prevent infinite recursion
6. **Permissions** - Properly granted to authenticated users and service role

### What Stayed the Same

1. **Plan Names** - Ascent, Glide, Soar
2. **Pricing** - ₹5,000, ₹7,000, ₹10,000 monthly
3. **Features** - JSONB feature arrays preserved
4. **Limits** - JSONB limit objects preserved

## Support

For issues or questions:
1. Check the migration logs
2. Review the troubleshooting section
3. Verify database connection and permissions
4. Check Supabase dashboard for any errors

## Additional Resources

- [Supabase Migration Guide](https://supabase.com/docs/guides/database/migrations)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [RLS Policies](https://supabase.com/docs/guides/auth/row-level-security)
