-- =================================================================
-- MIGRATION: Drop Old Table and Adopt Archive Schema
-- Date: 2026-01-30
-- Purpose: Migrate from old subscription_plans to archive schema
-- =================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =================================================================
-- STEP 1: BACKUP EXISTING DATA
-- =================================================================

-- Create a temporary backup table to preserve existing data
CREATE TEMPORARY TABLE IF NOT EXISTS temp_subscription_plans_backup AS
SELECT * FROM public.subscription_plans;

-- Log the backup
DO $$
DECLARE
    backup_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO backup_count FROM temp_subscription_plans_backup;
    RAISE NOTICE '✅ Backed up % records from subscription_plans', backup_count;
END $$;

-- =================================================================
-- STEP 2: DROP FOREIGN KEY CONSTRAINTS
-- =================================================================

-- Drop foreign key constraints from dependent tables
DO $$
BEGIN
    -- Drop constraints from user_subscriptions if they exist
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'user_subscriptions_plan_id_fkey'
    ) THEN
        ALTER TABLE public.user_subscriptions DROP CONSTRAINT user_subscriptions_plan_id_fkey;
        RAISE NOTICE '✅ Dropped user_subscriptions_plan_id_fkey constraint';
    END IF;

    -- Drop constraints from subscription_events if they exist
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'subscription_events_previous_plan_id_fkey'
    ) THEN
        ALTER TABLE public.subscription_events DROP CONSTRAINT subscription_events_previous_plan_id_fkey;
        RAISE NOTICE '✅ Dropped subscription_events_previous_plan_id_fkey constraint';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'subscription_events_new_plan_id_fkey'
    ) THEN
        ALTER TABLE public.subscription_events DROP CONSTRAINT subscription_events_new_plan_id_fkey;
        RAISE NOTICE '✅ Dropped subscription_events_new_plan_id_fkey constraint';
    END IF;

    -- Drop constraints from payment_transactions if they exist
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'payment_transactions_plan_id_fkey'
    ) THEN
        ALTER TABLE public.payment_transactions DROP CONSTRAINT payment_transactions_plan_id_fkey;
        RAISE NOTICE '✅ Dropped payment_transactions_plan_id_fkey constraint';
    END IF;
END $$;

-- =================================================================
-- STEP 3: DROP OLD TABLE
-- =================================================================

-- Drop the old subscription_plans table
DROP TABLE IF EXISTS public.subscription_plans CASCADE;

RAISE NOTICE '✅ Dropped old subscription_plans table';

-- =================================================================
-- STEP 4: CREATE NEW ARCHIVE SCHEMA TABLE
-- =================================================================

-- Create the new subscription_plans table with archive schema
CREATE TABLE public.subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

RAISE NOTICE '✅ Created new subscription_plans table with archive schema';

-- =================================================================
-- STEP 5: MIGRATE DATA FROM BACKUP
-- =================================================================

-- Insert data from backup, handling any schema differences
INSERT INTO public.subscription_plans (
    id,
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
    sort_order,
    created_at,
    updated_at
)
SELECT
    id,
    COALESCE(name, 'Unknown') as name,
    COALESCE(slug, 'unknown') as slug,
    COALESCE(display_name, name, 'Unknown Plan') as display_name,
    COALESCE(description, '') as description,
    COALESCE(price_monthly, 0) as price_monthly,
    COALESCE(price_annual, 0) as price_annual,
    COALESCE(currency, 'INR') as currency,
    COALESCE(features, '[]'::jsonb) as features,
    COALESCE(limits, '{}'::jsonb) as limits,
    COALESCE(is_active, true) as is_active,
    COALESCE(sort_order, 0) as sort_order,
    COALESCE(created_at, NOW()) as created_at,
    COALESCE(updated_at, NOW()) as updated_at
FROM temp_subscription_plans_backup
ON CONFLICT (id) DO NOTHING;

-- Log the migration
DO $$
DECLARE
    migrated_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO migrated_count FROM public.subscription_plans;
    RAISE NOTICE '✅ Migrated % records to new subscription_plans table', migrated_count;
