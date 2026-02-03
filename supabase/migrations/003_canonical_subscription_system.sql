-- ============================================
-- CANONICAL SUBSCRIPTION SYSTEM MIGRATION
-- Creates subscription plans and user subscriptions
-- Date: 2026-01-30
-- ============================================

BEGIN;

-- ============================================
-- SUBSCRIPTION_PLANS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE CHECK (name IN ('Ascent', 'Glide', 'Soar')),
    slug VARCHAR(50) NOT NULL UNIQUE CHECK (slug IN ('ascent', 'glide', 'soar')),
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly INTEGER NOT NULL CHECK (price_monthly > 0),
    price_annual INTEGER NOT NULL CHECK (price_annual > 0),
    currency VARCHAR(3) DEFAULT 'INR',
    features JSONB DEFAULT '[]',
    limits JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subscription plans indexes
CREATE INDEX IF NOT EXISTS idx_subscription_plans_name ON public.subscription_plans(name);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_slug ON public.subscription_plans(slug);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_active ON public.subscription_plans(is_active);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_sort_order ON public.subscription_plans(sort_order);

-- Subscription plans updated_at trigger
CREATE OR REPLACE FUNCTION public.update_subscription_plans_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER subscription_plans_updated_at
    BEFORE UPDATE ON public.subscription_plans
    FOR EACH ROW
    EXECUTE FUNCTION public.update_subscription_plans_updated_at();

-- Insert default plans
INSERT INTO public.subscription_plans (name, slug, display_name, description, price_monthly, price_annual, features, limits, sort_order)
VALUES 
    (
        'Ascent',
        'ascent',
        'Ascent Plan',
        'Perfect for getting started with ICP profiling',
        500000,
        5000000,
        '["Basic ICP profiling", "3 moves per week", "Email support", "Basic analytics"]'::jsonb,
        '{"moves_per_week": 3, "campaigns": 1, "team_seats": 1}'::jsonb,
        1
    ),
    (
        'Glide',
        'glide',
        'Glide Plan',
        'Advanced features for growing teams',
        700000,
        7000000,
        '["Advanced ICP profiling", "10 moves per week", "Priority support", "Advanced analytics", "A/B testing"]'::jsonb,
        '{"moves_per_week": 10, "campaigns": 5, "team_seats": 3}'::jsonb,
        2
    ),
    (
        'Soar',
        'soar',
        'Soar Plan',
        'Enterprise-grade capabilities',
        1000000,
        10000000,
        '["Enterprise ICP profiling", "Unlimited moves", "24/7 support", "Custom analytics", "Advanced A/B testing", "API access", "Dedicated account manager"]'::jsonb,
        '{"moves_per_week": -1, "campaigns": -1, "team_seats": -1}'::jsonb,
        3
    )
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- USER_SUBSCRIPTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES public.subscription_plans(id) ON DELETE RESTRICT,
    status VARCHAR(50) NOT NULL DEFAULT 'trial' CHECK (status IN ('trial', 'active', 'past_due', 'canceled', 'unpaid', 'incomplete', 'incomplete_expired', 'paused')),
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    grace_period_end TIMESTAMP WITH TIME ZONE,
    phonepe_subscription_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    
    CONSTRAINT user_subscriptions_workspace_unique UNIQUE (workspace_id),
    CONSTRAINT user_subscriptions_period_check CHECK (
        (current_period_start IS NULL AND current_period_end IS NULL) OR
        (current_period_start IS NOT NULL AND current_period_end IS NOT NULL AND current_period_end > current_period_start)
    )
);

-- User subscriptions indexes
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_workspace_id ON public.user_subscriptions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_plan_id ON public.user_subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON public.user_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_trial_end ON public.user_subscriptions(trial_end);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_current_period_end ON public.user_subscriptions(current_period_end);

-- User subscriptions updated_at trigger
CREATE OR REPLACE FUNCTION public.update_user_subscriptions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_subscriptions_updated_at
    BEFORE UPDATE ON public.user_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION public.update_user_subscriptions_updated_at();

-- ============================================
-- SUBSCRIPTION_EVENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.subscription_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES public.user_subscriptions(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    previous_plan_id UUID REFERENCES public.subscription_plans(id) ON DELETE SET NULL,
    new_plan_id UUID REFERENCES public.subscription_plans(id) ON DELETE SET NULL,
    previous_status VARCHAR(50),
    new_status VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subscription events indexes
CREATE INDEX IF NOT EXISTS idx_subscription_events_subscription_id ON public.subscription_events(subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscription_events_event_type ON public.subscription_events(event_type);
CREATE INDEX IF NOT EXISTS idx_subscription_events_created_at ON public.subscription_events(created_at);

-- ============================================
-- PAYMENT_TRANSACTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES public.user_subscriptions(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES public.subscription_plans(id) ON DELETE SET NULL,
    amount INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'refunded', 'canceled')),
    payment_method VARCHAR(50),
    phonepe_transaction_id VARCHAR(255),
    phonepe_merchant_transaction_id VARCHAR(255),
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payment transactions indexes
CREATE INDEX IF NOT EXISTS idx_payment_transactions_subscription_id ON public.payment_transactions(subscription_id);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_plan_id ON public.payment_transactions(plan_id);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_status ON public.payment_transactions(status);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_created_at ON public.payment_transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_phonepe_transaction_id ON public.payment_transactions(phonepe_transaction_id);

-- Payment transactions updated_at trigger
CREATE OR REPLACE FUNCTION public.update_payment_transactions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER payment_transactions_updated_at
    BEFORE UPDATE ON public.payment_transactions
    FOR EACH ROW
    EXECUTE FUNCTION public.update_payment_transactions_updated_at();

-- ============================================
-- COMMENTS
-- ============================================
COMMENT ON TABLE public.subscription_plans IS 'Available subscription plans (Ascent, Glide, Soar)';
COMMENT ON TABLE public.user_subscriptions IS 'Active subscriptions for workspaces';
COMMENT ON TABLE public.subscription_events IS 'Audit log of subscription changes';
COMMENT ON TABLE public.payment_transactions IS 'Payment transaction records';

COMMIT;
