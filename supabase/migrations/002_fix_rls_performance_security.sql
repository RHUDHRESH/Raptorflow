-- =====================================================
-- RAPTORFLOW DATABASE PERFORMANCE & SECURITY FIX
-- Migration: 002_fix_rls_performance_security
-- 
-- Fixes:
-- 1. RLS policies using auth.uid() directly (causes per-row re-evaluation)
-- 2. Functions with mutable search_path (security risk)
-- 3. Duplicate permissive SELECT policies (performance issue)
-- =====================================================

-- =====================================================
-- PART 1: FIX FUNCTION SEARCH PATHS
-- Setting search_path = '' ensures functions use fully qualified names
-- =====================================================

-- Fix: update_updated_at function
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER 
LANGUAGE plpgsql
SET search_path = ''
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

-- Fix: activate_plan function
CREATE OR REPLACE FUNCTION public.activate_plan(
  p_user_id UUID,
  p_plan TEXT,
  p_payment_id TEXT,
  p_amount INTEGER
)
RETURNS BOOLEAN 
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
  v_duration_days INTEGER;
BEGIN
  -- Set duration based on plan
  v_duration_days := CASE p_plan
    WHEN 'ascent' THEN 30
    WHEN 'glide' THEN 90
    WHEN 'soar' THEN 365 * 10 -- "Lifetime" = 10 years
    ELSE 30
  END;

  -- Update profile with plan info
  UPDATE public.profiles
  SET
    plan = p_plan,
    plan_status = 'active',
    plan_started_at = NOW(),
    plan_expires_at = NOW() + (v_duration_days || ' days')::INTERVAL,
    payment_status = 'completed',
    last_payment_id = p_payment_id,
    last_payment_amount = p_amount,
    last_payment_date = NOW()
  WHERE id = p_user_id;

  RETURN FOUND;
END;
$$;

-- Fix: handle_new_user function
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER 
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name'),
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$;

-- =====================================================
-- PART 2: FIX RLS POLICIES - PROFILES TABLE
-- Wrap auth.uid() in (SELECT ...) to prevent per-row re-evaluation
-- =====================================================

DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile" 
  ON public.profiles FOR SELECT 
  USING ((SELECT auth.uid()) = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile" 
  ON public.profiles FOR UPDATE 
  USING ((SELECT auth.uid()) = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
CREATE POLICY "Users can insert own profile" 
  ON public.profiles FOR INSERT 
  WITH CHECK ((SELECT auth.uid()) = id);

-- =====================================================
-- PART 3: FIX RLS POLICIES - PAYMENTS TABLE
-- =====================================================

DROP POLICY IF EXISTS "Users can view own payments" ON public.payments;
CREATE POLICY "Users can view own payments" 
  ON public.payments FOR SELECT 
  USING ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own payments" ON public.payments;
CREATE POLICY "Users can insert own payments" 
  ON public.payments FOR INSERT 
  WITH CHECK ((SELECT auth.uid()) = user_id);

-- =====================================================
-- PART 4: FIX RLS POLICIES - WORKSPACES TABLE
-- =====================================================

DROP POLICY IF EXISTS "Users can view own workspaces" ON public.workspaces;
CREATE POLICY "Users can view own workspaces" 
  ON public.workspaces FOR SELECT 
  USING (owner_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Users can update own workspaces" ON public.workspaces;
CREATE POLICY "Users can update own workspaces" 
  ON public.workspaces FOR UPDATE 
  USING (owner_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Users can insert own workspaces" ON public.workspaces;
CREATE POLICY "Users can insert own workspaces" 
  ON public.workspaces FOR INSERT 
  WITH CHECK (owner_id = (SELECT auth.uid()));

-- =====================================================
-- PART 5: FIX RLS POLICIES - SUBSCRIPTIONS TABLE
-- =====================================================

DROP POLICY IF EXISTS "Users can view own subscriptions" ON public.subscriptions;
CREATE POLICY "Users can view own subscriptions" 
  ON public.subscriptions FOR SELECT 
  USING (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Users can update own subscriptions" ON public.subscriptions;
CREATE POLICY "Users can update own subscriptions" 
  ON public.subscriptions FOR UPDATE 
  USING (user_id = (SELECT auth.uid()));

-- =====================================================
-- PART 6: FIX RLS POLICIES - USER_PROFILES TABLE
-- =====================================================

DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
CREATE POLICY "Users can view own profile" 
  ON public.user_profiles FOR SELECT 
  USING (id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
CREATE POLICY "Users can update own profile" 
  ON public.user_profiles FOR UPDATE 
  USING (id = (SELECT auth.uid()));

-- =====================================================
-- PART 7: FIX RLS POLICIES - BILLING_HISTORY TABLE
-- =====================================================

DROP POLICY IF EXISTS "Users can view their billing history" ON public.billing_history;
CREATE POLICY "Users can view their billing history" 
  ON public.billing_history FOR SELECT 
  USING (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Service can insert billing history" ON public.billing_history;
CREATE POLICY "Service can insert billing history" 
  ON public.billing_history FOR INSERT 
  WITH CHECK (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Service can update billing history" ON public.billing_history;
CREATE POLICY "Service can update billing history" 
  ON public.billing_history FOR UPDATE 
  USING (user_id = (SELECT auth.uid()));

-- =====================================================
-- PART 8: FIX RLS POLICIES - AUTOPAY TABLES
-- =====================================================

-- autopay_subscriptions
DROP POLICY IF EXISTS "Users can view their subscriptions" ON public.autopay_subscriptions;
CREATE POLICY "Users can view their subscriptions" 
  ON public.autopay_subscriptions FOR SELECT 
  USING (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Service can insert subscriptions" ON public.autopay_subscriptions;
CREATE POLICY "Service can insert subscriptions" 
  ON public.autopay_subscriptions FOR INSERT 
  WITH CHECK (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Service can update subscriptions" ON public.autopay_subscriptions;
CREATE POLICY "Service can update subscriptions" 
  ON public.autopay_subscriptions FOR UPDATE 
  USING (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Service can delete subscriptions" ON public.autopay_subscriptions;
CREATE POLICY "Service can delete subscriptions" 
  ON public.autopay_subscriptions FOR DELETE 
  USING (user_id = (SELECT auth.uid()));

-- autopay_payments
DROP POLICY IF EXISTS "Users can view their payment history" ON public.autopay_payments;
CREATE POLICY "Users can view their payment history" 
  ON public.autopay_payments FOR SELECT 
  USING (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Service can insert payments" ON public.autopay_payments;
CREATE POLICY "Service can insert payments" 
  ON public.autopay_payments FOR INSERT 
  WITH CHECK (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Service can update payments" ON public.autopay_payments;
CREATE POLICY "Service can update payments" 
  ON public.autopay_payments FOR UPDATE 
  USING (user_id = (SELECT auth.uid()));

-- =====================================================
-- PART 9: FIX RLS POLICIES - PROJECTS TABLE
-- =====================================================

DROP POLICY IF EXISTS "Users can view own projects" ON public.projects;
CREATE POLICY "Users can view own projects" 
  ON public.projects FOR SELECT 
  USING (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Users can insert own projects" ON public.projects;
CREATE POLICY "Users can insert own projects" 
  ON public.projects FOR INSERT 
  WITH CHECK (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Users can update own projects" ON public.projects;
CREATE POLICY "Users can update own projects" 
  ON public.projects FOR UPDATE 
  USING (user_id = (SELECT auth.uid()));

-- =====================================================
-- PART 10: FIX RLS POLICIES - INTAKE TABLE
-- =====================================================

DROP POLICY IF EXISTS "Users can view intake for own projects" ON public.intake;
CREATE POLICY "Users can view intake for own projects" 
  ON public.intake FOR SELECT 
  USING (EXISTS (
    SELECT 1 FROM public.projects p 
    WHERE p.id = intake.project_id 
    AND p.user_id = (SELECT auth.uid())
  ));

DROP POLICY IF EXISTS "Users can insert intake for own projects" ON public.intake;
CREATE POLICY "Users can insert intake for own projects" 
  ON public.intake FOR INSERT 
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.projects p 
    WHERE p.id = intake.project_id 
    AND p.user_id = (SELECT auth.uid())
  ));

DROP POLICY IF EXISTS "Users can update intake for own projects" ON public.intake;
CREATE POLICY "Users can update intake for own projects" 
  ON public.intake FOR UPDATE 
  USING (EXISTS (
    SELECT 1 FROM public.projects p 
    WHERE p.id = intake.project_id 
    AND p.user_id = (SELECT auth.uid())
  ));

-- =====================================================
-- PART 11: FIX RLS POLICIES - PLANS TABLE
-- =====================================================

DROP POLICY IF EXISTS "Users can view plans for own projects" ON public.plans;
CREATE POLICY "Users can view plans for own projects" 
  ON public.plans FOR SELECT 
  USING (EXISTS (
    SELECT 1 FROM public.projects p 
    WHERE p.id = plans.project_id 
    AND p.user_id = (SELECT auth.uid())
  ));

DROP POLICY IF EXISTS "Users can insert plans for own projects" ON public.plans;
CREATE POLICY "Users can insert plans for own projects" 
  ON public.plans FOR INSERT 
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.projects p 
    WHERE p.id = plans.project_id 
    AND p.user_id = (SELECT auth.uid())
  ));

DROP POLICY IF EXISTS "Users can update plans for own projects" ON public.plans;
CREATE POLICY "Users can update plans for own projects" 
  ON public.plans FOR UPDATE 
  USING (EXISTS (
    SELECT 1 FROM public.projects p 
    WHERE p.id = plans.project_id 
    AND p.user_id = (SELECT auth.uid())
  ));

-- =====================================================
-- PART 12: FIX RLS POLICIES - ONBOARDING TABLES
-- =====================================================

DROP POLICY IF EXISTS "Users can view own analyses" ON public.onboarding_analyses;
CREATE POLICY "Users can view own analyses" 
  ON public.onboarding_analyses FOR SELECT 
  USING (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Users can insert own analyses" ON public.onboarding_analyses;
CREATE POLICY "Users can insert own analyses" 
  ON public.onboarding_analyses FOR INSERT 
  WITH CHECK (user_id = (SELECT auth.uid()));

-- =====================================================
-- PART 13: FIX RLS POLICIES - POSITIONING BLUEPRINTS TABLE
-- =====================================================

DROP POLICY IF EXISTS "Users can view own blueprints" ON public.positioning_blueprints;
CREATE POLICY "Users can view own blueprints" 
  ON public.positioning_blueprints FOR SELECT 
  USING (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Users can insert own blueprints" ON public.positioning_blueprints;
CREATE POLICY "Users can insert own blueprints" 
  ON public.positioning_blueprints FOR INSERT 
  WITH CHECK (user_id = (SELECT auth.uid()));

-- =====================================================
-- PART 14: FIX DUPLICATE SELECT POLICIES ON WORKSPACE TABLES
-- Remove redundant "view" policies where "manage" already covers SELECT
-- =====================================================

-- assets table
DROP POLICY IF EXISTS "Workspace members can view assets" ON public.assets;
-- Keep only "Workspace members can manage assets" for SELECT

-- capability_nodes table
DROP POLICY IF EXISTS "Workspace members can view capability_nodes" ON public.capability_nodes;

-- lines_of_operation table
DROP POLICY IF EXISTS "Workspace members can view lines_of_operation" ON public.lines_of_operation;

-- maneuver_prerequisites table
DROP POLICY IF EXISTS "Workspace members can view maneuver_prerequisites" ON public.maneuver_prerequisites;

-- move_anomalies table
DROP POLICY IF EXISTS "Workspace members can view move_anomalies" ON public.move_anomalies;

-- move_logs table
DROP POLICY IF EXISTS "Workspace members can view move_logs" ON public.move_logs;

-- moves table
DROP POLICY IF EXISTS "Workspace members can view moves" ON public.moves;

-- quest_milestones table
DROP POLICY IF EXISTS "Workspace members can view quest_milestones" ON public.quest_milestones;

-- quest_moves table
DROP POLICY IF EXISTS "Workspace members can view quest_moves" ON public.quest_moves;

-- quests table
DROP POLICY IF EXISTS "Workspace members can view quests" ON public.quests;

-- sprints table
DROP POLICY IF EXISTS "Workspace members can view sprints" ON public.sprints;

-- =====================================================
-- DONE: All performance and security issues fixed
-- =====================================================

