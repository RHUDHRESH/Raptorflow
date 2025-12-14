-- =====================================================
-- MIGRATION 012: Seed Data
-- =====================================================

-- Plans
INSERT INTO public.plans (code, name, description, price_monthly_paise, price_yearly_paise, cohort_limit, member_limit, storage_limit_mb, features, is_featured, sort_order) VALUES
('free', 'Free', 'Get started for free', 0, 0, 1, 1, 100, '["1 cohort", "1 member", "100MB storage"]', false, 0),
('starter', 'Starter', 'For small teams', 500000, 5000000, 5, 3, 1000, '["5 cohorts", "3 members", "1GB storage", "Email support"]', false, 1),
('growth', 'Growth', 'For growing businesses', 700000, 7000000, 20, 10, 10000, '["20 cohorts", "10 members", "10GB storage", "Priority support", "API access"]', true, 2),
('enterprise', 'Enterprise', 'For large organizations', 1000000, 10000000, 100, 50, 100000, '["Unlimited cohorts", "50 members", "100GB storage", "Dedicated support", "SSO"]', false, 3)
ON CONFLICT (code) DO UPDATE SET
  price_monthly_paise = EXCLUDED.price_monthly_paise,
  cohort_limit = EXCLUDED.cohort_limit,
  features = EXCLUDED.features;

-- Metric definitions
INSERT INTO public.metric_definitions (code, name, description, unit, aggregation) VALUES
('page_views', 'Page Views', 'Number of page views', 'count', 'sum'),
('sessions', 'Sessions', 'Number of user sessions', 'count', 'sum'),
('cohort_size', 'Cohort Size', 'Number of members in cohort', 'count', 'max'),
('campaign_reach', 'Campaign Reach', 'Users reached by campaign', 'count', 'sum'),
('storage_used', 'Storage Used', 'Storage used in bytes', 'bytes', 'max')
ON CONFLICT (code) DO NOTHING;

-- Grants
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO service_role;
GRANT SELECT ON public.plans TO anon;
GRANT SELECT ON public.metric_definitions TO anon;
