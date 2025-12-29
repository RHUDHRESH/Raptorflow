-- Align Supabase schema with backend subscription/payment expectations

-- Plans table
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
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_plans_name ON plans(name);

ALTER TABLE plans
    ADD COLUMN IF NOT EXISTS description TEXT,
    ADD COLUMN IF NOT EXISTS price DECIMAL(10,2),
    ADD COLUMN IF NOT EXISTS currency VARCHAR(3) DEFAULT 'INR',
    ADD COLUMN IF NOT EXISTS billing_interval VARCHAR(20),
    ADD COLUMN IF NOT EXISTS features JSONB DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS max_icp_profiles INTEGER DEFAULT 3,
    ADD COLUMN IF NOT EXISTS max_campaigns INTEGER DEFAULT 10,
    ADD COLUMN IF NOT EXISTS max_users INTEGER DEFAULT 1,
    ADD COLUMN IF NOT EXISTS api_quota_daily INTEGER DEFAULT 1000,
    ADD COLUMN IF NOT EXISTS storage_quota_gb INTEGER DEFAULT 10,
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
    ADD COLUMN IF NOT EXISTS stripe_price_id VARCHAR(100),
    ADD COLUMN IF NOT EXISTS phonepe_plan_id VARCHAR(100),
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

UPDATE plans
SET
  price = COALESCE(price, price_monthly_paise / 100.0),
  currency = COALESCE(currency, 'INR'),
  billing_interval = COALESCE(billing_interval, 'monthly'),
  max_icp_profiles = COALESCE(max_icp_profiles, cohort_limit),
  max_campaigns = COALESCE(max_campaigns, cohort_limit),
  max_users = COALESCE(max_users, member_limit),
  storage_quota_gb = COALESCE(storage_quota_gb, (storage_limit_mb / 1024)),
  is_active = COALESCE(is_active, true)
WHERE price IS NULL
  OR billing_interval IS NULL
  OR max_users IS NULL
  OR max_campaigns IS NULL
  OR storage_quota_gb IS NULL;

-- Subscriptions table adjustments (keep existing columns, add missing ones)
ALTER TABLE subscriptions
    ADD COLUMN IF NOT EXISTS workspace_id UUID,
    ADD COLUMN IF NOT EXISTS plan_id UUID REFERENCES plans(id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS current_period_start TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS current_period_end TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS trial_start TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS trial_end TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS cancellation_reason TEXT,
    ADD COLUMN IF NOT EXISTS phonepe_merchant_order_id VARCHAR(100),
    ADD COLUMN IF NOT EXISTS phonepe_subscription_id VARCHAR(100),
    ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- Payment transactions
CREATE TABLE IF NOT EXISTS payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    plan_id UUID REFERENCES plans(id) ON DELETE RESTRICT,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
    merchant_order_id VARCHAR(100) NOT NULL,
    transaction_id VARCHAR(100),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'refunded', 'cancelled')),
    payment_method VARCHAR(50) DEFAULT 'phonepe',
    promo_code TEXT,
    discount_amount DECIMAL(10,2),
    gateway_response JSONB,
    failure_reason TEXT,
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(merchant_order_id),
    UNIQUE(transaction_id)
);

ALTER TABLE payment_transactions
    ADD COLUMN IF NOT EXISTS plan_id UUID REFERENCES plans(id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS promo_code TEXT,
    ADD COLUMN IF NOT EXISTS discount_amount DECIMAL(10,2);

-- Subscription usage tracking
CREATE TABLE IF NOT EXISTS subscription_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    metric_name VARCHAR(50) NOT NULL,
    current_usage INTEGER DEFAULT 0,
    limit_value INTEGER NOT NULL,
    reset_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workspace_id, subscription_id, metric_name)
);

-- Promo codes for discounted upgrades
CREATE TABLE IF NOT EXISTS promo_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    description TEXT,
    percent_off NUMERIC(5,2),
    amount_off NUMERIC(10,2),
    currency VARCHAR(3) DEFAULT 'INR',
    max_redemptions INTEGER,
    redemption_count INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT true,
    starts_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_workspace_id ON subscriptions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_workspace_id ON payment_transactions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_status ON payment_transactions(status);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_merchant_order_id ON payment_transactions(merchant_order_id);
CREATE INDEX IF NOT EXISTS idx_subscription_usage_workspace_id ON subscription_usage(workspace_id);
CREATE INDEX IF NOT EXISTS idx_subscription_usage_subscription_id ON subscription_usage(subscription_id);
CREATE INDEX IF NOT EXISTS idx_promo_codes_code ON promo_codes(code);
