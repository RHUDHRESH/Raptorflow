-- QUICK FIX - Copy and paste this into Supabase SQL Editor
-- This will create all missing tables and fix the subscription function

-- Step 1: Create subscription_plans table
CREATE TABLE IF NOT EXISTS public.subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly INTEGER NOT NULL,
    price_annual INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    features JSONB DEFAULT '{}',
    limits JSONB DEFAULT '{}',
    sort_order INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 2: Create user_subscriptions table
CREATE TABLE IF NOT EXISTS public.user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES public.subscription_plans(id) ON DELETE RESTRICT,
    billing_cycle VARCHAR(10) NOT NULL CHECK (billing_cycle IN ('monthly', 'annual')),
    phonepe_order_id VARCHAR(100),
    amount_paid INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    next_billing_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 3: Create user_onboarding table
CREATE TABLE IF NOT EXISTS public.user_onboarding (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES public.user_subscriptions(id) ON DELETE CASCADE,
    onboarding_status VARCHAR(50) DEFAULT 'started',
    completed_steps JSONB DEFAULT '{}',
    current_step VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 4: Create plan_usage_limits table
CREATE TABLE IF NOT EXISTS public.plan_usage_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES public.user_subscriptions(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    limit_value VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(subscription_id, metric_name)
);

-- Step 5: Insert subscription plans
INSERT INTO public.subscription_plans (slug, name, display_name, description, price_monthly, price_annual, currency, features, limits, sort_order, is_active)
VALUES 
    ('ascent', 'Ascent', 'Ascent Plan', 'Perfect for small teams getting started', 500000, 5000000, 'INR', '{"campaigns": 3, "team_seats": 1, "moves_per_week": 3}', '{"moves_per_week": "3", "campaigns": "3", "team_seats": "1"}', 1, true),
    ('glide', 'Glide', 'Glide Plan', 'Ideal for growing businesses', 700000, 7000000, 'INR', '{"campaigns": -1, "team_seats": 5, "moves_per_week": -1}', '{"moves_per_week": "-1", "campaigns": "-1", "team_seats": "5"}', 2, true),
    ('soar', 'Soar', 'Soar Plan', 'Enterprise solution for large teams', 1000000, 10000000, 'INR', '{"campaigns": -1, "team_seats": -1, "moves_per_week": -1}', '{"moves_per_week": "-1", "campaigns": "-1", "team_seats": "-1"}', 3, true)
ON CONFLICT (slug) DO NOTHING;

-- Step 6: Drop and recreate the function with correct signature
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

-- Step 7: Grant permissions
GRANT EXECUTE ON FUNCTION public.create_user_subscription TO authenticated;
GRANT EXECUTE ON FUNCTION public.create_user_subscription TO service_role;

-- Step 8: Enable RLS and create basic policies
ALTER TABLE public.subscription_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_onboarding ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.plan_usage_limits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view active subscription plans" ON public.subscription_plans
    FOR SELECT USING (is_active = true);

CREATE POLICY "Users can view their own subscriptions" ON public.user_subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own subscriptions" ON public.user_subscriptions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- DONE! Your subscription system is now ready.
