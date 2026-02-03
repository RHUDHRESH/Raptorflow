-- ============================================================================
-- RAPTORFLOW AUTH SYSTEM FIX - RUN THIS IN SUPABASE SQL EDITOR
-- ============================================================================
-- Copy everything below this line and paste into:
-- https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc/sql/new
-- Then click "Run"
-- ============================================================================

-- 1. ENABLE UUID EXTENSION
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. CREATE UCID GENERATOR
DROP SEQUENCE IF EXISTS ucid_seq;
CREATE SEQUENCE ucid_seq START 1;

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

-- 3. PROFILES TABLE (User identity in public schema)
DROP TABLE IF EXISTS public.profiles CASCADE;
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    ucid TEXT UNIQUE DEFAULT public.generate_ucid(),
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    onboarding_status TEXT DEFAULT 'pending' CHECK (onboarding_status IN ('pending', 'in_progress', 'completed')),
    subscription_plan TEXT DEFAULT 'free' CHECK (subscription_plan IN ('free', 'ascent', 'glide', 'soar')),
    subscription_status TEXT DEFAULT 'none' CHECK (subscription_status IN ('none', 'active', 'past_due', 'cancelled', 'expired')),
    workspace_preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. WORKSPACES TABLE
DROP TABLE IF EXISTS public.workspaces CASCADE;
CREATE TABLE public.workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL DEFAULT 'Personal Workspace',
    slug TEXT UNIQUE,
    description TEXT,
    settings JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. WORKSPACE MEMBERS TABLE
DROP TABLE IF EXISTS public.workspace_members CASCADE;
CREATE TABLE public.workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
    is_active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

-- 6. USER SESSIONS TABLE
DROP TABLE IF EXISTS public.user_sessions CASCADE;
CREATE TABLE public.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    token TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. INDEXES
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_ucid ON public.profiles(ucid);
CREATE INDEX IF NOT EXISTS idx_workspaces_owner_id ON public.workspaces(owner_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON public.workspaces(slug);
CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace_id ON public.workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_user_id ON public.workspace_members(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON public.user_sessions(token);

-- 8. ENABLE RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

-- 9. RLS POLICIES FOR PROFILES
DROP POLICY IF EXISTS "profiles_select_own" ON public.profiles;
DROP POLICY IF EXISTS "profiles_update_own" ON public.profiles;

CREATE POLICY "profiles_select_own" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "profiles_update_own" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- Allow insert via trigger function
CREATE POLICY "profiles_insert_trigger" ON public.profiles
    FOR INSERT WITH CHECK (true);

-- 10. RLS POLICIES FOR WORKSPACES
DROP POLICY IF EXISTS "workspaces_owner_all" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_member_view" ON public.workspaces;

CREATE POLICY "workspaces_owner_all" ON public.workspaces
    FOR ALL USING (auth.uid() = owner_id);

CREATE POLICY "workspaces_member_view" ON public.workspaces
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM public.workspace_members
            WHERE workspace_id = workspaces.id AND is_active = true
        )
    );

-- 11. RLS POLICIES FOR WORKSPACE MEMBERS
DROP POLICY IF EXISTS "workspace_members_select" ON public.workspace_members;
DROP POLICY IF EXISTS "workspace_members_owner_manage" ON public.workspace_members;

CREATE POLICY "workspace_members_select" ON public.workspace_members
    FOR SELECT USING (
        auth.uid() = user_id OR
        auth.uid() IN (
            SELECT owner_id FROM public.workspaces
            WHERE id = workspace_members.workspace_id
        )
    );

CREATE POLICY "workspace_members_owner_manage" ON public.workspace_members
    FOR ALL USING (
        auth.uid() IN (
            SELECT owner_id FROM public.workspaces
            WHERE id = workspace_members.workspace_id
        )
    );

-- 12. RLS POLICIES FOR USER SESSIONS
DROP POLICY IF EXISTS "user_sessions_own" ON public.user_sessions;
CREATE POLICY "user_sessions_own" ON public.user_sessions
    FOR ALL USING (auth.uid() = user_id);

-- 13. UPDATED_AT TRIGGER FUNCTION
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 14. ATTACH TRIGGERS
DROP TRIGGER IF EXISTS update_profiles_updated_at ON public.profiles;
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_workspaces_updated_at ON public.workspaces;
CREATE TRIGGER update_workspaces_updated_at
    BEFORE UPDATE ON public.workspaces
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_workspace_members_updated_at ON public.workspace_members;
CREATE TRIGGER update_workspace_members_updated_at
    BEFORE UPDATE ON public.workspace_members
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 15. HANDLE NEW USER FUNCTION
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    new_workspace_id UUID;
BEGIN
    -- Create profile
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

    -- Create default workspace
    INSERT INTO public.workspaces (owner_id, name, slug)
    VALUES (NEW.id, 'My Personal Workspace', 'personal-' || substr(NEW.id::text, 1, 8))
    RETURNING id INTO new_workspace_id;

    -- Add owner as member
    INSERT INTO public.workspace_members (workspace_id, user_id, role)
    VALUES (new_workspace_id, NEW.id, 'owner');

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 16. ATTACH AUTH TRIGGER
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- VERIFICATION QUERY - Run this after to confirm everything worked:
-- SELECT * FROM information_schema.tables
-- WHERE table_schema = 'public'
-- AND table_name IN ('profiles', 'workspaces', 'workspace_members');
-- ============================================================================
