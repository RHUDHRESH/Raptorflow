-- =====================================================
-- MIGRATION 011: Materialized Views
-- =====================================================

-- Subscription stats
CREATE MATERIALIZED VIEW public.mv_subscription_stats AS
SELECT 
  p.code as plan_code,
  s.status,
  COUNT(*) as count,
  SUM(s.amount_paise) as total_mrr_paise
FROM public.subscriptions s
JOIN public.plans p ON s.plan_id = p.id
WHERE s.deleted_at IS NULL
GROUP BY p.code, s.status;

CREATE UNIQUE INDEX idx_mv_subscription_stats ON public.mv_subscription_stats(plan_code, status);

-- Org metrics
CREATE MATERIALIZED VIEW public.mv_org_metrics AS
SELECT 
  o.id as organization_id,
  o.name,
  COUNT(DISTINCT om.user_id) as member_count,
  COUNT(DISTINCT c.id) as cohort_count,
  COUNT(DISTINCT ca.id) as campaign_count
FROM public.organizations o
LEFT JOIN public.organization_members om ON o.id = om.organization_id AND om.is_active = true
LEFT JOIN public.cohorts c ON o.id = c.organization_id AND c.deleted_at IS NULL
LEFT JOIN public.campaigns ca ON o.id = ca.organization_id AND ca.deleted_at IS NULL
WHERE o.deleted_at IS NULL
GROUP BY o.id, o.name;

CREATE UNIQUE INDEX idx_mv_org_metrics ON public.mv_org_metrics(organization_id);

-- Refresh function
CREATE OR REPLACE FUNCTION public.refresh_materialized_views()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_subscription_stats;
  REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_org_metrics;
END;
$$ LANGUAGE plpgsql;
