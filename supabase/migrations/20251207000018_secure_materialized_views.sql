-- =====================================================
-- MIGRATION 018: Secure Materialized Views
-- =====================================================

-- Materialized views contain aggregated sensitive data (revenue, usage)
-- They should only be accessible to server-side code (service_role), not clients

-- Revoke public access from subscription stats
REVOKE ALL ON public.mv_subscription_stats FROM anon;
REVOKE ALL ON public.mv_subscription_stats FROM authenticated;
GRANT SELECT ON public.mv_subscription_stats TO service_role;

-- Revoke public access from org metrics
REVOKE ALL ON public.mv_org_metrics FROM anon;
REVOKE ALL ON public.mv_org_metrics FROM authenticated;
GRANT SELECT ON public.mv_org_metrics TO service_role;

-- Note: Applications must now query these views via backend API
-- Direct PostgREST API calls from clients will fail (403 Forbidden)
