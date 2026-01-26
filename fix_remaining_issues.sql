-- ============================================================================
-- FIX REMAINING SCHEMA ISSUES
-- Execute this in Supabase Dashboard > SQL Editor
-- ============================================================================

-- First, let's check what tables actually exist
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name IN ('profiles', 'workspaces', 'subscriptions', 'payments', 'email_logs')
ORDER BY table_name, ordinal_position;

-- Fix profiles table - remove workspace_id if it exists
ALTER TABLE public.profiles DROP COLUMN IF EXISTS workspace_id;

-- Ensure workspaces table has correct structure
DO $$
BEGIN
    -- Check if workspaces table exists and has the right columns
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'workspaces' AND table_schema = 'public') THEN
        -- Add missing columns if they don't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'workspaces' AND column_name = 'id' AND table_schema = 'public') THEN
            ALTER TABLE public.workspaces ADD COLUMN IF NOT EXISTS id UUID PRIMARY KEY DEFAULT gen_random_uuid();
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'workspaces' AND column_name = 'owner_id' AND table_schema = 'public') THEN
            ALTER TABLE public.workspaces ADD COLUMN IF NOT EXISTS owner_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'workspaces' AND column_name = 'name' AND table_schema = 'public') THEN
            ALTER TABLE public.workspaces ADD COLUMN IF NOT EXISTS name TEXT NOT NULL DEFAULT 'Personal Workspace';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'workspaces' AND column_name = 'settings' AND table_schema = 'public') THEN
            ALTER TABLE public.workspaces ADD COLUMN IF NOT EXISTS settings JSONB DEFAULT '{}'::jsonb;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'workspaces' AND column_name = 'created_at' AND table_schema = 'public') THEN
            ALTER TABLE public.workspaces ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'workspaces' AND column_name = 'updated_at' AND table_schema = 'public') THEN
            ALTER TABLE public.workspaces ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
        END IF;
    ELSE
        -- Create workspaces table if it doesn't exist
        CREATE TABLE public.workspaces (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            owner_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
            name TEXT NOT NULL DEFAULT 'Personal Workspace',
            settings JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
    END IF;
END $$;

-- Create payments table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    transaction_id TEXT UNIQUE NOT NULL,
    phonepe_transaction_id TEXT,
    amount INTEGER NOT NULL,
    currency TEXT DEFAULT 'INR',
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    plan_id TEXT CHECK (plan_id IN ('ascent', 'glide', 'soar')),
    invoice_url TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    verified_at TIMESTAMPTZ
);

-- Create email_logs table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.email_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    email_type TEXT NOT NULL,
    recipient_email TEXT NOT NULL,
    resend_id TEXT,
    status TEXT DEFAULT 'sent',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.email_logs ENABLE ROW LEVEL SECURITY;

-- Drop and recreate policies for clean state
DROP POLICY IF EXISTS "profiles_self_view" ON public.profiles;
DROP POLICY IF EXISTS "profiles_self_update" ON public.profiles;
DROP POLICY IF EXISTS "workspaces_owner_all" ON public.workspaces;
DROP POLICY IF EXISTS "subscriptions_self_view" ON public.subscriptions;
DROP POLICY IF EXISTS "payments_self_view" ON public.payments;
DROP POLICY IF EXISTS "email_logs_self_view" ON public.email_logs;

-- Create proper RLS policies
CREATE POLICY "profiles_self_view" ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "profiles_self_update" ON public.profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "workspaces_owner_all" ON public.workspaces FOR ALL USING (auth.uid() = owner_id);
CREATE POLICY "subscriptions_self_view" ON public.subscriptions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "payments_self_view" ON public.payments FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "email_logs_self_view" ON public.email_logs FOR SELECT USING (auth.uid() = user_id);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_profiles_ucid ON public.profiles(ucid);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON public.payments(user_id);
CREATE INDEX IF NOT EXISTS idx_email_logs_user_id ON public.email_logs(user_id);

-- Final verification
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('profiles', 'workspaces', 'subscriptions', 'payments', 'email_logs')
ORDER BY table_name;
