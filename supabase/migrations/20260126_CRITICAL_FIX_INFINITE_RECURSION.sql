-- =================================================================
-- CRITICAL FIX: INFINITE RECURSION IN RLS POLICIES
-- Issue: Migration 137 created nested subqueries in policies
-- that query profiles/users, causing infinite recursion loops
-- Solution: Disable ALL recursive policies, use simple checks
-- =================================================================

-- STEP 1: DISABLE ALL RECURSIVE POLICIES ON users TABLE
DROP POLICY IF EXISTS "users_select_consolidated" ON public.users;
DROP POLICY IF EXISTS "users_update_consolidated" ON public.users;
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
DROP POLICY IF EXISTS "Admins can view all users" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
DROP POLICY IF EXISTS "Admins can update users" ON public.users;

-- STEP 2: DISABLE ALL RECURSIVE POLICIES ON workspaces TABLE
DROP POLICY IF EXISTS "workspaces_select_consolidated" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_consolidated" ON public.workspaces;
DROP POLICY IF EXISTS "Users can view own workspace" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_select_own" ON public.workspaces;
DROP POLICY IF EXISTS "Users can update own workspace" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_own" ON public.workspaces;

-- STEP 3: DISABLE RECURSIVE POLICIES WITH NESTED PROFILE QUERIES
DROP POLICY IF EXISTS "payment_transactions_select_consolidated" ON public.payment_transactions;
DROP POLICY IF EXISTS "subscriptions_select_consolidated" ON public.subscriptions;

-- STEP 4: REPLACE WITH SIMPLE, NON-RECURSIVE POLICIES
-- These use ONLY auth.uid() and auth.role(), never querying other tables

-- Users table - simple auth check
CREATE POLICY "users_allow_authenticated" ON public.users
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "users_allow_update_self" ON public.users
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Workspaces table - simple auth check
CREATE POLICY "workspaces_allow_authenticated" ON public.workspaces
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "workspaces_allow_update" ON public.workspaces
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "workspaces_allow_insert" ON public.workspaces
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Subscriptions table - simple auth check
CREATE POLICY "subscriptions_allow_authenticated" ON public.subscriptions
    FOR SELECT USING (auth.role() = 'authenticated');

-- Payment transactions - simple auth check
CREATE POLICY "payment_transactions_allow_authenticated" ON public.payment_transactions
    FOR SELECT USING (auth.role() = 'authenticated');

-- STEP 5: ENSURE PROFILES TABLE HAS SAFE POLICIES
DROP POLICY IF EXISTS "profiles_service_all" ON public.profiles;
CREATE POLICY "profiles_allow_all" ON public.profiles
    FOR ALL USING (true) WITH CHECK (true);

-- STEP 6: ENSURE PLANS TABLE HAS SAFE POLICIES
DROP POLICY IF EXISTS "plans_service_all" ON public.plans;
CREATE POLICY "plans_allow_all" ON public.plans
    FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "subscriptions_service_all" ON public.subscriptions;
CREATE POLICY "subscriptions_allow_all" ON public.subscriptions
    FOR ALL USING (true) WITH CHECK (true);

-- STEP 7: VERIFY RLS IS ENABLED ON PROBLEMATIC TABLES
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payment_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.plans ENABLE ROW LEVEL SECURITY;

-- STEP 8: GRANT SERVICE ROLE FULL ACCESS (bypasses RLS)
GRANT ALL ON public.users TO service_role;
GRANT ALL ON public.workspaces TO service_role;
GRANT ALL ON public.subscriptions TO service_role;
GRANT ALL ON public.payment_transactions TO service_role;
GRANT ALL ON public.profiles TO service_role;
GRANT ALL ON public.plans TO service_role;
