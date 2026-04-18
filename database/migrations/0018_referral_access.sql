ALTER TABLE users
    ADD COLUMN IF NOT EXISTS referral_code text,
    ADD COLUMN IF NOT EXISTS referral_applied_at timestamptz;

ALTER TABLE subscriptions
    ADD COLUMN IF NOT EXISTS plan_tier text,
    ADD COLUMN IF NOT EXISTS referral_code text,
    ADD COLUMN IF NOT EXISTS discount_percent integer NOT NULL DEFAULT 0;

UPDATE subscriptions
SET plan_tier = CASE
    WHEN plan_tier IS NOT NULL THEN plan_tier
    WHEN plan_amount_inr <= 0 THEN 'ascend'
    WHEN plan_amount_inr <= 5000 THEN 'ascend'
    WHEN plan_amount_inr <= 7000 THEN 'glide'
    WHEN plan_amount_inr <= 10000 THEN 'soar'
    ELSE 'enterprise'
END;

UPDATE subscriptions
SET discount_percent = CASE
    WHEN referral_code IS NOT NULL THEN 100
    ELSE discount_percent
END;

ALTER TABLE subscriptions
    ALTER COLUMN plan_tier SET NOT NULL,
    ALTER COLUMN plan_tier SET DEFAULT 'ascend';

CREATE INDEX IF NOT EXISTS idx_users_referral_code ON users(referral_code);
CREATE INDEX IF NOT EXISTS idx_subscriptions_org_id_created_at ON subscriptions(org_id, created_at DESC);