END $$;

-- =================================================================
-- STEP 6: INSERT DEFAULT PLANS IF TABLE IS EMPTY
-- =================================================================

DO $$
DECLARE
    plan_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO plan_count FROM public.subscription_plans;

    IF plan_count = 0 THEN
        -- Insert the three subscription plans with correct pricing
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
            500000,  -- ₹5,000 in paise
            5000000, -- ₹50,000 in paise
            'INR',
            '["Basic ICP profiling", "3 moves per week", "Email support", "Basic analytics"]'::jsonb,
            '{"moves_per_week": 3, "campaigns": 1, "team_seats": 1}'::jsonb,
            true,
            1
        ),
        (
            'Glide',
            'glide',
            'Glide',
            'For growing teams ready to scale their marketing operations.',
            700000,  -- ₹7,000 in paise
            7000000, -- ₹70,000 in paise
            'INR',
            '["Advanced ICP profiling", "10 moves per week", "Priority support", "Advanced analytics", "A/B testing"]'::jsonb,
            '{"moves_per_week": 10, "campaigns": 5, "team_seats": 3}'::jsonb,
            true,
            2
        ),
        (
            'Soar',
            'soar',
            'Soar',
            'For established businesses with complex marketing needs.',
            1000000, -- ₹10,000 in paise
            10000000, -- ₹100,000 in paise
            'INR',
            '["Enterprise ICP profiling", "Unlimited moves", "24/7 support", "Custom analytics", "Advanced A/B testing", "API access", "Dedicated account manager"]'::jsonb,
            '{"moves_per_week": -1, "campaigns": -1, "team_seats": -1}'::jsonb,
            true,
            3
        );

        RAISE NOTICE '✅ Inserted default subscription plans';
    END IF;
END $$;

-- =================================================================
-- STEP 7: RECREATE FOREIGN KEY CONSTRAINTS
-- =================================================================

-- Recreate foreign key constraints for user_subscriptions
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'user_subscriptions'
    ) THEN
        ALTER TABLE public.user_subscriptions
        ADD CONSTRAINT user_subscriptions_plan_id_fkey
        FOREIGN KEY (plan_id) REFERENCES public.subscription_plans(id) ON DELETE RESTRICT;

        RAISE NOTICE '✅ Recreated user_subscriptions_plan_id_fkey constraint';
    END IF;
END $$;

-- Recreate foreign key constraints for subscription_events
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'subscription_events'
    ) THEN
        ALTER TABLE public.subscription_events
        ADD CONSTRAINT subscription_events_previous_plan_id_fkey
        FOREIGN KEY (previous_plan_id) REFERENCES public.subscription_plans(id) ON DELETE SET NULL;

        ALTER TABLE public.subscription_events
        ADD CONSTRAINT subscription_events_new_plan_id_fkey
        FOREIGN KEY (new_plan_id) REFERENCES public.subscription_plans(id) ON DELETE SET NULL;

        RAISE NOTICE '✅ Recreated subscription_events foreign key constraints';
    END IF;
END $$;

-- Recreate foreign key constraints for payment_transactions if plan_id column exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'payment_transactions' AND column_name = 'plan_id'
    ) THEN
        ALTER TABLE public.payment_transactions
        ADD CONSTRAINT payment_transactions_plan_id_fkey
        FOREIGN KEY (plan_id) REFERENCES public.subscription_plans(id) ON DELETE SET NULL;

        RAISE NOTICE '✅ Recreated payment_transactions_plan_id_fkey constraint';
    END IF;
END $$;

-- =================================================================
-- STEP 8: CREATE INDEXES FOR PERFORMANCE
-- =================================================================

-- Create indexes for subscription_plans
CREATE INDEX IF NOT EXISTS idx_subscription_plans_name ON public.subscription_plans(name);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_slug ON public.subscription_plans(slug);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_active ON public.subscription_plans(is_active);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_sort_order ON public.subscription_plans(sort_order);

