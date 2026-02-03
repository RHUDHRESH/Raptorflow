-- =================================================================
-- CRITICAL FIX: INFINITE RECURSION IN RLS POLICIES
-- Issue: Migration 137 created nested subqueries in policies
-- that query profiles/users, causing infinite recursion loops
-- Solution: Drop recursive policies, properly scoped policies
-- are created in later migrations
-- =================================================================

-- STEP 1: DROP ALL RECURSIVE/PERMISSIVE POLICIES ON users TABLE
DROP POLICY IF EXISTS "users_select_consolidated" ON public.users;
DROP POLICY IF EXISTS "users_update_consolidated" ON public.users;
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
DROP POLICY IF EXISTS "Admins can view all users" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
DROP POLICY IF EXISTS "Admins can update users" ON public.users;
DROP POLICY IF EXISTS "users_allow_authenticated" ON public.users;
DROP POLICY IF EXISTS "users_allow_update_self" ON public.users;

-- STEP 2: DROP ALL RECURSIVE/PERMISSIVE POLICIES ON workspaces TABLE
DROP POLICY IF EXISTS "workspaces_select_consolidated" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_consolidated" ON public.workspaces;
DROP POLICY IF EXISTS "Users can view own workspace" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_select_own" ON public.workspaces;
DROP POLICY IF EXISTS "Users can update own workspace" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_own" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_allow_authenticated" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_allow_update" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_allow_insert" ON public.workspaces;

-- STEP 3: DROP RECURSIVE/PERMISSIVE POLICIES WITH NESTED PROFILE QUERIES
DROP POLICY IF EXISTS "payment_transactions_select_consolidated" ON public.payment_transactions;
DROP POLICY IF EXISTS "subscriptions_select_consolidated" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_allow_authenticated" ON public.subscriptions;
DROP POLICY IF EXISTS "payment_transactions_allow_authenticated" ON public.payment_transactions;

-- STEP 4: DROP OVERLY PERMISSIVE "ALLOW ALL" POLICIES
DROP POLICY IF EXISTS "profiles_service_all" ON public.profiles;
DROP POLICY IF EXISTS "profiles_allow_all" ON public.profiles;
DROP POLICY IF EXISTS "plans_service_all" ON public.plans;
DROP POLICY IF EXISTS "plans_allow_all" ON public.plans;
DROP POLICY IF EXISTS "subscriptions_service_all" ON public.subscriptions;
DROP POLICY IF EXISTS "subscriptions_allow_all" ON public.subscriptions;

-- STEP 5: VERIFY RLS IS ENABLED ON PROBLEMATIC TABLES
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payment_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.plans ENABLE ROW LEVEL SECURITY;

-- STEP 6: GRANT SERVICE ROLE FULL ACCESS (bypasses RLS)
GRANT ALL ON public.users TO service_role;
GRANT ALL ON public.workspaces TO service_role;
GRANT ALL ON public.subscriptions TO service_role;
GRANT ALL ON public.payment_transactions TO service_role;
GRANT ALL ON public.profiles TO service_role;
GRANT ALL ON public.plans TO service_role;

-- NOTE: Properly scoped RLS policies are created in:
-- - 20260130_fix_duplicate_subscription_plans.sql (workspaces, subscriptions, payment_transactions)
-- - 20260130_comprehensive_security_fixes.sql (ICP tables, users)
-- - 134_fix_rls_performance.sql (profiles, foundations, bcm, etc.)
