-- =====================================================
-- MIGRATION 009: Row Level Security Policies
-- =====================================================

-- Enable RLS
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.organization_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.organization_invites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payment_mandates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cohorts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cohort_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.storage_quotas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scheduled_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.task_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.metric_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.metrics ENABLE ROW LEVEL SECURITY;

-- Helper: Get user's org IDs
CREATE OR REPLACE FUNCTION public.get_user_org_ids()
RETURNS UUID[] AS $$
  SELECT ARRAY_AGG(organization_id)
  FROM public.organization_members
  WHERE user_id = auth.uid() AND is_active = true AND removed_at IS NULL;
$$ LANGUAGE sql STABLE SECURITY DEFINER;

-- Helper: Check org membership
CREATE OR REPLACE FUNCTION public.is_org_member(org_id UUID)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.organization_members
    WHERE organization_id = org_id AND user_id = auth.uid() AND is_active = true AND removed_at IS NULL
  );
$$ LANGUAGE sql STABLE SECURITY DEFINER;

-- Helper: Check org admin
CREATE OR REPLACE FUNCTION public.is_org_admin(org_id UUID)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.organization_members
    WHERE organization_id = org_id AND user_id = auth.uid() AND role IN ('owner', 'admin') AND is_active = true AND removed_at IS NULL
  );
$$ LANGUAGE sql STABLE SECURITY DEFINER;

-- Profiles
CREATE POLICY "profiles_select_own" ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "profiles_update_own" ON public.profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "profiles_insert_own" ON public.profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- Organizations
CREATE POLICY "organizations_select" ON public.organizations FOR SELECT USING (public.is_org_member(id) OR deleted_at IS NULL);
CREATE POLICY "organizations_update" ON public.organizations FOR UPDATE USING (public.is_org_admin(id));

-- Organization members
CREATE POLICY "org_members_select" ON public.organization_members FOR SELECT USING (public.is_org_member(organization_id));
CREATE POLICY "org_members_insert" ON public.organization_members FOR INSERT WITH CHECK (public.is_org_admin(organization_id));
CREATE POLICY "org_members_update" ON public.organization_members FOR UPDATE USING (public.is_org_admin(organization_id));
CREATE POLICY "org_members_delete" ON public.organization_members FOR DELETE USING (public.is_org_admin(organization_id));

-- Plans (public)
CREATE POLICY "plans_select" ON public.plans FOR SELECT USING (is_active = true);

-- Subscriptions
CREATE POLICY "subscriptions_select" ON public.subscriptions FOR SELECT USING (public.is_org_member(organization_id));
CREATE POLICY "subscriptions_insert" ON public.subscriptions FOR INSERT WITH CHECK (public.is_org_admin(organization_id));
CREATE POLICY "subscriptions_update" ON public.subscriptions FOR UPDATE USING (public.is_org_admin(organization_id));

-- Invoices, Payments
CREATE POLICY "invoices_select" ON public.invoices FOR SELECT USING (public.is_org_member(organization_id));
CREATE POLICY "payments_select" ON public.payments FOR SELECT USING (public.is_org_member(organization_id));
CREATE POLICY "payments_insert" ON public.payments FOR INSERT WITH CHECK (public.is_org_admin(organization_id));

-- Cohorts, Campaigns
CREATE POLICY "cohorts_select" ON public.cohorts FOR SELECT USING (public.is_org_member(organization_id));
CREATE POLICY "cohorts_insert" ON public.cohorts FOR INSERT WITH CHECK (public.is_org_member(organization_id));
CREATE POLICY "cohorts_update" ON public.cohorts FOR UPDATE USING (public.is_org_member(organization_id));
CREATE POLICY "cohorts_delete" ON public.cohorts FOR DELETE USING (public.is_org_admin(organization_id));

CREATE POLICY "campaigns_select" ON public.campaigns FOR SELECT USING (public.is_org_member(organization_id));
CREATE POLICY "campaigns_insert" ON public.campaigns FOR INSERT WITH CHECK (public.is_org_member(organization_id));
CREATE POLICY "campaigns_update" ON public.campaigns FOR UPDATE USING (public.is_org_member(organization_id));
CREATE POLICY "campaigns_delete" ON public.campaigns FOR DELETE USING (public.is_org_admin(organization_id));

-- Assets
CREATE POLICY "assets_select" ON public.assets FOR SELECT USING (public.is_org_member(organization_id));
CREATE POLICY "assets_insert" ON public.assets FOR INSERT WITH CHECK (public.is_org_member(organization_id));
CREATE POLICY "assets_delete" ON public.assets FOR DELETE USING (public.is_org_member(organization_id));

-- Audit & Metrics
CREATE POLICY "audit_select" ON public.audit_logs FOR SELECT USING (public.is_org_admin(organization_id));
CREATE POLICY "metrics_select" ON public.metrics FOR SELECT USING (public.is_org_member(organization_id));
CREATE POLICY "metric_defs_select" ON public.metric_definitions FOR SELECT USING (is_active = true);
