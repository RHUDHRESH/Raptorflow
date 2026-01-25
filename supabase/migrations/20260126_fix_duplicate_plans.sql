-- =================================================================
-- FIX DUPLICATE PLANS AND INFINITE RECURSION
-- Issue: Plans displayed twice, infinite recursion in users policy
-- =================================================================

-- Remove recursive policies from workspaces that caused duplicate returns
DROP POLICY IF EXISTS "workspaces_select_consolidated" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_consolidated" ON public.workspaces;

-- Create simple workspace policies without nested profile queries
CREATE POLICY "workspaces_select_simple" ON public.workspaces
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "workspaces_update_simple" ON public.workspaces
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "workspaces_insert_simple" ON public.workspaces
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Fix subscription policies to avoid recursion
DROP POLICY IF EXISTS "subscriptions_select_consolidated" ON public.subscriptions;
CREATE POLICY "subscriptions_select_simple" ON public.subscriptions
    FOR SELECT USING (auth.role() = 'authenticated');

-- Fix payment_transactions policies to avoid recursion
DROP POLICY IF EXISTS "payment_transactions_select_consolidated" ON public.payment_transactions;
CREATE POLICY "payment_transactions_select_simple" ON public.payment_transactions
    FOR SELECT USING (auth.role() = 'authenticated');

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
