-- ============================================================================
-- RAPTORFLOW AUTH & TENANT RECOVERY
-- Migration: 20260120_auth_tenant_recovery.sql
-- Fixes: Workspace isolation, missing memberships, and profiles schema
-- ============================================================================

-- 1. ADD MISSING COLUMNS TO PROFILES
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'workspace_id') THEN
        ALTER TABLE public.profiles ADD COLUMN workspace_id UUID REFERENCES public.workspaces(id);
    END IF;
END $$;

-- 2. ENSURE WORKSPACE MEMBERSHIP FOR ALL OWNERS
-- This ensures that every user who owns a workspace is actually a member of it (fixing RLS bypass)
-- We check both owner_id and user_id to cover different schema versions
INSERT INTO public.workspace_members (user_id, workspace_id, role)
SELECT owner_id, id, 'owner'
FROM public.workspaces
WHERE owner_id IS NOT NULL
ON CONFLICT (user_id, workspace_id) DO NOTHING;

INSERT INTO public.workspace_members (user_id, workspace_id, role)
SELECT user_id, id, 'owner'
FROM public.workspaces
WHERE user_id IS NOT NULL
ON CONFLICT (user_id, workspace_id) DO NOTHING;

-- 3. SYNC WORKSPACE_ID BACK TO PROFILES
-- Some RLS policies depend on profiles.workspace_id
UPDATE public.profiles p
SET workspace_id = w.id
FROM public.workspaces w
WHERE (w.owner_id = p.id OR w.user_id = p.id) AND p.workspace_id IS NULL;

-- 4. IMPROVED NEW USER HANDLER
-- This handler ensures a profile, a workspace, AND a membership record are created atomically
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    new_ucid TEXT;
    new_workspace_id UUID;
    new_full_name TEXT;
    new_slug TEXT;
BEGIN
    -- 1. Generate unique identifiers
    new_ucid := public.generate_ucid();
    new_workspace_id := gen_random_uuid();
    new_full_name := COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', 'User');
    new_slug := 'personal-' || lower(replace(new_full_name, ' ', '-')) || '-' || floor(random() * 10000)::text;

    -- 2. Create Profile
    INSERT INTO public.profiles (id, email, full_name, avatar_url, ucid, onboarding_status, workspace_id)
    VALUES (
        NEW.id,
        NEW.email,
        new_full_name,
        COALESCE(NEW.raw_user_meta_data->>'avatar_url', NEW.raw_user_meta_data->>'picture', ''),
        new_ucid,
        'pending',
        new_workspace_id
    )
    ON CONFLICT (id) DO UPDATE SET
        email = EXCLUDED.email,
        full_name = EXCLUDED.full_name,
        avatar_url = EXCLUDED.avatar_url,
        -- Don't overwrite active status if already set
        onboarding_status = COALESCE(NULLIF(public.profiles.onboarding_status, 'pending'), EXCLUDED.onboarding_status),
        workspace_id = COALESCE(public.profiles.workspace_id, EXCLUDED.workspace_id),
        updated_at = NOW();

    -- 3. Create Workspace
    INSERT INTO public.workspaces (id, owner_id, name, slug)
    VALUES (
        new_workspace_id,
        NEW.id,
        new_full_name || '''s Personal Workspace',
        new_slug
    )
    ON CONFLICT DO NOTHING;

    -- 4. Create Workspace Membership (CRITICAL for RLS)
    INSERT INTO public.workspace_members (user_id, workspace_id, role)
    VALUES (
        NEW.id,
        new_workspace_id,
        'owner'
    )
    ON CONFLICT DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. RE-ATTACH TRIGGER
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 6. GRANT NECESSARY PERMISSIONS
GRANT SELECT ON public.workspace_members TO authenticated;
GRANT SELECT ON public.workspaces TO authenticated;
GRANT SELECT ON public.profiles TO authenticated;
