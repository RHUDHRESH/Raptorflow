-- =====================================================
-- MIGRATION 022: Optimize Admin RLS Policies
-- =====================================================
-- Fix auth_rls_initplan linter warnings by wrapping auth.uid() in SELECT
-- This prevents per-row re-evaluation of auth functions

-- ========== SCHEDULED JOBS ==========
DROP POLICY IF EXISTS scheduled_jobs_admin_access ON public.scheduled_jobs;
CREATE POLICY scheduled_jobs_admin_access ON public.scheduled_jobs
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.organization_members
      WHERE user_id = (SELECT auth.uid())
      AND role IN ('owner', 'admin')
      AND is_active = true
    )
  );

-- ========== TASK QUEUE ==========
DROP POLICY IF EXISTS task_queue_admin_access ON public.task_queue;
CREATE POLICY task_queue_admin_access ON public.task_queue
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.organization_members
      WHERE user_id = (SELECT auth.uid())
      AND role IN ('owner', 'admin')
      AND is_active = true
    )
  );
