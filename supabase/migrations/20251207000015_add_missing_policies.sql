-- =====================================================
-- MIGRATION 015: Add Missing RLS Policies
-- =====================================================

-- Tables with RLS enabled but no policies are inaccessible to users
-- Add basic policies for org-scoped access

-- Cohort Memberships (via cohort_id FK to cohorts)
CREATE POLICY cohort_memberships_org_access ON public.cohort_memberships
  FOR ALL
  USING (
    cohort_id IN (
      SELECT id FROM public.cohorts WHERE organization_id = ANY(get_user_org_ids())
    )
  );

-- Organization Invites
CREATE POLICY organization_invites_org_access ON public.organization_invites
  FOR ALL
  USING (organization_id = ANY(get_user_org_ids()));

-- Payment Mandates
CREATE POLICY payment_mandates_org_access ON public.payment_mandates
  FOR ALL
  USING (organization_id = ANY(get_user_org_ids()));

-- Scheduled Jobs (system-wide, admin-only)
CREATE POLICY scheduled_jobs_admin_access ON public.scheduled_jobs
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.organization_members
      WHERE user_id = auth.uid()
      AND role IN ('owner', 'admin')
      AND is_active = true
    )
  );

-- Storage Quotas
CREATE POLICY storage_quotas_org_access ON public.storage_quotas
  FOR ALL
  USING (organization_id = ANY(get_user_org_ids()));

-- Task Queue (system-wide, admin-only)
CREATE POLICY task_queue_admin_access ON public.task_queue
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.organization_members
      WHERE user_id = auth.uid()
      AND role IN ('owner', 'admin')
      AND is_active = true
    )
  );
