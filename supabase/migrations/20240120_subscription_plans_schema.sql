-- Subscription Plans and User Journey Schema
-- Complete database schema for Ascent/Glide/Soar plans with payment and onboarding

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- SUBSCRIPTION PLANS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE, -- 'Ascent', 'Glide', 'Soar'
    slug VARCHAR(50) NOT NULL UNIQUE, -- 'ascent', 'glide', 'soar'
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly INTEGER NOT NULL, -- in paise (2900, 7900, 19900)
    price_annual INTEGER NOT NULL, -- in paise (2400, 6600, 16600)
    currency VARCHAR(3) DEFAULT 'INR',
    features JSONB NOT NULL DEFAULT '[]',
    limits JSONB NOT NULL DEFAULT '{}', -- Plan limits (moves, campaigns, etc.)
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER NOT NULL, -- For display ordering
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_plan_name CHECK (name IN ('Ascent', 'Glide', 'Soar')),
    CONSTRAINT positive_price CHECK (price_monthly > 0 AND price_annual > 0)
);

-- ==========================================
-- USER SUBSCRIPTIONS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),
    
    -- Subscription details
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'active', 'cancelled', 'expired', 'suspended'
    billing_cycle VARCHAR(10) NOT NULL DEFAULT 'monthly', -- 'monthly', 'annual'
    
    -- Payment references
    phonepe_order_id VARCHAR(100) UNIQUE,
    phonepe_transaction_id VARCHAR(100),
    
    -- Pricing and dates
    amount_paid INTEGER NOT NULL, -- in paise
    currency VARCHAR(3) DEFAULT 'INR',
    started_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    
    -- Auto-renewal settings
    auto_renew BOOLEAN DEFAULT true,
    next_billing_date TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_subscription_status CHECK (status IN ('pending', 'active', 'cancelled', 'expired', 'suspended')),
    CONSTRAINT valid_billing_cycle CHECK (billing_cycle IN ('monthly', 'annual')),
    CONSTRAINT positive_amount CHECK (amount_paid > 0)
);

-- ==========================================
-- USER ONBOARDING STATUS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS user_onboarding (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES user_subscriptions(id) ON DELETE SET NULL,
    
    -- Progress tracking
    current_step INTEGER DEFAULT 1,
    total_steps INTEGER DEFAULT 13, -- Total onboarding steps
    completed_steps JSONB DEFAULT '[]', -- Array of completed step numbers
    step_data JSONB DEFAULT '{}', -- Data collected during onboarding
    
    -- Status
    is_completed BOOLEAN DEFAULT false,
    is_skipped BOOLEAN DEFAULT false,
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_current_step CHECK (current_step >= 1 AND current_step <= total_steps)
);

-- ==========================================
-- PLAN USAGE LIMITS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS plan_usage_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscription_id UUID NOT NULL REFERENCES user_subscriptions(id) ON DELETE CASCADE,
    
    -- Usage tracking
    metric_name VARCHAR(100) NOT NULL, -- 'moves_per_week', 'campaigns', 'team_seats', etc.
    current_usage INTEGER DEFAULT 0,
    limit_value INTEGER NOT NULL,
    reset_period VARCHAR(20) DEFAULT 'monthly', -- 'daily', 'weekly', 'monthly', 'yearly'
    last_reset_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT positive_usage CHECK (current_usage >= 0 AND limit_value > 0),
    CONSTRAINT valid_reset_period CHECK (reset_period IN ('daily', 'weekly', 'monthly', 'yearly', 'never'))
);

-- ==========================================
-- SUBSCRIPTION EVENTS LOG TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS subscription_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES user_subscriptions(id) ON DELETE SET NULL,
    
    -- Event details
    event_type VARCHAR(50) NOT NULL, -- 'created', 'activated', 'cancelled', 'expired', 'renewed', 'upgraded', 'downgraded'
    previous_plan_id UUID REFERENCES subscription_plans(id),
    new_plan_id UUID REFERENCES subscription_plans(id),
    
    -- Event data
    event_data JSONB DEFAULT '{}',
    reason TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_event_type CHECK (event_type IN ('created', 'activated', 'cancelled', 'expired', 'renewed', 'upgraded', 'downgraded', 'suspended', 'reactivated'))
);

-- ==========================================
-- INDEXES FOR PERFORMANCE
-- ==========================================

-- Subscription plans indexes
CREATE INDEX IF NOT EXISTS idx_subscription_plans_name ON subscription_plans(name);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_slug ON subscription_plans(slug);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_active ON subscription_plans(is_active);

