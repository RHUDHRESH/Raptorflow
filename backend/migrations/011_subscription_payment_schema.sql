-- Subscription and Payment Management Schema
-- Handles plans, subscriptions, and payment transactions with workspace isolation

-- Plans table - defines subscription plans and their entitlements
CREATE TABLE IF NOT EXISTS plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    billing_interval VARCHAR(20) NOT NULL CHECK (billing_interval IN ('monthly', 'yearly')),
    features JSONB NOT NULL DEFAULT '{}',
    max_icp_profiles INTEGER DEFAULT 3,
    max_campaigns INTEGER DEFAULT 10,
    max_users INTEGER DEFAULT 1,
    api_quota_daily INTEGER DEFAULT 1000,
    storage_quota_gb INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT true,
    stripe_price_id VARCHAR(100),
    phonepe_plan_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subscriptions table - tracks workspace subscriptions
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES plans(id) ON DELETE RESTRICT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'cancelled', 'expired', 'past_due')),
    current_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,
    phonepe_merchant_order_id VARCHAR(100),
    phonepe_subscription_id VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(workspace_id), -- One subscription per workspace
    UNIQUE(phonepe_merchant_order_id)
);

-- Payment transactions table - tracks all payment attempts
CREATE TABLE IF NOT EXISTS payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
    merchant_order_id VARCHAR(100) NOT NULL,
    transaction_id VARCHAR(100),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'refunded', 'cancelled')),
    payment_method VARCHAR(50) DEFAULT 'phonepe',
    gateway_response JSONB,
    failure_reason TEXT,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(merchant_order_id),
    UNIQUE(transaction_id)
);

-- Subscription usage tracking
CREATE TABLE IF NOT EXISTS subscription_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    metric_name VARCHAR(50) NOT NULL, -- e.g., 'api_calls', 'storage_gb', 'icp_profiles'
    current_usage INTEGER DEFAULT 0,
    limit_value INTEGER NOT NULL,
    reset_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(workspace_id, subscription_id, metric_name)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_subscriptions_workspace_id ON subscriptions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_workspace_id ON payment_transactions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_status ON payment_transactions(status);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_merchant_order_id ON payment_transactions(merchant_order_id);
CREATE INDEX IF NOT EXISTS idx_subscription_usage_workspace_id ON subscription_usage(workspace_id);
CREATE INDEX IF NOT EXISTS idx_subscription_usage_subscription_id ON subscription_usage(subscription_id);

-- Insert default plans
INSERT INTO plans (name, description, price, currency, billing_interval, features, max_icp_profiles, max_campaigns, max_users, api_quota_daily, storage_quota_gb) VALUES
('Starter', 'Perfect for small teams getting started with AI-powered marketing', 999.00, 'INR', 'monthly', '{"ai_agents": true, "basic_analytics": true, "email_support": true}', 3, 10, 3, 1000, 10),
('Professional', 'Advanced features for growing marketing teams', 2999.00, 'INR', 'monthly', '{"ai_agents": true, "advanced_analytics": true, "priority_support": true, "custom_integrations": true}', 10, 50, 10, 5000, 50),
('Enterprise', 'Full-featured solution for large organizations', 9999.00, 'INR', 'monthly', '{"ai_agents": true, "advanced_analytics": true, "dedicated_support": true, "custom_integrations": true, "white_label": true, "sla_guarantee": true}', -1, -1, -1, -1, -1)
ON CONFLICT DO NOTHING;

-- RLS policies for workspace isolation
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscription_usage ENABLE ROW LEVEL SECURITY;

-- Subscriptions RLS - users can only see their workspace subscriptions
CREATE POLICY subscription_workspace_policy ON subscriptions
    FOR ALL USING (workspace_id = current_setting('app.current_workspace_id', true)::UUID);

-- Payment transactions RLS - users can only see their workspace transactions
CREATE POLICY payment_transaction_workspace_policy ON payment_transactions
    FOR ALL USING (workspace_id = current_setting('app.current_workspace_id', true)::UUID);

-- Subscription usage RLS - users can only see their workspace usage
CREATE POLICY subscription_usage_workspace_policy ON subscription_usage
    FOR ALL USING (workspace_id = current_setting('app.current_workspace_id', true)::UUID);

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_plans_timestamp BEFORE UPDATE ON plans
    FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_subscriptions_timestamp BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_payment_transactions_timestamp BEFORE UPDATE ON payment_transactions
    FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_subscription_usage_timestamp BEFORE UPDATE ON subscription_usage
    FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();