RAISE NOTICE '✅ Created indexes for subscription_plans';

-- =================================================================
-- STEP 9: CREATE TRIGGER FOR UPDATED_AT
-- =================================================================

-- Create or replace the update_updated_at_column function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for subscription_plans
DROP TRIGGER IF EXISTS update_subscription_plans_updated_at ON public.subscription_plans;
CREATE TRIGGER update_subscription_plans_updated_at
    BEFORE UPDATE ON public.subscription_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

RAISE NOTICE '✅ Created updated_at trigger for subscription_plans';

-- =================================================================
-- STEP 10: ENABLE ROW LEVEL SECURITY (RLS)
-- =================================================================

ALTER TABLE public.subscription_plans ENABLE ROW LEVEL SECURITY;

RAISE NOTICE '✅ Enabled RLS on subscription_plans';

-- =================================================================
-- STEP 11: CREATE RLS POLICIES
-- =================================================================

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "subscription_plans_allow_authenticated" ON public.subscription_plans;
DROP POLICY IF EXISTS "Public can read active subscription plans" ON public.subscription_plans;
DROP POLICY IF EXISTS "Public can read subscription plans" ON public.subscription_plans;
DROP POLICY IF EXISTS "subscription_plans_view_active" ON public.subscription_plans;

-- Create consolidated policy for reading active plans
CREATE POLICY "subscription_plans_view_active" ON public.subscription_plans
    FOR SELECT USING (is_active = true OR auth.role() = 'service_role');

RAISE NOTICE '✅ Created RLS policies for subscription_plans';

-- =================================================================
-- STEP 12: GRANT PERMISSIONS
-- =================================================================

-- Grant permissions to authenticated users
GRANT SELECT ON public.subscription_plans TO authenticated;

-- Grant full permissions to service role
GRANT ALL ON public.subscription_plans TO service_role;

RAISE NOTICE '✅ Granted permissions on subscription_plans';

-- =================================================================
-- STEP 13: ADD COMMENTS FOR DOCUMENTATION
-- =================================================================

COMMENT ON TABLE public.subscription_plans IS 'Standardized subscription plans (Ascent: ₹5,000, Glide: ₹7,000, Soar: ₹10,000)';
COMMENT ON COLUMN public.subscription_plans.price_monthly IS 'Monthly price in paise (₹1 = 100 paise)';
COMMENT ON COLUMN public.subscription_plans.price_annual IS 'Annual price in paise (₹1 = 100 paise)';
COMMENT ON COLUMN public.subscription_plans.limits IS 'JSON object with plan limits, -1 means unlimited';
COMMENT ON COLUMN public.subscription_plans.features IS 'JSON array of features included in the plan';

RAISE NOTICE '✅ Added documentation comments';

-- =================================================================
-- STEP 14: CLEANUP TEMPORARY BACKUP TABLE
-- =================================================================

DROP TABLE IF EXISTS temp_subscription_plans_backup;

RAISE NOTICE '✅ Cleaned up temporary backup table';

-- =================================================================
-- MIGRATION COMPLETE
-- =================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════';
    RAISE NOTICE '✅ MIGRATION COMPLETED SUCCESSFULLY';
    RAISE NOTICE '═══════════════════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE 'Summary:';
    RAISE NOTICE '  - Dropped old subscription_plans table';
    RAISE NOTICE '  - Created new archive schema table';
    RAISE NOTICE '  - Migrated existing data';
    RAISE NOTICE '  - Updated foreign key constraints';
    RAISE NOTICE '  - Created indexes and triggers';
    RAISE NOTICE '  - Enabled RLS and created policies';
    RAISE NOTICE '  - Granted permissions';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Run migration 20260126_fix_duplicate_plans.sql';
    RAISE NOTICE '  2. Verify data integrity';
    RAISE NOTICE '  3. Test application functionality';
    RAISE NOTICE '═══════════════════════════════════════════════════════════';
    RAISE NOTICE '';
END $$;