-- User subscriptions indexes
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_plan_id ON user_subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON user_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_expires_at ON user_subscriptions(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_phonepe_order_id ON user_subscriptions(phonepe_order_id);

-- User onboarding indexes
CREATE INDEX IF NOT EXISTS idx_user_onboarding_user_id ON user_onboarding(user_id);
CREATE INDEX IF NOT EXISTS idx_user_onboarding_subscription_id ON user_onboarding(subscription_id);
CREATE INDEX IF NOT EXISTS idx_user_onboarding_completed ON user_onboarding(is_completed);
CREATE INDEX IF NOT EXISTS idx_user_onboarding_current_step ON user_onboarding(current_step);

-- Plan usage limits indexes
CREATE INDEX IF NOT EXISTS idx_plan_usage_limits_subscription_id ON plan_usage_limits(subscription_id);
CREATE INDEX IF NOT EXISTS idx_plan_usage_limits_metric ON plan_usage_limits(metric_name);

-- Subscription events indexes
CREATE INDEX IF NOT EXISTS idx_subscription_events_user_id ON subscription_events(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_events_subscription_id ON subscription_events(subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscription_events_type ON subscription_events(event_type);
CREATE INDEX IF NOT EXISTS idx_subscription_events_created_at ON subscription_events(created_at);

-- ==========================================
-- TRIGGERS FOR UPDATED_AT
-- ==========================================

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_subscription_plans_updated_at
    BEFORE UPDATE ON subscription_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_subscriptions_updated_at
    BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_onboarding_updated_at
    BEFORE UPDATE ON user_onboarding
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plan_usage_limits_updated_at
    BEFORE UPDATE ON plan_usage_limits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ==========================================

-- Enable RLS on subscription tables
ALTER TABLE subscription_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_onboarding ENABLE ROW LEVEL SECURITY;
ALTER TABLE plan_usage_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscription_events ENABLE ROW LEVEL SECURITY;

-- Policies for subscription plans (public read access)
CREATE POLICY "Public can read subscription plans" ON subscription_plans
    FOR SELECT USING (is_active = true);

-- Policies for user subscriptions (users can only see their own)
CREATE POLICY "Users can view own subscriptions" ON user_subscriptions
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert own subscriptions" ON user_subscriptions
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own subscriptions" ON user_subscriptions
    FOR UPDATE USING (user_id = auth.uid());

-- Policies for user onboarding (users can only see their own)
CREATE POLICY "Users can view own onboarding" ON user_onboarding
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert own onboarding" ON user_onboarding
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own onboarding" ON user_onboarding
    FOR UPDATE USING (user_id = auth.uid());

-- Policies for plan usage limits (users can only see their own)
CREATE POLICY "Users can view own usage limits" ON plan_usage_limits
    FOR SELECT USING (
        subscription_id IN (
            SELECT id FROM user_subscriptions
            WHERE user_id = auth.uid()
        )
    );

-- Policies for subscription events (users can only see their own)
CREATE POLICY "Users can view own subscription events" ON subscription_events
    FOR SELECT USING (user_id = auth.uid());

-- ==========================================
-- VIEWS FOR COMMON QUERIES
-- ==========================================

-- View for user's current subscription with plan details
CREATE OR REPLACE VIEW user_current_subscription AS
SELECT 
    us.id as subscription_id,
    us.user_id,
    us.plan_id,
    sp.name as plan_name,
    sp.slug as plan_slug,
    sp.display_name as plan_display_name,
    us.status,
    us.billing_cycle,
    us.amount_paid,
    us.started_at,
    us.expires_at,
    us.auto_renew,
    us.next_billing_date,
    uo.is_completed as onboarding_completed,
    uo.current_step as onboarding_step,
    us.created_at as subscription_created_at
FROM user_subscriptions us
JOIN subscription_plans sp ON us.plan_id = sp.id
LEFT JOIN user_onboarding uo ON us.id = uo.subscription_id
WHERE us.status = 'active'
AND (us.expires_at IS NULL OR us.expires_at > NOW());

-- View for subscription analytics
CREATE OR REPLACE VIEW subscription_analytics AS
SELECT 
    sp.name as plan_name,
    COUNT(us.id) as active_subscriptions,
    SUM(us.amount_paid) as total_revenue,
    AVG(us.amount_paid) as avg_revenue,
    COUNT(CASE WHEN us.billing_cycle = 'annual' THEN 1 END) as annual_subscriptions,
    COUNT(CASE WHEN us.billing_cycle = 'monthly' THEN 1 END) as monthly_subscriptions
FROM subscription_plans sp
LEFT JOIN user_subscriptions us ON sp.id = us.plan_id AND us.status = 'active'
GROUP BY sp.id, sp.name;

-- ==========================================
-- FUNCTIONS FOR SUBSCRIPTION OPERATIONS
-- ==========================================

-- Function to get user's current subscription status
CREATE OR REPLACE FUNCTION get_user_subscription_status(p_user_id UUID)
RETURNS TABLE(
    has_subscription BOOLEAN,
    plan_name VARCHAR(50),
    plan_slug VARCHAR(50),
    status VARCHAR(20),
    expires_at TIMESTAMP WITH TIME ZONE,
    onboarding_completed BOOLEAN,
    onboarding_step INTEGER,
    can_access_app BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (us.id IS NOT NULL) as has_subscription,
        sp.name as plan_name,
        sp.slug as plan_slug,
        us.status,
        us.expires_at,
        COALESCE(uo.is_completed, false) as onboarding_completed,
        COALESCE(uo.current_step, 1) as onboarding_step,
        (us.id IS NOT NULL AND us.status = 'active' AND (us.expires_at IS NULL OR us.expires_at > NOW()) AND COALESCE(uo.is_completed, false)) as can_access_app
    FROM user_subscriptions us
    JOIN subscription_plans sp ON us.plan_id = sp.id
    LEFT JOIN user_onboarding uo ON us.id = uo.subscription_id
    WHERE us.user_id = p_user_id
    AND us.status = 'active'
    ORDER BY us.created_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create user subscription
CREATE OR REPLACE FUNCTION create_user_subscription(
    p_user_id UUID,
    p_plan_slug VARCHAR(50),
    p_billing_cycle VARCHAR(10) DEFAULT 'monthly',
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
    FROM subscription_plans
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
    INSERT INTO user_subscriptions (
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
    INSERT INTO user_onboarding (user_id, subscription_id)
    VALUES (p_user_id, new_subscription_id);
    
    -- Initialize usage limits
    INSERT INTO plan_usage_limits (subscription_id, metric_name, limit_value)
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

-- ==========================================
-- SEED DATA FOR SUBSCRIPTION PLANS
-- ==========================================

-- Insert subscription plans
INSERT INTO subscription_plans (name, slug, display_name, description, price_monthly, price_annual, features, limits, sort_order) VALUES
('Ascent', 'ascent', 'Ascent', 'For founders just getting started with systematic marketing.', 2900, 24000, 
 '["Foundation setup (ICP + Positioning)", "Weekly Moves (3 per week)", "Basic Muse AI generation", "Matrix analytics dashboard", "Email support"]',
 '{"moves_per_week": 3, "campaigns": 3, "team_seats": 1, "muse_ai_basic": true, "priority_support": false}',
 1),
('Glide', 'glide', 'Glide', 'For founders scaling their marketing engine.', 7900, 66000,
 '["Everything in Ascent", "Unlimited Moves", "Advanced Muse (voice training)", "Cohort segmentation", "Campaign planning tools", "Priority support", "Blackbox learnings vault"]',
 '{"moves_per_week": -1, "campaigns": -1, "team_seats": 5, "muse_ai_advanced": true, "priority_support": true}',
 2),
('Soar', 'soar', 'Soar', 'For teams running multi-channel campaigns.', 19900, 166000,
 '["Everything in Glide", "Team seats (up to 5)", "White-label exports", "Custom AI training", "API access", "Dedicated success manager", "Custom integrations"]',
 '{"moves_per_week": -1, "campaigns": -1, "team_seats": -1, "muse_ai_custom": true, "api_access": true, "white_label": true}',
 3)
ON CONFLICT (name) DO NOTHING;

-- ==========================================
-- COMMENTS
-- ==========================================

COMMENT ON TABLE subscription_plans IS 'Available subscription plans (Ascent, Glide, Soar)';
COMMENT ON TABLE user_subscriptions IS 'User subscription records with payment and billing details';
COMMENT ON TABLE user_onboarding IS 'Tracks user progress through onboarding wizard';
COMMENT ON TABLE plan_usage_limits IS 'Enforces plan-specific usage limits';
COMMENT ON TABLE subscription_events IS 'Audit log for subscription lifecycle events';

COMMENT ON COLUMN user_subscriptions.amount_paid IS 'Amount in paise (1 INR = 100 paise)';
COMMENT ON COLUMN user_subscriptions.status IS 'Subscription status: pending, active, cancelled, expired, suspended';
COMMENT ON COLUMN user_onboarding.current_step IS 'Current onboarding step (1-13)';
COMMENT ON COLUMN plan_usage_limits.limit_value IS 'Usage limit, -1 means unlimited';
