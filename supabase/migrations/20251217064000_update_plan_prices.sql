-- =====================================================
-- MIGRATION: Update plan monthly pricing (PhonePe charge amounts)
-- =====================================================

UPDATE public.plans
SET price_monthly_paise = 499900,
    updated_at = NOW()
WHERE code = 'starter';

UPDATE public.plans
SET price_monthly_paise = 699900,
    updated_at = NOW()
WHERE code = 'growth';

UPDATE public.plans
SET price_monthly_paise = 1199900,
    updated_at = NOW()
WHERE code = 'enterprise';
