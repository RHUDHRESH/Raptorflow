-- =================================================================
-- FIX DUPLICATE PLANS AND INFINITE RECURSION
-- Issue: Plans displayed twice, infinite recursion in users policy
-- Note: This migration now only drops policies and fixes plans table
-- Properly scoped policies are created in later migrations
-- =================================================================

-- Drop recursive/permissive policies from workspaces
DROP POLICY IF EXISTS "workspaces_select_consolidated" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_consolidated" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_select_simple" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_simple" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_insert_simple" ON public.workspaces;

-- Drop recursive/permissive subscription policies
DROP POLICY IF EXISTS "subscriptions_select_consolidated" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_select_simple" ON public.subscriptions;

-- Drop recursive/permissive payment_transactions policies
DROP POLICY IF EXISTS "payment_transactions_select_consolidated" ON public.payment_transactions;
DROP POLICY IF EXISTS "payment_transactions_select_simple" ON public.payment_transactions;

-- Remove any duplicate plans (keep only one of each)
DELETE FROM public.plans p1
WHERE p1.ctid > (
    SELECT MIN(p2.ctid)
    FROM public.plans p2
    WHERE p1.id = p2.id
);

-- Ensure plans table has no duplicate constraints
ALTER TABLE public.plans DROP CONSTRAINT IF EXISTS plans_pkey CASCADE;
ALTER TABLE public.plans ADD PRIMARY KEY (id);

-- NOTE: Properly scoped RLS policies are created in:
-- - 20260130_fix_duplicate_subscription_plans.sql
