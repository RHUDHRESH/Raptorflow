-- CRITICAL FIX: Foreign Key Reference Inconsistencies
-- Problem: subscriptions, payment_transactions reference users(id)
-- But code uses profiles.id (which = auth.uid())
-- users.id is a different auto-generated UUID, users.auth_user_id = auth.uid()

-- This causes foreign key violations when inserting subscriptions

-- ============================================================================
-- OPTION 1: Change FKs to reference profiles(id) since profiles.id = auth.uid()
-- This is cleaner since we authenticate via auth.uid()
-- ============================================================================

-- 1. Fix subscriptions table
ALTER TABLE public.subscriptions DROP CONSTRAINT IF EXISTS subscriptions_user_id_fkey;
ALTER TABLE public.subscriptions
    ADD CONSTRAINT subscriptions_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE;

-- 2. Fix payment_transactions table
ALTER TABLE public.payment_transactions DROP CONSTRAINT IF EXISTS payment_transactions_user_id_fkey;
ALTER TABLE public.payment_transactions
    ADD CONSTRAINT payment_transactions_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE;

-- 3. Fix audit_logs table
ALTER TABLE public.audit_logs DROP CONSTRAINT IF EXISTS audit_logs_actor_id_fkey;
ALTER TABLE public.audit_logs
    ADD CONSTRAINT audit_logs_actor_id_fkey
    FOREIGN KEY (actor_id) REFERENCES public.profiles(id) ON DELETE SET NULL;

-- 4. Fix admin_actions table
ALTER TABLE public.admin_actions DROP CONSTRAINT IF EXISTS admin_actions_admin_id_fkey;
ALTER TABLE public.admin_actions DROP CONSTRAINT IF EXISTS admin_actions_target_user_id_fkey;
ALTER TABLE public.admin_actions
    ADD CONSTRAINT admin_actions_admin_id_fkey
    FOREIGN KEY (admin_id) REFERENCES public.profiles(id) ON DELETE CASCADE;
ALTER TABLE public.admin_actions
    ADD CONSTRAINT admin_actions_target_user_id_fkey
    FOREIGN KEY (target_user_id) REFERENCES public.profiles(id) ON DELETE SET NULL;

-- 5. Fix security_events table
ALTER TABLE public.security_events DROP CONSTRAINT IF EXISTS security_events_user_id_fkey;
ALTER TABLE public.security_events
    ADD CONSTRAINT security_events_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE SET NULL;

-- 6. Fix user_sessions table
ALTER TABLE public.user_sessions DROP CONSTRAINT IF EXISTS user_sessions_user_id_fkey;
ALTER TABLE public.user_sessions
    ADD CONSTRAINT user_sessions_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE;

-- 7. Fix workspaces table - use owner_id consistently
ALTER TABLE public.workspaces DROP CONSTRAINT IF EXISTS workspaces_user_id_fkey;
-- Keep owner_id FK to profiles, make user_id nullable or remove
ALTER TABLE public.workspaces ALTER COLUMN user_id DROP NOT NULL;

-- ============================================================================
-- ENSURE PROFILES HAS ALL NEEDED DATA
-- ============================================================================

-- Add missing columns to profiles if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'phone') THEN
        ALTER TABLE public.profiles ADD COLUMN phone text;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'ucid') THEN
        ALTER TABLE public.profiles ADD COLUMN ucid text UNIQUE;
    END IF;
END $$;

-- Create function to generate UCID if not exists
CREATE OR REPLACE FUNCTION generate_ucid()
RETURNS TRIGGER AS $$
DECLARE
    new_ucid text;
    prefix text := 'RF';
BEGIN
    IF NEW.ucid IS NULL THEN
        new_ucid := prefix || '-' || UPPER(SUBSTRING(MD5(NEW.id::text || NOW()::text) FROM 1 FOR 8));
        NEW.ucid := new_ucid;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for UCID generation
DROP TRIGGER IF EXISTS generate_ucid_trigger ON public.profiles;
CREATE TRIGGER generate_ucid_trigger
    BEFORE INSERT ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION generate_ucid();

-- Update existing profiles without UCID
UPDATE public.profiles
SET ucid = 'RF-' || UPPER(SUBSTRING(MD5(id::text || created_at::text) FROM 1 FOR 8))
WHERE ucid IS NULL;

-- ============================================================================
-- RLS POLICIES - Ensure service role can do everything
-- ============================================================================

