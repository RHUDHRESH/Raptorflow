-- Migration: 006_plan_expiry.sql
-- Description: Adds plan expiry tracking for 30-day plans (no proration)

-- Add plan_expires_at column to profiles if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'plan_expires_at') THEN
        ALTER TABLE public.profiles ADD COLUMN plan_expires_at TIMESTAMPTZ;
    END IF;
END $$;

-- Add plan_started_at column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'plan_started_at') THEN
        ALTER TABLE public.profiles ADD COLUMN plan_started_at TIMESTAMPTZ;
    END IF;
END $$;

-- Add last_payment_id column if it doesn't exist  
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'last_payment_id') THEN
        ALTER TABLE public.profiles ADD COLUMN last_payment_id UUID;
    END IF;
END $$;

-- Add last_payment_amount column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'last_payment_amount') THEN
        ALTER TABLE public.profiles ADD COLUMN last_payment_amount INTEGER;
    END IF;
END $$;

-- Add last_payment_date column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'last_payment_date') THEN
        ALTER TABLE public.profiles ADD COLUMN last_payment_date TIMESTAMPTZ;
    END IF;
END $$;

-- Create index for plan expiry queries
CREATE INDEX IF NOT EXISTS idx_profiles_plan_expires_at ON public.profiles(plan_expires_at);
CREATE INDEX IF NOT EXISTS idx_profiles_plan_status ON public.profiles(plan_status);

-- Function to check and expire plans (can be called by a cron job)
CREATE OR REPLACE FUNCTION check_expired_plans()
RETURNS void AS $$
BEGIN
    UPDATE public.profiles
    SET 
        plan_status = 'expired',
        updated_at = NOW()
    WHERE 
        plan_status = 'active'
        AND plan_expires_at IS NOT NULL
        AND plan_expires_at < NOW();
        
    -- Log how many plans were expired
    RAISE NOTICE 'Expired % plans', (SELECT COUNT(*) FROM public.profiles WHERE plan_status = 'expired' AND plan_expires_at < NOW() + INTERVAL '1 minute');
END;
$$ LANGUAGE plpgsql;

-- Comment for documentation
COMMENT ON COLUMN public.profiles.plan_expires_at IS 'When the current plan expires. All plans are 30 days, no proration allowed.';

-- Success message
DO $$ 
BEGIN
    RAISE NOTICE 'Plan expiry migration completed successfully!';
END $$;

