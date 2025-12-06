-- Fix Function Search Path (Security Warning)
ALTER FUNCTION public.update_updated_at_column() SET search_path = '';

-- Fix RLS InitPlan and Multiple Permissive Policies (Performance/Security Warnings)

-- 1. onboarding_intake
-- Combine SELECT policies for 'public' (Auth and Anon)
DROP POLICY IF EXISTS "Sales reps can view assigned intake" ON public.onboarding_intake;
DROP POLICY IF EXISTS "Users can view own intake" ON public.onboarding_intake;
DROP POLICY IF EXISTS "View onboarding intake" ON public.onboarding_intake;
CREATE POLICY "View onboarding intake" ON public.onboarding_intake
FOR SELECT
TO public
USING (
  ((select auth.uid()) = user_id) OR ((select auth.uid()) = sales_rep_id)
);

-- Combine UPDATE policies for 'public'
DROP POLICY IF EXISTS "Sales reps can update assigned intake" ON public.onboarding_intake;
DROP POLICY IF EXISTS "Users can update own intake" ON public.onboarding_intake;
DROP POLICY IF EXISTS "Update onboarding intake" ON public.onboarding_intake;
CREATE POLICY "Update onboarding intake" ON public.onboarding_intake
FOR UPDATE
TO public
USING (
  ((select auth.uid()) = user_id) OR ((select auth.uid()) = sales_rep_id)
);

-- Fix INSERT policy performance (wrap auth.uid())
DROP POLICY IF EXISTS "Users can insert own intake" ON public.onboarding_intake;
CREATE POLICY "Users can insert own intake" ON public.onboarding_intake
FOR INSERT
TO public
WITH CHECK (
  (select auth.uid()) = user_id
);

-- 2. agent_executions
-- Fix SELECT policy performance
DROP POLICY IF EXISTS "Users can view own agent executions" ON public.agent_executions;
CREATE POLICY "Users can view own agent executions" ON public.agent_executions
FOR SELECT
TO public
USING (
  EXISTS (
    SELECT 1 FROM onboarding_intake
    WHERE onboarding_intake.id = agent_executions.intake_id
    AND onboarding_intake.user_id = (select auth.uid())
  )
);

-- Fix INSERT policy performance
DROP POLICY IF EXISTS "Users can insert own agent executions" ON public.agent_executions;
CREATE POLICY "Users can insert own agent executions" ON public.agent_executions
FOR INSERT
TO public
WITH CHECK (
  EXISTS (
    SELECT 1 FROM onboarding_intake
    WHERE onboarding_intake.id = agent_executions.intake_id
    AND onboarding_intake.user_id = (select auth.uid())
  )
);

-- 3. shared_links
-- Fix Multiple Permissive Policies for SELECT
-- Existing 'Anyone can read shared links by token' is TRUE, which overrides 'Users can view own shared links'.
-- We drop the redundant user policy to clear the warning.
DROP POLICY IF EXISTS "Users can view own shared links" ON public.shared_links;

-- Fix INSERT policy performance
DROP POLICY IF EXISTS "Users can insert shared links for own intake" ON public.shared_links;
CREATE POLICY "Users can insert shared links for own intake" ON public.shared_links
FOR INSERT
TO public
WITH CHECK (
  EXISTS (
    SELECT 1 FROM onboarding_intake
    WHERE onboarding_intake.id = shared_links.intake_id
    AND (
      onboarding_intake.user_id = (select auth.uid()) OR
      onboarding_intake.sales_rep_id = (select auth.uid())
    )
  )
);

-- Fix Unindexed Foreign Keys (Performance Info)
CREATE INDEX IF NOT EXISTS idx_maneuver_prereq_required_cap ON public.maneuver_prerequisites(required_capability_id);
CREATE INDEX IF NOT EXISTS idx_moves_line_of_op ON public.moves(line_of_operation_id);
CREATE INDEX IF NOT EXISTS idx_moves_maneuver_type ON public.moves(maneuver_type_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_analyses_user ON public.onboarding_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_intake_sales_rep ON public.onboarding_intake(sales_rep_id);
CREATE INDEX IF NOT EXISTS idx_plans_project ON public.plans(project_id);
CREATE INDEX IF NOT EXISTS idx_positioning_blueprints_analysis ON public.positioning_blueprints(analysis_id);
CREATE INDEX IF NOT EXISTS idx_positioning_blueprints_user ON public.positioning_blueprints(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_user ON public.projects(user_id);
CREATE INDEX IF NOT EXISTS idx_shared_links_sales_rep ON public.shared_links(sales_rep_id);
