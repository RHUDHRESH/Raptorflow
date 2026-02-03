-- ============================================================================
-- RAPTORFLOW SUBSCRIPTION UNIFICATION FIX
-- Purpose: Standardize all subscription plans to ₹5,000, ₹7,000, ₹10,000 (Ascent, Glide, Soar)
-- Author: Cascade AI Assistant
-- Date: 2025-01-30
-- ============================================================================

BEGIN;

-- 1. DROP AND RECREATE subscription_plans TABLE WITH CORRECT SCHEMA
DROP TABLE IF EXISTS subscription_plans CASCADE;

CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE, -- 'Ascent', 'Glide', 'Soar'
    slug VARCHAR(50) NOT NULL UNIQUE, -- 'ascent', 'glide', 'soar'
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly INTEGER NOT NULL, -- in paise (500000, 700000, 1000000)
    price_annual INTEGER NOT NULL, -- in paise (5000000, 7000000, 10000000)
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

-- 2. INSERT STANDARDIZED PRICING (₹5,000, ₹7,000, ₹10,000)
INSERT INTO subscription_plans (name, slug, display_name, description, price_monthly, price_annual, features, limits, sort_order) VALUES
('Ascent', 'ascent', 'Ascent', 'For founders just getting started with systematic marketing.', 500000, 5000000,
 '["Foundation setup (ICP + Positioning)", "Weekly Moves (3 per week)", "Basic Muse AI generation", "Matrix analytics dashboard", "Email support"]',
 '{"moves_per_week": 3, "campaigns": 3, "team_seats": 1, "muse_ai_basic": true, "priority_support": false}',
 1),
('Glide', 'glide', 'Glide', 'For founders scaling their marketing engine.', 700000, 7000000,
 '["Everything in Ascent", "Unlimited Moves", "Advanced Muse (voice training)", "Cohort segmentation", "Campaign planning tools", "Priority support", "Blackbox learnings vault"]',
 '{"moves_per_week": -1, "campaigns": -1, "team_seats": 5, "muse_ai_advanced": true, "priority_support": true}',
 2),
('Soar', 'soar', 'Soar', 'For teams running multi-channel campaigns.', 1000000, 10000000,
 '["Everything in Glide", "Team seats (up to 5)", "White-label exports", "Custom AI training", "API access", "Dedicated success manager", "Custom integrations"]',
 '{"moves_per_week": -1, "campaigns": -1, "team_seats": -1, "muse_ai_custom": true, "api_access": true, "white_label": true}',
 3);

-- 3. UPDATE subscriptions TABLE TO USE NEW PLAN SLUGS
UPDATE subscriptions 
SET plan = CASE 
    WHEN plan = 'starter' THEN 'ascent'
    WHEN plan = 'growth' THEN 'glide' 
    WHEN plan = 'enterprise' THEN 'soar'
    WHEN plan IN ('free', 'trial') THEN plan
    ELSE 'ascent' -- Default fallback
END
WHERE plan NOT IN ('ascent', 'glide', 'soar', 'free', 'trial');

-- 4. CREATE OR REPLACE VIEWS FOR COMPATIBILITY
CREATE OR REPLACE VIEW user_current_subscription AS
SELECT
    s.id as subscription_id,
    s.workspace_id,
    s.plan as plan_slug,
    sp.name as plan_name,
    sp.display_name as plan_display_name,
    s.status,
    s.current_period_start,
    s.current_period_end,
    s.trial_end,
    sp.price_monthly,
    sp.price_annual,
    sp.features,
    sp.limits,
    s.created_at as subscription_created_at
FROM subscriptions s
LEFT JOIN subscription_plans sp ON s.plan = sp.slug
WHERE s.status = 'active'
AND (s.current_period_end IS NULL OR s.current_period_end > NOW());

-- 5. CREATE HELPER FUNCTIONS
CREATE OR REPLACE FUNCTION get_plan_price_in_rupees(plan_slug TEXT, period TEXT DEFAULT 'monthly')
RETURNS NUMERIC AS $$
DECLARE
    price_in_paise NUMERIC;
BEGIN
    SELECT price_in_paise :=
        CASE
            WHEN period = 'monthly' THEN price_monthly
            WHEN period = 'annual' THEN price_annual
            ELSE price_monthly
        END
    FROM subscription_plans
    WHERE slug = get_plan_price_in_rupees.plan_slug AND is_active = true;

    RETURN price_in_paise / 100; -- Convert from paise to rupees
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION format_price_display(price_in_paise NUMERIC)
RETURNS TEXT AS $$
BEGIN
    RETURN '₹' || (price_in_paise / 100)::TEXT;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 6. ADD INDEXES FOR PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_subscription_plans_name ON subscription_plans(name);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_slug ON subscription_plans(slug);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_active ON subscription_plans(is_active);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_sort_order ON subscription_plans(sort_order);

-- 7. ENABLE RLS AND CREATE POLICIES
ALTER TABLE subscription_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public can read active subscription plans" ON subscription_plans
    FOR SELECT USING (is_active = true);

-- 8. UPDATED_AT TRIGGER
CREATE OR REPLACE FUNCTION update_subscription_plans_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER subscription_plans_updated_at
    BEFORE UPDATE ON subscription_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_subscription_plans_updated_at();

-- 9. ADD COMMENTS FOR DOCUMENTATION
COMMENT ON TABLE subscription_plans IS 'Standardized subscription plans (Ascent: ₹5,000, Glide: ₹7,000, Soar: ₹10,000)';
COMMENT ON COLUMN subscription_plans.price_monthly IS 'Monthly price in paise (₹1 = 100 paise)';
COMMENT ON COLUMN subscription_plans.price_annual IS 'Annual price in paise (₹1 = 100 paise)';
COMMENT ON COLUMN subscription_plans.limits IS 'JSON object with plan limits, -1 means unlimited';

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES (Run these to verify the fix)
-- ============================================================================

-- Check subscription plans
-- SELECT * FROM subscription_plans ORDER BY sort_order;

-- Check pricing in rupees
-- SELECT name, slug, price_monthly/100 as monthly_rupees, price_annual/100 as annual_rupees FROM subscription_plans;

-- Check subscriptions table
-- SELECT * FROM subscriptions WHERE plan IN ('ascent', 'glide', 'soar') LIMIT 5;
