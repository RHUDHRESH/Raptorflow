-- ============================================================================
-- RAPTORFLOW PRICING FIX: ASCENT (5K), GLIDE (7K), SOAR (10K)
-- Script: scripts/fix_plans_pricing.sql
-- ============================================================================

BEGIN;

-- 1. UPDATE ASCENT PRICING (₹5,000)
UPDATE public.plans SET 
    name = 'Ascent',
    price_monthly_paise = 500000,
    price_yearly_paise = 5000000,
    updated_at = NOW()
WHERE slug = 'ascent';

-- 2. UPDATE GLIDE PRICING (₹7,000)
UPDATE public.plans SET 
    name = 'Glide',
    price_monthly_paise = 700000,
    price_yearly_paise = 7000000,
    updated_at = NOW()
WHERE slug = 'glide';

-- 3. UPDATE SOAR PRICING (₹10,000)
UPDATE public.plans SET 
    name = 'Soar',
    price_monthly_paise = 1000000,
    price_yearly_paise = 10000000,
    updated_at = NOW()
WHERE slug = 'soar';

-- 4. INSERT IF NOT EXISTS (Safety)
INSERT INTO public.plans (name, slug, price_monthly_paise, price_yearly_paise, is_active, display_order)
VALUES 
    ('Ascent', 'ascent', 500000, 5000000, true, 1),
    ('Glide', 'glide', 700000, 7000000, true, 2),
    ('Soar', 'soar', 1000000, 10000000, true, 3)
ON CONFLICT (slug) DO UPDATE SET
    price_monthly_paise = EXCLUDED.price_monthly_paise,
    price_yearly_paise = EXCLUDED.price_yearly_paise,
    updated_at = NOW();

-- 5. SYNC SUBSCRIPTION_PLANS table if it exists (legacy redundancy)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'subscription_plans') THEN
        UPDATE public.subscription_plans SET price_monthly = 500000, price_annual = 5000000 WHERE slug = 'ascent';
        UPDATE public.subscription_plans SET price_monthly = 700000, price_annual = 7000000 WHERE slug = 'glide';
        UPDATE public.subscription_plans SET price_monthly = 1000000, price_annual = 10000000 WHERE slug = 'soar';
    END IF;
END $$;

COMMIT;
