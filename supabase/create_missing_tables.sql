-- Create missing subscription tables
-- Run this first before applying the function fix

-- Create subscription_plans table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly INTEGER NOT NULL, -- in paise
    price_annual INTEGER NOT NULL, -- in paise
    currency VARCHAR(3) DEFAULT 'INR',
    features JSONB DEFAULT '{}',
    limits JSONB DEFAULT '{}',
    sort_order INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_subscriptions table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES public.subscription_plans(id) ON DELETE RESTRICT,
    billing_cycle VARCHAR(10) NOT NULL CHECK (billing_cycle IN ('monthly', 'annual')),
    phonepe_order_id VARCHAR(100),
    amount_paid INTEGER NOT NULL, -- in paise
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired', 'pending')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    next_billing_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_onboarding table if it doesn't exist
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

-- Create plan_usage_limits table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.plan_usage_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES public.user_subscriptions(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    limit_value VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(subscription_id, metric_name)
);

-- Create subscription_events table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.subscription_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES public.user_subscriptions(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert basic subscription plans if they don't exist
INSERT INTO public.subscription_plans (slug, name, display_name, description, price_monthly, price_annual, currency, features, limits, sort_order, is_active)
VALUES
    ('ascent', 'Ascent', 'Ascent Plan', 'Perfect for small teams getting started', 500000, 5000000, 'INR', '{"campaigns": 3, "team_seats": 1, "moves_per_week": 3}', '{"moves_per_week": "3", "campaigns": "3", "team_seats": "1"}', 1, true),
    ('glide', 'Glide', 'Glide Plan', 'Ideal for growing businesses', 700000, 7000000, 'INR', '{"campaigns": -1, "team_seats": 5, "moves_per_week": -1}', '{"moves_per_week": "-1", "campaigns": "-1", "team_seats": "5"}', 2, true),
    ('soar', 'Soar', 'Soar Plan', 'Enterprise solution for large teams', 1000000, 10000000, 'INR', '{"campaigns": -1, "team_seats": -1, "moves_per_week": -1}', '{"moves_per_week": "-1", "campaigns": "-1", "team_seats": "-1"}', 3, true)
ON CONFLICT (slug) DO NOTHING;

-- Enable RLS
ALTER TABLE public.subscription_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_onboarding ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.plan_usage_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_events ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- subscription_plans - everyone can read active plans
CREATE POLICY "Anyone can view active subscription plans" ON public.subscription_plans
    FOR SELECT USING (is_active = true);

-- user_subscriptions - users can only see their own subscriptions
CREATE POLICY "Users can view their own subscriptions" ON public.user_subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own subscriptions" ON public.user_subscriptions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own subscriptions" ON public.user_subscriptions
    FOR UPDATE USING (auth.uid() = user_id);

-- user_onboarding - users can only see their own onboarding
CREATE POLICY "Users can view their own onboarding" ON public.user_onboarding
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own onboarding" ON public.user_onboarding
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own onboarding" ON public.user_onboarding
    FOR UPDATE USING (auth.uid() = user_id);

-- plan_usage_limits - users can only see their own usage limits
CREATE POLICY "Users can view their own usage limits" ON public.plan_usage_limits
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.user_subscriptions
            WHERE id = subscription_id AND user_id = auth.uid()
        )
    );

-- subscription_events - users can only see their own events
CREATE POLICY "Users can view their own subscription events" ON public.subscription_events
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.user_subscriptions
            WHERE id = subscription_id AND user_id = auth.uid()
        )
    );

-- Grant permissions
GRANT ALL ON public.subscription_plans TO authenticated;
GRANT ALL ON public.subscription_plans TO service_role;
GRANT ALL ON public.user_subscriptions TO authenticated;
GRANT ALL ON public.user_subscriptions TO service_role;
GRANT ALL ON public.user_onboarding TO authenticated;
GRANT ALL ON public.user_onboarding TO service_role;
GRANT ALL ON public.plan_usage_limits TO authenticated;
GRANT ALL ON public.plan_usage_limits TO service_role;
GRANT ALL ON public.subscription_events TO authenticated;
GRANT ALL ON public.subscription_events TO service_role;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON public.user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_plan_id ON public.user_subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON public.user_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_user_onboarding_user_id ON public.user_onboarding(user_id);
CREATE INDEX IF NOT EXISTS idx_plan_usage_limits_subscription_id ON public.plan_usage_limits(subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscription_events_subscription_id ON public.subscription_events(subscription_id);

-- Log table creation
DO $$
BEGIN
    RAISE NOTICE '✅ Created missing subscription tables';
    RAISE NOTICE '📊 Tables: subscription_plans, user_subscriptions, user_onboarding, plan_usage_limits, subscription_events';
    RAISE NOTICE '🔧 RLS policies and permissions applied';
    RAISE NOTICE '💰 Inserted basic subscription plans (Ascent, Glide, Soar)';
END $$;
