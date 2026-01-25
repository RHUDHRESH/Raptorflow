-- ============================================================================
-- RaptorFlow CIN (Customer Identification Number) & Enhanced Auth Schema
-- Migration: 20260113_cin_and_enhanced_auth.sql
-- 
-- This migration adds:
-- 1. CIN (Customer Identification Number) - unique immutable customer ID
-- 2. Enhanced user profile fields
-- 3. Updated auth hook to generate CIN on signup
-- 4. Proper payment-user linkage
-- ============================================================================

-- 1. Add CIN column to users table if not exists
DO $$ 
BEGIN
    -- Add CIN column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'cin') THEN
        ALTER TABLE users ADD COLUMN cin TEXT UNIQUE;
    END IF;
    
    -- Add subscription fields if not exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'subscription_plan') THEN
        ALTER TABLE users ADD COLUMN subscription_plan TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'subscription_status') THEN
        ALTER TABLE users ADD COLUMN subscription_status TEXT DEFAULT 'none';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'subscription_expires_at') THEN
        ALTER TABLE users ADD COLUMN subscription_expires_at TIMESTAMPTZ;
    END IF;
    
    -- Add storage allocation field
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'storage_bytes_used') THEN
        ALTER TABLE users ADD COLUMN storage_bytes_used BIGINT DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'storage_bytes_limit') THEN
        ALTER TABLE users ADD COLUMN storage_bytes_limit BIGINT DEFAULT 1073741824; -- 1GB default
    END IF;
END $$;

-- 2. Create function to generate CIN
-- Format: RF-YYYYMMDD-XXXXX (e.g., RF-20260113-A7B2C)
CREATE OR REPLACE FUNCTION generate_cin()
RETURNS TEXT AS $$
DECLARE
    date_part TEXT;
    random_part TEXT;
    new_cin TEXT;
    attempt INT := 0;
BEGIN
    LOOP
        date_part := to_char(NOW(), 'YYYYMMDD');
        random_part := upper(substr(md5(random()::text || clock_timestamp()::text), 1, 5));
        new_cin := 'RF-' || date_part || '-' || random_part;
        
        -- Check if this CIN already exists
        IF NOT EXISTS (SELECT 1 FROM users WHERE cin = new_cin) THEN
            RETURN new_cin;
        END IF;
        
        attempt := attempt + 1;
        IF attempt > 100 THEN
            RAISE EXCEPTION 'Failed to generate unique CIN after 100 attempts';
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Update the handle_new_user function to generate CIN
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    new_cin TEXT;
BEGIN
    -- Generate unique CIN
    new_cin := generate_cin();
    
    INSERT INTO public.users (
        auth_user_id, 
        email, 
        full_name, 
        avatar_url,
        cin,
        onboarding_status,
        created_at
    )
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name'),
        NEW.raw_user_meta_data->>'avatar_url',
        new_cin,
        'pending_workspace',
        NOW()
    )
    ON CONFLICT (auth_user_id) DO UPDATE SET
        email = EXCLUDED.email,
        full_name = COALESCE(EXCLUDED.full_name, users.full_name),
        avatar_url = COALESCE(EXCLUDED.avatar_url, users.avatar_url),
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4. Re-attach trigger (idempotent)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 5. Backfill existing users without CIN
UPDATE users 
SET cin = generate_cin() 
WHERE cin IS NULL;

-- 6. Make CIN NOT NULL after backfill
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'users' AND column_name = 'cin' AND is_nullable = 'YES') THEN
        ALTER TABLE users ALTER COLUMN cin SET NOT NULL;
    END IF;
END $$;

-- 7. Create index on CIN for fast lookups
CREATE INDEX IF NOT EXISTS idx_users_cin ON users(cin);
CREATE INDEX IF NOT EXISTS idx_users_subscription_status ON users(subscription_status);

-- 8. Update payments table to use proper foreign key
DO $$
BEGIN
    -- Add user_cin column to payments if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'payments' AND column_name = 'user_cin') THEN
        ALTER TABLE payments ADD COLUMN user_cin TEXT REFERENCES users(cin);
    END IF;
END $$;

-- 9. Create function to update user subscription after successful payment
CREATE OR REPLACE FUNCTION update_user_subscription_on_payment()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        UPDATE users 
        SET 
            subscription_status = 'active',
            subscription_plan = NEW.metadata->>'plan_name',
            subscription_expires_at = NOW() + INTERVAL '1 month',
            onboarding_status = 'active',
            updated_at = NOW()
        WHERE id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 10. Create trigger for payment completion
DROP TRIGGER IF EXISTS on_payment_completed ON payments;
CREATE TRIGGER on_payment_completed
    AFTER UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_user_subscription_on_payment();

-- 11. Create view for customer records with CIN
CREATE OR REPLACE VIEW customer_records AS
SELECT 
    u.cin AS customer_id,
    u.email,
    u.full_name,
    u.phone,
    u.subscription_plan,
    u.subscription_status,
    u.subscription_expires_at,
    u.onboarding_status,
    u.storage_bytes_used,
    u.storage_bytes_limit,
    u.created_at AS customer_since,
    u.last_login_at,
    u.is_active,
    w.name AS workspace_name,
    w.id AS workspace_id,
    (SELECT COUNT(*) FROM payments p WHERE p.user_id = u.id AND p.status = 'completed') AS total_payments,
    (SELECT COALESCE(SUM(p.amount_paise), 0) FROM payments p WHERE p.user_id = u.id AND p.status = 'completed') AS total_revenue_paise
FROM users u
LEFT JOIN workspaces w ON w.owner_id = u.id;

-- Grant access to the view
GRANT SELECT ON customer_records TO authenticated;

-- 12. Add RLS policy for customer_records view
-- (Views inherit RLS from underlying tables)

COMMENT ON COLUMN users.cin IS 'Customer Identification Number - immutable unique identifier for the customer (format: RF-YYYYMMDD-XXXXX)';
COMMENT ON VIEW customer_records IS 'Consolidated customer view with CIN, subscription, and revenue data';