-- Drop and recreate comprehensive policies
DROP POLICY IF EXISTS "profiles_service_all" ON public.profiles;
CREATE POLICY "profiles_service_all" ON public.profiles
    FOR ALL
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "subscriptions_service_all" ON public.subscriptions;
CREATE POLICY "subscriptions_service_all" ON public.subscriptions
    FOR ALL
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "plans_service_all" ON public.plans;
CREATE POLICY "plans_service_all" ON public.plans
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Grant full permissions to service_role
GRANT ALL ON public.profiles TO service_role;
GRANT ALL ON public.subscriptions TO service_role;
GRANT ALL ON public.plans TO service_role;
GRANT ALL ON public.payments TO service_role;
GRANT ALL ON public.payment_transactions TO service_role;
GRANT ALL ON public.audit_logs TO service_role;
GRANT ALL ON public.workspaces TO service_role;
GRANT ALL ON public.email_logs TO service_role;

-- ============================================================================
-- FIX HANDLE_NEW_USER TO CREATE PROPER PROFILE
-- ============================================================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    new_ucid text;
    new_workspace_id uuid;
BEGIN
    -- Generate UCID
    new_ucid := 'RF-' || UPPER(SUBSTRING(MD5(NEW.id::text || NOW()::text) FROM 1 FOR 8));

    -- Create profile (profiles.id = auth.users.id for direct lookup)
    INSERT INTO public.profiles (
        id,
        email,
        full_name,
        avatar_url,
        ucid,
        role,
        onboarding_status,
        subscription_status,
        is_active,
        is_banned
    )
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
        COALESCE(NEW.raw_user_meta_data->>'avatar_url', NEW.raw_user_meta_data->>'picture', ''),
        new_ucid,
        'user',
        'pending',
        'none',
        true,
        false
    )
    ON CONFLICT (id) DO UPDATE SET
        email = EXCLUDED.email,
        full_name = COALESCE(EXCLUDED.full_name, public.profiles.full_name),
        avatar_url = COALESCE(EXCLUDED.avatar_url, public.profiles.avatar_url),
        updated_at = NOW();

    -- Create default workspace
    INSERT INTO public.workspaces (owner_id, name, slug, status)
    VALUES (
        NEW.id,
        'My Workspace',
        'ws-' || LOWER(SUBSTRING(MD5(NEW.id::text) FROM 1 FOR 12)),
        'active'
    )
    ON CONFLICT DO NOTHING
    RETURNING id INTO new_workspace_id;

    -- Update profile with workspace_id if created
    IF new_workspace_id IS NOT NULL THEN
        UPDATE public.profiles SET workspace_id = new_workspace_id WHERE id = NEW.id;
    END IF;

    RETURN NEW;
EXCEPTION WHEN OTHERS THEN
    -- Log error but don't fail the auth signup
    RAISE WARNING 'handle_new_user error for %: %', NEW.id, SQLERRM;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Ensure trigger exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO service_role;
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO authenticated;

-- ============================================================================
-- SYNC EXISTING USERS TO PROFILES
-- ============================================================================

-- Create profiles for any auth.users that don't have one
INSERT INTO public.profiles (id, email, full_name, avatar_url, ucid, role, onboarding_status, subscription_status, is_active)
SELECT
    au.id,
    au.email,
    COALESCE(au.raw_user_meta_data->>'full_name', au.raw_user_meta_data->>'name', split_part(au.email, '@', 1)),
    COALESCE(au.raw_user_meta_data->>'avatar_url', au.raw_user_meta_data->>'picture', ''),
    'RF-' || UPPER(SUBSTRING(MD5(au.id::text || au.created_at::text) FROM 1 FOR 8)),
    'user',
    'pending',
    'none',
    true
FROM auth.users au
WHERE NOT EXISTS (SELECT 1 FROM public.profiles p WHERE p.id = au.id)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- ENSURE DEFAULT PLANS EXIST
-- ============================================================================

INSERT INTO public.plans (id, name, description, price_monthly_paise, price_yearly_paise, features, storage_limit_bytes, is_active, display_order, popular)
VALUES
    ('ascent', 'Ascent', 'For founders just getting started', 500000, 5000000, '{"projects": 3, "team_members": 1, "support": "email"}'::jsonb, 5368709120, true, 1, false),
    ('glide', 'Glide', 'For founders scaling their marketing', 700000, 7000000, '{"projects": 10, "team_members": 5, "support": "priority"}'::jsonb, 26843545600, true, 2, true),
    ('soar', 'Soar', 'For teams running multi-channel campaigns', 1000000, 10000000, '{"projects": -1, "team_members": -1, "support": "dedicated"}'::jsonb, 107374182400, true, 3, false)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    price_monthly_paise = EXCLUDED.price_monthly_paise,
    price_yearly_paise = EXCLUDED.price_yearly_paise,
    features = EXCLUDED.features,
    storage_limit_bytes = EXCLUDED.storage_limit_bytes,
    is_active = EXCLUDED.is_active,
    display_order = EXCLUDED.display_order,
    popular = EXCLUDED.popular;
