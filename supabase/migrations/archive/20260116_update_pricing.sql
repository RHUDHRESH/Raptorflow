-- Update pricing plans to match database structure
-- Migration: 20260116_update_pricing.sql
-- This migration updates the subscription plans to match the actual pricing structure

-- Update subscription_plans table to match actual pricing
UPDATE subscription_plans SET
    price_monthly = 290000,  -- ₹2,900 in paise (Ascent)
    price_yearly = 2900000,  -- ₹29,000 in paise (Ascent)
    features = jsonb_build_array(
        'Basic workspace access',
        'Up to 5 users',
        '10GB storage',
        'Email support',
        'Standard templates'
    )
WHERE plan_name = 'ascent';

UPDATE subscription_plans SET
    price_monthly = 790000,  -- ₹7,900 in paise (Glide)
    price_yearly = 7900000,  -- ₹79,000 in paise (Glide)
    features = jsonb_build_array(
        'Advanced workspace access',
        'Up to 25 users',
        '100GB storage',
        'Priority email support',
        'Advanced templates',
        'Custom branding',
        'API access'
    )
WHERE plan_name = 'glide';

UPDATE subscription_plans SET
    price_monthly = 1990000, -- ₹19,900 in paise (Soar)
    price_yearly = 19900000, -- ₹199,000 in paise (Soar)
    features = jsonb_build_array(
        'Enterprise workspace access',
        'Unlimited users',
        '1TB storage',
        '24/7 phone support',
        'Premium templates',
        'White-label branding',
        'Advanced API access',
        'Custom integrations',
        'Dedicated account manager',
        'SLA guarantee',
        'Advanced analytics',
        'Custom workflows'
    )
WHERE plan_name = 'soar';

-- Update free plan if it exists
UPDATE subscription_plans SET
    price_monthly = 0,
    price_yearly = 0,
    features = jsonb_build_array(
        'Basic workspace access',
        'Up to 3 users',
        '1GB storage',
        'Community support',
        'Basic templates'
    )
WHERE plan_name = 'free';

-- Add missing plans if they don't exist
INSERT INTO subscription_plans (plan_name, display_name, description, price_monthly, price_yearly, features, is_active, created_at, updated_at)
SELECT
    'free',
    'Free',
    'Perfect for individuals and small teams getting started',
    0,
    0,
    jsonb_build_array(
        'Basic workspace access',
        'Up to 3 users',
        '1GB storage',
        'Community support',
        'Basic templates'
    ),
    true,
    NOW(),
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM subscription_plans WHERE plan_name = 'free');

-- Add trial plan if it doesn't exist
INSERT INTO subscription_plans (plan_name, display_name, description, price_monthly, price_yearly, features, is_active, created_at, updated_at)
SELECT
    'trial',
    'Trial',
    'Try all features for 14 days',
    0,
    0,
    json_build_array(
        'All features included',
        'Up to 50 users',
        '500GB storage',
        'Priority support',
        'All templates',
        'API access',
        'Custom branding'
    ),
    true,
    NOW(),
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM subscription_plans WHERE plan_name = 'trial');

-- Update user subscription plans to match new pricing
-- First, update any users with invalid pricing plans
UPDATE users
SET
    subscription_plan = 'free',
    subscription_status = CASE
        WHEN subscription_status = 'active' AND subscription_plan NOT IN ('free', 'ascent', 'glide', 'soar') THEN 'cancelled'
        ELSE subscription_status
    END
WHERE subscription_plan NOT IN ('free', 'ascent', 'glide', 'soar');

-- Update profiles table to match new pricing structure
UPDATE profiles
SET
    subscription_plan = CASE
        WHEN subscription_plan NOT IN ('free', 'ascent', 'glide', 'soar') THEN 'free'
        ELSE subscription_plan
    END,
    subscription_status = CASE
        WHEN subscription_status NOT IN ('none', 'trial', 'active', 'cancelled', 'expired', 'suspended') THEN 'none'
        ELSE subscription_status
    END
WHERE subscription_plan NOT IN ('free', 'ascent', 'glide', 'soar');

-- Add comments for clarity
COMMENT ON TABLE subscription_plans IS 'Subscription plans with pricing in paise (₹1 = 100 paise)';
COMMENT ON COLUMN subscription_plans.price_monthly IS 'Monthly price in paise (₹1 = 100 paise)';
COMMENT ON COLUMN subscription_plans.price_yearly IS 'Yearly price in paise (₹1 = 100 paise)';
COMMENT ON COLUMN subscription_plans.features IS 'JSON array of features included in the plan';

-- Create a function to get plan pricing in rupees
CREATE OR REPLACE FUNCTION get_plan_price_in_rupees(plan_name TEXT, period TEXT DEFAULT 'monthly')
RETURNS NUMERIC AS $$
DECLARE
    price_in_paise NUMERIC;
BEGIN
    SELECT price_in_paise =
        CASE
            WHEN period = 'monthly' THEN price_monthly
            WHEN period = 'yearly' THEN price_yearly
            ELSE price_monthly
        END
    FROM subscription_plans
    WHERE plan_name = get_plan_price_in_rupees.plan_name;

    RETURN price_in_paise / 100; -- Convert from paise to rupees
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to format price display
CREATE OR REPLACE FUNCTION format_price_display(price_in_paise NUMERIC)
RETURNS TEXT AS $$
BEGIN
    RETURN '₹' || (price_in_paise / 100)::TEXT;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to get plan features
CREATE OR REPLACE FUNCTION get_plan_features(plan_name TEXT)
RETURNS JSONB AS $$
BEGIN
    RETURN (
        SELECT features
        FROM subscription_plans
        WHERE plan_name = get_plan_features.plan_name
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a trigger to update updated_at timestamp on subscription_plans
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

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_subscription_plans_name ON subscription_plans(plan_name);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_active ON subscription_plans(is_active);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_price_monthly ON subscription_plans(price_monthly);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_price_yearly ON subscription_plans(price_yearly);

-- Grant necessary permissions
GRANT SELECT ON subscription_plans TO authenticated;
GRANT SELECT ON get_plan_price_in_rupees TO authenticated;
GRANT SELECT ON format_price_display TO authenticated;
GRANT SELECT ON get_plan_features TO authenticated;
