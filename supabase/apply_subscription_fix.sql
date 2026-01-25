-- Apply subscription function fix
-- Run this script directly in Supabase SQL Editor

-- Drop existing function if it exists with wrong signature
DROP FUNCTION IF EXISTS public.create_user_subscription(p_amount_paid, p_billing_cycle, p_phonepe_order_id, p_plan_slug, p_user_id);

-- Create the function with correct parameter order matching frontend call
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

-- Grant permissions
GRANT EXECUTE ON FUNCTION public.create_user_subscription TO authenticated;
GRANT EXECUTE ON FUNCTION public.create_user_subscription TO service_role;

-- Verify function exists with correct signature
SELECT
    proname as function_name,
    proargtypes as argument_types,
    proargnames as argument_names
FROM pg_proc
WHERE proname = 'create_user_subscription'
AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');

-- Test the function (optional - comment out if not needed)
-- SELECT public.create_user_subscription(
--     '00000000-0000-0000-0000-000000000000'::UUID, -- test user_id
--     'ascent', -- plan_slug
--     'monthly', -- billing_cycle
--     'TEST_ORDER_123', -- phonepe_order_id
--     500000 -- amount_paid (₹5,000 in paise)
-- );
