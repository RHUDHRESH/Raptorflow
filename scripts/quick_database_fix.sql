-- Quick Database Fix Script
-- Run this in Supabase SQL Editor to fix missing tables

-- Create missing profiles table
DROP TABLE IF EXISTS public.profiles CASCADE;
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'super_admin')),
    workspace_id UUID,
    subscription_plan TEXT DEFAULT 'free' CHECK (subscription_plan IN ('free', 'ascent', 'glide', 'soar')),
    subscription_status TEXT DEFAULT 'none' CHECK (subscription_status IN ('none', 'trial', 'active', 'cancelled', 'expired', 'suspended')),
    onboarding_status TEXT DEFAULT 'pending' CHECK (onboarding_status IN ('pending', 'in_progress', 'active', 'skipped')),
    is_active BOOLEAN DEFAULT true,
    is_banned BOOLEAN DEFAULT false,
    ban_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create BCM manifest table
DROP TABLE IF EXISTS public.business_context_manifests CASCADE;
CREATE TABLE public.business_context_manifests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    manifest JSONB NOT NULL,
    checksum TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workspace_id, version)
);

-- Create foundations table
DROP TABLE IF EXISTS public.foundations CASCADE;
CREATE TABLE public.foundations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    company_info JSONB,
    mission TEXT,
    vision TEXT,
    value_proposition TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create ICP profiles table
DROP TABLE IF EXISTS public.icp_profiles CASCADE;
CREATE TABLE public.icp_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    demographics JSONB,
    psychographics JSONB,
    pain_points JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_workspace ON public.profiles(workspace_id);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON public.profiles(role);
CREATE INDEX IF NOT EXISTS idx_bcm_workspace ON public.business_context_manifests(workspace_id);
CREATE INDEX IF NOT EXISTS idx_bcm_version ON public.business_context_manifests(workspace_id, version);
CREATE INDEX IF NOT EXISTS idx_foundations_workspace ON public.foundations(workspace_id);
CREATE INDEX IF NOT EXISTS idx_icp_workspace ON public.icp_profiles(workspace_id);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.business_context_manifests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.foundations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.icp_profiles ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
DROP POLICY IF EXISTS "profiles_select_own" ON public.profiles;
CREATE POLICY "profiles_select_own" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "profiles_update_own" ON public.profiles;
CREATE POLICY "profiles_update_own" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

DROP POLICY IF EXISTS "bcm_select_workspace" ON public.business_context_manifests;
CREATE POLICY "bcm_select_workspace" ON public.business_context_manifests
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM public.workspaces 
            WHERE owner_id = auth.uid()
        )
    );

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE TRIGGER profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER foundations_updated_at
    BEFORE UPDATE ON public.foundations
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER icp_profiles_updated_at
    BEFORE UPDATE ON public.icp_profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- Create user profile trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Verify setup
SELECT 'Database fix completed successfully' as status,
       (SELECT COUNT(*) FROM public.profiles) as profiles_count,
       (SELECT COUNT(*) FROM public.workspaces) as workspaces_count,
       (SELECT COUNT(*) FROM public.business_context_manifests) as bcm_count;
