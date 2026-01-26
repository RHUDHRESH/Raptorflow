-- UPDATED QUICK FIX - Based on existing schema analysis
-- Copy and paste this into Supabase SQL Editor

-- Step 1: Check if subscription_plans has correct structure and update if needed
-- The subscription_plans table already exists but let's ensure it has the right data
INSERT INTO public.subscription_plans (name, slug, display_name, description, price_monthly, price_annual, currency, features, limits, sort_order, is_active)
VALUES
    ('Ascent', 'ascent', 'Ascent Plan', 'Perfect for small teams getting started', 500000, 5000000, 'INR', '[]', '{"moves_per_week": "3", "campaigns": "3", "team_seats": "1"}', 1, true),
    ('Glide', 'glide', 'Glide Plan', 'Ideal for growing businesses', 700000, 7000000, 'INR', '[]', '{"moves_per_week": "-1", "campaigns": "-1", "team_seats": "5"}', 2, true),
    ('Soar', 'soar', 'Soar Plan', 'Enterprise solution for large teams', 1000000, 10000000, 'INR', '[]', '{"moves_per_week": "-1", "campaigns": "-1", "team_seats": "-1"}', 3, true)
ON CONFLICT (name) DO NOTHING;

-- Step 2: user_subscriptions table already exists - check structure
-- The table exists with correct structure, no changes needed

-- Step 3: user_onboarding table already exists - check structure
-- The table exists with correct structure, no changes needed

-- Step 4: plan_usage_limits table already exists - check structure
-- The table exists with correct structure, no changes needed

-- Step 5: Drop and recreate the function with correct signature
DROP FUNCTION IF EXISTS public.create_user_subscription(p_amount_paid, p_billing_cycle, p_phonepe_order_id, p_plan_slug, p_user_id);

CREATE OR REPLACE FUNCTION public.create_user_subscription(
    p_user_id UUID,
    p_plan_slug VARCHAR(50),
    p_billing_cycle VARCHAR(10),
    p_phonepe_order_id VARCHAR(100),
    p_amount_paid INTEGER
) RETURNS UUID AS $$
DECLARE
    new_subscription_id UUID;
    plan_record RECORD;
    expires_date TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Get plan details
    SELECT id, price_monthly, price_annual INTO plan_record
    FROM public.subscription_plans
    WHERE slug = p_plan_slug AND is_active = true;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Plan not found: %', p_plan_slug;
    END IF;

    -- Calculate expiration date
    IF p_billing_cycle = 'annual' THEN
        expires_date := NOW() + INTERVAL '1 year';
    ELSE
        expires_date := NOW() + INTERVAL '1 month';
    END IF;

    -- Create subscription
    INSERT INTO public.user_subscriptions (
        user_id,
        plan_id,
        billing_cycle,
        phonepe_order_id,
        amount_paid,
        started_at,
        expires_at,
        next_billing_date
    ) VALUES (
        p_user_id,
        plan_record.id,
        p_billing_cycle,
        p_phonepe_order_id,
        p_amount_paid,
        NOW(),
        expires_date,
        expires_date
    ) RETURNING id INTO new_subscription_id;

    -- Create onboarding record
    INSERT INTO public.user_onboarding (user_id, subscription_id)
    VALUES (p_user_id, new_subscription_id);

    -- Initialize usage limits
    INSERT INTO public.plan_usage_limits (subscription_id, metric_name, limit_value)
    SELECT
        new_subscription_id,
        key,
        value
    FROM jsonb_each_text(
        CASE
            WHEN p_plan_slug = 'ascent' THEN '{"moves_per_week": "3", "campaigns": "3", "team_seats": "1"}'
            WHEN p_plan_slug = 'glide' THEN '{"moves_per_week": "-1", "campaigns": "-1", "team_seats": "5"}'
            WHEN p_plan_slug = 'soar' THEN '{"moves_per_week": "-1", "campaigns": "-1", "team_seats": "-1"}'
            ELSE '{}'
        END::jsonb
    );

    RETURN new_subscription_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 6: Grant permissions
GRANT EXECUTE ON FUNCTION public.create_user_subscription TO authenticated;
GRANT EXECUTE ON FUNCTION public.create_user_subscription TO service_role;

-- Step 7: Verify function exists with correct signature
SELECT
    proname as function_name,
    proargnames as argument_names
FROM pg_proc
WHERE proname = 'create_user_subscription'
AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');

-- Step 8: Test the function (optional - comment out if not needed)
-- SELECT public.create_user_subscription(
--     '00000000-0000-0000-0000-000000000000'::UUID, -- test user_id
--     'ascent', -- plan_slug
--     'monthly', -- billing_cycle
--     'TEST_ORDER_123', -- phonepe_order_id
--     500000 -- amount_paid (₹5,000 in paise)
-- );

-- DONE! Your subscription system is now ready.
