-- ============================================================================
-- RAPTORFLOW AUTH OVERHAUL: SCHEMA CONSOLIDATION & UCID
-- Migration: 20260119_auth_overhaul_consolidation.sql
-- ============================================================================

-- 1. CLEANUP OLD TRIGGERS & FUNCTIONS
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP TRIGGER IF EXISTS handle_new_user_workspace ON public.profiles;
DROP FUNCTION IF EXISTS public.handle_new_user();
DROP FUNCTION IF EXISTS public.handle_new_user_workspace();

-- 2. CREATE UCID SEQUENCE
CREATE SEQUENCE IF NOT EXISTS ucid_seq START 1;

-- 3. CREATE UCID GENERATION FUNCTION
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

-- 4. ENSURE UNIFIED PROFILES TABLE
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    ucid TEXT UNIQUE DEFAULT public.generate_ucid(),
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    onboarding_status TEXT DEFAULT 'pending' CHECK (onboarding_status IN ('pending', 'in_progress', 'active')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. ENSURE UNIFIED WORKSPACES TABLE
CREATE TABLE IF NOT EXISTS public.workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL DEFAULT 'Personal Workspace',
    slug TEXT UNIQUE NOT NULL,
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. NEW USER HANDLER (Google OAuth Only capture)
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    new_ucid TEXT;
BEGIN
    -- Generate UCID
    new_ucid := public.generate_ucid();

    -- Insert into profiles
    INSERT INTO public.profiles (id, email, full_name, avatar_url, ucid, onboarding_status)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', ''),
        COALESCE(NEW.raw_user_meta_data->>'avatar_url', NEW.raw_user_meta_data->>'picture', ''),
        new_ucid,
        'pending'
    )
    ON CONFLICT (id) DO UPDATE SET
        email = EXCLUDED.email,
        full_name = EXCLUDED.full_name,
        avatar_url = EXCLUDED.avatar_url,
        updated_at = NOW();

    -- Insert into workspaces (Personal Workspace)
    INSERT INTO public.workspaces (owner_id, name, slug)
    VALUES (
        NEW.id,
        'My Personal Workspace',
        'personal-' || lower(replace(COALESCE(NEW.raw_user_meta_data->>'full_name', 'user'), ' ', '-')) || '-' || floor(random() * 10000)::text
    )
    ON CONFLICT DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 7. RECREATE AUTH TRIGGER
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 8. RLS POLICIES
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "profiles_self_view" ON public.profiles;
DROP POLICY IF EXISTS "profiles_self_update" ON public.profiles;
CREATE POLICY "profiles_self_view" ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "profiles_self_update" ON public.profiles FOR UPDATE USING (auth.uid() = id);

DROP POLICY IF EXISTS "workspaces_owner_all" ON public.workspaces;
CREATE POLICY "workspaces_owner_all" ON public.workspaces FOR ALL USING (auth.uid() = owner_id);

-- 9. BACKFILL EXISTING USERS
-- Ensure all existing auth users have profiles and workspaces
INSERT INTO public.profiles (id, email, full_name, avatar_url)
SELECT
  id,
  email,
  COALESCE(raw_user_meta_data->>'full_name', raw_user_meta_data->>'name', ''),
  COALESCE(raw_user_meta_data->>'avatar_url', raw_user_meta_data->>'picture', '')
FROM auth.users
WHERE id NOT IN (SELECT id FROM public.profiles)
ON CONFLICT (id) DO NOTHING;

-- Backfill workspaces for profiles without one
INSERT INTO public.workspaces (owner_id, name, slug)
SELECT
    id,
    'My Personal Workspace',
    'personal-' || id::text
FROM public.profiles
WHERE id NOT IN (SELECT owner_id FROM public.workspaces)
ON CONFLICT DO NOTHING;
