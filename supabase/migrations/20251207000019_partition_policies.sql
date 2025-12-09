-- =====================================================
-- MIGRATION 019: Add RLS Policies to Partition Tables
-- =====================================================

-- Partitioned tables inherit RLS enablement but NOT policies
-- We must explicitly create policies on each partition

-- ========== AUDIT LOGS PARTITIONS ==========
-- Policies inherit from parent audit_logs table

CREATE POLICY audit_logs_org_access_2025_q1 ON public.audit_logs_2025_q1
  FOR ALL
  USING (organization_id = ANY(get_user_org_ids()));

CREATE POLICY audit_logs_org_access_2025_q2 ON public.audit_logs_2025_q2
  FOR ALL
  USING (organization_id = ANY(get_user_org_ids()));

CREATE POLICY audit_logs_org_access_2025_q3 ON public.audit_logs_2025_q3
  FOR ALL
  USING (organization_id = ANY(get_user_org_ids()));

CREATE POLICY audit_logs_org_access_2025_q4 ON public.audit_logs_2025_q4
  FOR ALL
  USING (organization_id = ANY(get_user_org_ids()));

CREATE POLICY audit_logs_org_access_default ON public.audit_logs_default
  FOR ALL
  USING (organization_id = ANY(get_user_org_ids()));

-- ========== ACTIVITY EVENTS PARTITIONS ==========

CREATE POLICY activity_events_org_access_2025_q1 ON public.activity_events_2025_q1
  FOR ALL
  USING (organization_id = ANY(get_user_org_ids()));

CREATE POLICY activity_events_org_access_2025_q2 ON public.activity_events_2025_q2
  FOR ALL
  USING (organization_id = ANY(get_user_org_ids()));

CREATE POLICY activity_events_org_access_default ON public.activity_events_default
  FOR ALL
  USING (organization_id = ANY(get_user_org_ids()));

-- ========== JOB EXECUTIONS PARTITIONS ==========
-- Job executions are linked to scheduled_jobs which don't have org_id
-- Use admin-only access pattern

CREATE POLICY job_executions_admin_access_2025_q1 ON public.job_executions_2025_q1
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.organization_members
      WHERE user_id = (SELECT auth.uid())
      AND role IN ('owner', 'admin')
      AND is_active = true
    )
  );

CREATE POLICY job_executions_admin_access_default ON public.job_executions_default
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.organization_members
      WHERE user_id = (SELECT auth.uid())
      AND role IN ('owner', 'admin')
      AND is_active = true
    )
  );

-- ========== METRICS PARTITIONS ==========

CREATE POLICY metrics_org_access_2025_q1 ON public.metrics_2025_q1
  FOR ALL
  USING (organization_id = ANY(get_user_org_ids()));

CREATE POLICY metrics_org_access_2025_q2 ON public.metrics_2025_q2
  FOR ALL
  USING (organization_id = ANY(get_user_org_ids()));

CREATE POLICY metrics_org_access_default ON public.metrics_default
  FOR ALL
  USING (organization_id = ANY(get_user_org_ids()));
