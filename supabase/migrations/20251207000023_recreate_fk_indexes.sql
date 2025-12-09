-- =====================================================
-- MIGRATION 023: Recreate Foreign Key Indexes
-- =====================================================
-- Migration 021 dropped FK indexes. This migration recreates them.
-- https://supabase.com/docs/guides/database/database-linter?lint=0001_unindexed_foreign_keys

-- Activity Events (parent + partitions)
CREATE INDEX IF NOT EXISTS idx_activity_events_organization_id ON public.activity_events(organization_id);
CREATE INDEX IF NOT EXISTS idx_activity_events_2025_q1_organization_id ON public.activity_events_2025_q1(organization_id);
CREATE INDEX IF NOT EXISTS idx_activity_events_2025_q2_organization_id ON public.activity_events_2025_q2(organization_id);
CREATE INDEX IF NOT EXISTS idx_activity_events_default_organization_id ON public.activity_events_default(organization_id);

-- Assets
CREATE INDEX IF NOT EXISTS idx_assets_uploaded_by ON public.assets(uploaded_by);

-- Audit Logs (parent + partitions) - user_id
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_2025_q1_user_id ON public.audit_logs_2025_q1(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_2025_q2_user_id ON public.audit_logs_2025_q2(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_2025_q3_user_id ON public.audit_logs_2025_q3(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_2025_q4_user_id ON public.audit_logs_2025_q4(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_default_user_id ON public.audit_logs_default(user_id);

-- Campaigns
CREATE INDEX IF NOT EXISTS idx_campaigns_created_by ON public.campaigns(created_by);

-- Cohorts
CREATE INDEX IF NOT EXISTS idx_cohorts_created_by ON public.cohorts(created_by);

-- Invoices
CREATE INDEX IF NOT EXISTS idx_invoices_subscription_id ON public.invoices(subscription_id);

-- Job Executions (parent + partitions)
CREATE INDEX IF NOT EXISTS idx_job_executions_job_id ON public.job_executions(job_id);
CREATE INDEX IF NOT EXISTS idx_job_executions_2025_q1_job_id ON public.job_executions_2025_q1(job_id);
CREATE INDEX IF NOT EXISTS idx_job_executions_default_job_id ON public.job_executions_default(job_id);

-- Metrics (parent + partitions) - metric_id
CREATE INDEX IF NOT EXISTS idx_metrics_metric_id ON public.metrics(metric_id);
CREATE INDEX IF NOT EXISTS idx_metrics_2025_q1_metric_id ON public.metrics_2025_q1(metric_id);
CREATE INDEX IF NOT EXISTS idx_metrics_2025_q2_metric_id ON public.metrics_2025_q2(metric_id);
CREATE INDEX IF NOT EXISTS idx_metrics_default_metric_id ON public.metrics_default(metric_id);

-- Organization Invites
CREATE INDEX IF NOT EXISTS idx_organization_invites_invited_by ON public.organization_invites(invited_by);
CREATE INDEX IF NOT EXISTS idx_organization_invites_organization_id ON public.organization_invites(organization_id);

-- Organization Members
CREATE INDEX IF NOT EXISTS idx_organization_members_invited_by ON public.organization_members(invited_by);

-- Payment Mandates
CREATE INDEX IF NOT EXISTS idx_payment_mandates_organization_id ON public.payment_mandates(organization_id);
CREATE INDEX IF NOT EXISTS idx_payment_mandates_subscription_id ON public.payment_mandates(subscription_id);

-- Payments
CREATE INDEX IF NOT EXISTS idx_payments_invoice_id ON public.payments(invoice_id);
CREATE INDEX IF NOT EXISTS idx_payments_subscription_id ON public.payments(subscription_id);

-- Subscriptions
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_id ON public.subscriptions(plan_id);
