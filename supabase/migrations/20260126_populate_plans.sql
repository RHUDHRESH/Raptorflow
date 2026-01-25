-- Create and populate subscription_plans table with correct data
-- This ensures the plans table has the required data for plan selection

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create subscription_plans table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE, -- 'Ascent', 'Glide', 'Soar'
    slug VARCHAR(50) NOT NULL UNIQUE, -- 'ascent', 'glide', 'soar'
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly INTEGER NOT NULL, -- in paise (5000, 7000, 10000)
    price_annual INTEGER NOT NULL, -- in paise (50000, 70000, 100000)
    currency VARCHAR(3) DEFAULT 'INR',
    features JSONB NOT NULL DEFAULT '[]',
    limits JSONB NOT NULL DEFAULT '{}', -- Plan limits (projects, team_members, etc.)
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER NOT NULL, -- For display ordering
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT valid_plan_name CHECK (name IN ('Ascent', 'Glide', 'Soar')),
    CONSTRAINT positive_price CHECK (price_monthly > 0 AND price_annual > 0)
);

-- Clear existing data to avoid duplicates
DELETE FROM public.subscription_plans WHERE name IN ('Ascent', 'Glide', 'Soar');

-- Insert the three subscription plans
INSERT INTO public.subscription_plans (
    name,
    slug,
    display_name,
    description,
    price_monthly,
    price_annual,
    currency,
    features,
    limits,
    is_active,
    sort_order
) VALUES
(
    'Ascent',
    'ascent',
    'Ascent',
    'For founders just getting started with systematic marketing.',
    500000,
    5000000,
    'INR',
    '["Foundation setup", "3 weekly Moves", "Basic Muse AI", "Matrix analytics", "Email support"]',
    '{"projects": 3, "team_members": 1, "support": "email"}',
    true,
    1
),
(
    'Glide',
    'glide',
    'Glide',
    'For founders scaling their marketing engine.',
    700000,
    7000000,
    'INR',
    '["Everything in Ascent", "Unlimited Moves", "Advanced Muse", "Cohort segmentation", "Priority support"]',
    '{"projects": 10, "team_members": 5, "support": "priority"}',
    true,
    2
),
(
    'Soar',
    'soar',
    'Soar',
    'For teams running multi-channel campaigns.',
    1000000,
    10000000,
    'INR',
    '["Everything in Glide", "Unlimited team seats", "Custom AI training", "API access", "Dedicated support"]',
    '{"projects": -1, "team_members": -1, "support": "dedicated"}',
    true,
    3
);

-- Ensure RLS is enabled and policies allow access
ALTER TABLE public.subscription_plans ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read plans
DROP POLICY IF EXISTS "subscription_plans_allow_authenticated" ON public.subscription_plans;
CREATE POLICY "subscription_plans_allow_authenticated" ON public.subscription_plans
    FOR SELECT USING (auth.role() = 'authenticated');

-- Allow service role full access
GRANT ALL ON public.subscription_plans TO service_role;

-- Log the operation
DO $$
BEGIN
    RAISE NOTICE '✅ Subscription plans table created and populated successfully';
    RAISE NOTICE '📊 Plans inserted: Ascent (₹5,000), Glide (₹7,000), Soar (₹10,000)';
END $$;
