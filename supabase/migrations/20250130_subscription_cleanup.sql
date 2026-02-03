-- ============================================================================
-- RAPTORFLOW SUBSCRIPTION CLEANUP SCRIPT
-- Purpose: Remove duplicate/conflicting subscription entries and ensure consistency
-- Author: Cascade AI Assistant
-- Date: 2025-01-30
-- ============================================================================

BEGIN;

-- 1. CLEAN UP subscriptions TABLE - Remove conflicting plan names
UPDATE subscriptions
SET plan = CASE
    WHEN plan IN ('starter', 'basic', 'trial') THEN 'ascent'
    WHEN plan IN ('growth', 'pro', 'premium') THEN 'glide'
    WHEN plan IN ('enterprise', 'business', 'scale') THEN 'soar'
    WHEN plan IN ('free', 'trial') THEN plan
    ELSE 'ascent' -- Default fallback
END
WHERE plan NOT IN ('ascent', 'glide', 'soar', 'free', 'trial');

-- 2. REMOVE DUPLICATE ENTRIES IN subscription_plans IF ANY EXIST
DELETE FROM subscription_plans
WHERE id NOT IN (
    SELECT DISTINCT ON (slug) id
    FROM subscription_plans
    ORDER BY slug, created_at DESC
);

-- 3. ENSURE UNIQUE CONSTRAINTS
ALTER TABLE subscription_plans
ADD CONSTRAINT IF NOT EXISTS subscription_plans_slug_unique UNIQUE (slug);

-- 4. CLEAN UP ANY ORPHANED ENTRIES
DELETE FROM user_subscriptions
WHERE plan_id NOT IN (SELECT id FROM subscription_plans);

-- 5. UPDATE ANY REFERENCES IN OTHER TABLES
-- Update profiles table if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'profiles') THEN
        UPDATE profiles
        SET subscription_plan = CASE
            WHEN subscription_plan IN ('starter', 'basic') THEN 'ascent'
            WHEN subscription_plan IN ('growth', 'pro', 'premium') THEN 'glide'
            WHEN subscription_plan IN ('enterprise', 'business', 'scale') THEN 'soar'
            WHEN subscription_plan IN ('free', 'trial') THEN subscription_plan
            ELSE 'ascent'
        END
        WHERE subscription_plan NOT IN ('ascent', 'glide', 'soar', 'free', 'trial');
    END IF;
END $$;

-- 6. UPDATE users TABLE IF IT EXISTS
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        UPDATE users
        SET subscription_plan = CASE
            WHEN subscription_plan IN ('starter', 'basic') THEN 'ascent'
            WHEN subscription_plan IN ('growth', 'pro', 'premium') THEN 'glide'
            WHEN subscription_plan IN ('enterprise', 'business', 'scale') THEN 'soar'
            WHEN subscription_plan IN ('free', 'trial') THEN subscription_plan
            ELSE 'ascent'
        END
        WHERE subscription_plan NOT IN ('ascent', 'glide', 'soar', 'free', 'trial');
    END IF;
END $$;

-- 7. CREATE FINAL CONSISTENCY VIEW
CREATE OR REPLACE VIEW subscription_consistency_report AS
SELECT
    'subscription_plans' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT slug) as unique_plans,
    STRING_AGG(DISTINCT slug, ', ') as plan_list
FROM subscription_plans
UNION ALL
SELECT
    'subscriptions' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT plan) as unique_plans,
    STRING_AGG(DISTINCT plan, ', ') as plan_list
FROM subscriptions;

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check consistency report
-- SELECT * FROM subscription_consistency_report;

-- Check final subscription plans
-- SELECT * FROM subscription_plans ORDER BY sort_order;

-- Check subscriptions table
-- SELECT plan, COUNT(*) as count FROM subscriptions GROUP BY plan ORDER BY count DESC;
