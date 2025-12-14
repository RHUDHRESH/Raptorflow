-- =====================================================
-- MIGRATION 000: WIPE CLEAN (Fresh Start)
-- =====================================================

-- Drop Materialized Views
DROP MATERIALIZED VIEW IF EXISTS public.mv_subscription_stats CASCADE;
DROP MATERIALIZED VIEW IF EXISTS public.mv_org_metrics CASCADE;

-- Drop Tables (Order matters for FKs, using CASCADE handles most)
DROP TABLE IF EXISTS public.metrics CASCADE;
DROP TABLE IF EXISTS public.metric_definitions CASCADE;
DROP TABLE IF EXISTS public.task_queue CASCADE;
DROP TABLE IF EXISTS public.job_executions CASCADE;
DROP TABLE IF EXISTS public.scheduled_jobs CASCADE;
DROP TABLE IF EXISTS public.activity_events CASCADE;
DROP TABLE IF EXISTS public.audit_logs CASCADE;
DROP TABLE IF EXISTS public.storage_quotas CASCADE;
DROP TABLE IF EXISTS public.assets CASCADE;
DROP TABLE IF EXISTS public.campaigns CASCADE;
DROP TABLE IF EXISTS public.cohort_memberships CASCADE;
DROP TABLE IF EXISTS public.cohorts CASCADE;
DROP TABLE IF EXISTS public.payments CASCADE;
DROP TABLE IF EXISTS public.invoices CASCADE;
DROP TABLE IF EXISTS public.payment_mandates CASCADE;
DROP TABLE IF EXISTS public.subscriptions CASCADE;
DROP TABLE IF EXISTS public.plans CASCADE;
DROP TABLE IF EXISTS public.organization_invites CASCADE;
DROP TABLE IF EXISTS public.organization_members CASCADE;
DROP TABLE IF EXISTS public.profiles CASCADE;
DROP TABLE IF EXISTS public.organizations CASCADE;

-- Drop Types (Enums)
DROP TYPE IF EXISTS public.org_role CASCADE;
DROP TYPE IF EXISTS public.plan_type CASCADE;
DROP TYPE IF EXISTS public.subscription_status CASCADE;
DROP TYPE IF EXISTS public.payment_status CASCADE;
DROP TYPE IF EXISTS public.payment_method_type CASCADE;
DROP TYPE IF EXISTS public.mandate_status CASCADE;
DROP TYPE IF EXISTS public.invoice_status CASCADE;
DROP TYPE IF EXISTS public.campaign_status CASCADE;
DROP TYPE IF EXISTS public.job_status CASCADE;
DROP TYPE IF EXISTS public.audit_action CASCADE;

-- Drop Domains (Fix for partial wipes)
DROP DOMAIN IF EXISTS public.amount_paise CASCADE;
DROP DOMAIN IF EXISTS public.percentage CASCADE;
DROP DOMAIN IF EXISTS public.email_address CASCADE;
DROP DOMAIN IF EXISTS public.indian_phone CASCADE;
DROP DOMAIN IF EXISTS public.url_string CASCADE;

-- Drop Functions
DROP FUNCTION IF EXISTS public.get_user_org_ids() CASCADE;
DROP FUNCTION IF EXISTS public.is_org_member(uuid) CASCADE;
DROP FUNCTION IF EXISTS public.is_org_admin(uuid) CASCADE;
DROP FUNCTION IF EXISTS public.update_updated_at() CASCADE;
DROP FUNCTION IF EXISTS public.handle_new_user() CASCADE;
DROP FUNCTION IF EXISTS public.update_storage_quota() CASCADE;
DROP FUNCTION IF EXISTS public.refresh_materialized_views() CASCADE;

-- Note: We do NOT drop extensions to avoid path issues
