-- ============================================================================
-- RAPTORFLOW AUTH & DATABASE OVERHAUL: FINAL CONSOLIDATION
-- Migration: 20260121_final_auth_database_consolidation.sql
-- ============================================================================

-- 1. CLEANUP OLD TRIGGERS & FUNCTIONS
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();

-- 2. UCID SYSTEM
CREATE SEQUENCE IF NOT EXISTS ucid_seq START 1;

CREATE OR REPLACE FUNCTION public.generate_ucid()
RETURNS TEXT AS $$
DECLARE
    year_prefix TEXT;
    seq_val TEXT;
BEGIN
    year_prefix := to_char(CURRENT_DATE, 'YYYY');
    seq_val := lpad(nextval('ucid_seq')::TEXT, 4, '0');
    RETURN 'RF-' || year_prefix || '-' || seq_val;
END;
$$ LANGUAGE plpgsql;

-- 3. PROFILES TABLE (Source of Truth for Identity)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    ucid TEXT UNIQUE DEFAULT public.generate_ucid(),
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    onboarding_status TEXT DEFAULT 'pending' CHECK (onboarding_status IN ('pending', 'in_progress', 'active')),
    subscription_plan TEXT DEFAULT 'free' CHECK (subscription_plan IN ('free', 'ascent', 'glide', 'soar')),
    subscription_status TEXT DEFAULT 'none' CHECK (subscription_status IN ('none', 'active', 'past_due', 'cancelled', 'expired')),
    workspace_preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. SUBSCRIPTIONS TABLE
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    plan_id TEXT NOT NULL CHECK (plan_id IN ('ascent', 'glide', 'soar')),
    status TEXT NOT NULL CHECK (status IN ('active', 'past_due', 'cancelled', 'expired')),
    current_period_start TIMESTAMPTZ NOT NULL,
    current_period_end TIMESTAMPTZ NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    phonepe_subscription_id TEXT, -- For future recurring payments
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. PAYMENTS TABLE
CREATE TABLE IF NOT EXISTS public.payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    transaction_id TEXT UNIQUE NOT NULL, -- PhonePe Merchant Transaction ID
    phonepe_transaction_id TEXT, -- PhonePe Gateway Transaction ID
    amount INTEGER NOT NULL, -- In Paise
    currency TEXT DEFAULT 'INR',
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    plan_id TEXT CHECK (plan_id IN ('ascent', 'glide', 'soar')),
    invoice_url TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    verified_at TIMESTAMPTZ
);

-- 6. EMAIL LOGS TABLE
CREATE TABLE IF NOT EXISTS public.email_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    email_type TEXT NOT NULL, -- 'welcome', 'verification', 'password_reset', 'invoice'
    recipient_email TEXT NOT NULL,
    resend_id TEXT, -- ID from Resend API
    status TEXT DEFAULT 'sent',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. WORKSPACES (Minimalist Personal Workspace)
CREATE TABLE IF NOT EXISTS public.workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL DEFAULT 'Personal Workspace',
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. DATA MIGRATION (Move from 'users' table if exists)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users' AND table_schema = 'public') THEN
        INSERT INTO public.profiles (id, email, full_name, avatar_url, role, onboarding_status, created_at, updated_at)
        SELECT id, email, full_name, avatar_url, role, onboarding_status, created_at, updated_at
        FROM public.users
        ON CONFLICT (id) DO UPDATE SET
            email = EXCLUDED.email,
            full_name = EXCLUDED.full_name,
            onboarding_status = EXCLUDED.onboarding_status,
            updated_at = NOW();
        
        -- Optional: DROP TABLE public.users; -- Keep it for safety for now
    END IF;
END $$;

-- 9. NEW USER HANDLER
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', ''),
        COALESCE(NEW.raw_user_meta_data->>'avatar_url', NEW.raw_user_meta_data->>'picture', '')
    )
    ON CONFLICT (id) DO UPDATE SET
        email = EXCLUDED.email,
        full_name = EXCLUDED.full_name,
        avatar_url = EXCLUDED.avatar_url,
        updated_at = NOW();

    -- Create default personal workspace
    INSERT INTO public.workspaces (owner_id, name)
    VALUES (NEW.id, 'My Personal Workspace')
    ON CONFLICT DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 10. RECREATE AUTH TRIGGER
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 11. RLS POLICIES (Hardened)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.email_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;

-- Profiles
DROP POLICY IF EXISTS "profiles_self_view" ON public.profiles;
DROP POLICY IF EXISTS "profiles_self_update" ON public.profiles;
CREATE POLICY "profiles_self_view" ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "profiles_self_update" ON public.profiles FOR UPDATE USING (auth.uid() = id);

-- Subscriptions
DROP POLICY IF EXISTS "subscriptions_self_view" ON public.subscriptions;
CREATE POLICY "subscriptions_self_view" ON public.subscriptions FOR SELECT USING (auth.uid() = user_id);

-- Payments
DROP POLICY IF EXISTS "payments_self_view" ON public.payments;
CREATE POLICY "payments_self_view" ON public.payments FOR SELECT USING (auth.uid() = user_id);

-- Email Logs
DROP POLICY IF EXISTS "email_logs_self_view" ON public.email_logs;
CREATE POLICY "email_logs_self_view" ON public.email_logs FOR SELECT USING (auth.uid() = user_id);

-- Workspaces
DROP POLICY IF EXISTS "workspaces_owner_all" ON public.workspaces;
CREATE POLICY "workspaces_owner_all" ON public.workspaces FOR ALL USING (auth.uid() = owner_id);

-- 12. INDEXES
CREATE INDEX IF NOT EXISTS idx_profiles_ucid ON public.profiles(ucid);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON public.payments(user_id);
CREATE INDEX IF NOT EXISTS idx_email_logs_user_id ON public.email_logs(user_id);
